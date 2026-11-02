import pytest
from bs4 import BeautifulSoup
from main import (
    parse_book,
    get_page,
    scrape_books,
    has_next_page,
    parse_page,
    parse_book,
)
from unittest.mock import patch
from requests.exceptions import RequestException


@pytest.fixture
def make_book():
    def _make_book(rating="Four"):
        html = f"""
        <article class="product_pod">
            <h3>
                <a href="example.html" title="Test Book">Test Book</a>
            </h3>
            <p class="price_color">£51.77</p>
            <p class="star-rating {rating}"></p>
        </article>
        """

        soup = BeautifulSoup(html, "html.parser")
        return soup.select_one("article.product_pod")

    return _make_book


def test_parse_book(make_book):
    book = make_book()
    result = parse_book(book)

    assert result["title"] == "Test Book"
    assert result["price"] == 51.77
    assert result["rating"] == 4
    assert result["link"] == "https://books.toscrape.com/example.html"


def test_parse_book_without_price():
    html = """
    <article class="product_pod">
        <h3>
            <a href="example.html" title="Test Book">Test Book</a>
        </h3>
        <p class="star-rating Four"></p>
    </article>
    """
    soup = BeautifulSoup(html, "html.parser")
    book = soup.select_one("article.product_pod")

    result = parse_book(book)

    assert result is None


def test_parse_book_with_unknown_rating(make_book):
    book = make_book("Unknown")

    with pytest.raises(ValueError, match="Неизвестный рейтинг"):
        parse_book(book)


def test_parse_book_without_rating():
    html = f"""
            <article class="product_pod">
                <h3>
                    <a href="example.html" title="Test Book">Test Book</a>
                </h3>
                
            </article>
            """
    soup = BeautifulSoup(html, "html.parser")
    book = soup.select_one("article.product_pod")
    result = parse_book(book)
    assert result is None


def test_parse_book_with_invalid_price():
    html = """
        <article class="product_pod">
            <h3>
                <a href="example.html" title="Test Book">Test Book</a>
            </h3>
            <p class="price_color">неизвестно</p>
            <p class="star-rating Four"></p>
        </article>
        """
    soup = BeautifulSoup(html, "html.parser")
    book = soup.select_one("article.product_pod")
    with pytest.raises(ValueError):
        parse_book(book)


@pytest.mark.parametrize(
    "rating_text, expected",
    [
        ("One", 1),
        ("Two", 2),
        ("Three", 3),
        ("Four", 4),
        ("Five", 5),
    ],
)
def test_parse_book_rating(make_book, rating_text, expected):
    book = make_book(rating_text)
    result = parse_book(book)
    assert result["rating"] == expected


def test_get_page_fails_after_three_attempts():
    with patch("main.requests.get") as mock_get:
        mock_get.side_effect = RequestException("Сайт недоступен")

        result = get_page("https://example.com")

        assert result is None
        assert mock_get.call_count == 3


def test_get_page_success():
    with patch("main.requests.get") as mock_get:
        mock_get.return_value.text = "<html><body><h1>Test</h1></body></html>"
        mock_get.return_value.raise_for_status.return_value = None

        result = get_page("https://example.com")

        assert result is not None
        assert result.select_one("h1").text == "Test"
        mock_get.assert_called_once_with(
            "https://example.com",
            timeout=10,
        )


def test_scrape_books_two_pages():
    with (
        patch("main.get_page") as mock_get_page,
        patch("main.parse_page") as mock_parse_page,
        patch("main.has_next_page") as mock_has_next,
    ):
        mock_get_page.side_effect = ["page1", "page2"]
        mock_parse_page.side_effect = [
            [{"title": "Book 1"}],
            [{"title": "Book 2"}],
        ]
        mock_has_next.side_effect = [True, False]

        result = scrape_books(max_pages=2)

        assert result == [
            {"title": "Book 1"},
            {"title": "Book 2"},
        ]
        assert mock_get_page.call_count == 2
        assert mock_parse_page.call_count == 2


def test_scrape_books_stops_when_page_fails():
    with (
        patch("main.get_page") as mock_get_page,
        patch("main.parse_page") as mock_parse_page,
        patch("main.has_next_page") as mock_has_next,
    ):
        mock_get_page.side_effect = ["page1", None]
        mock_parse_page.return_value = [{"title": "Book 1"}]
        mock_has_next.return_value = True

        result = scrape_books(max_pages=3)

        assert result == [{"title": "Book 1"}]
        assert mock_get_page.call_count == 2
        assert mock_parse_page.call_count == 1
        mock_has_next.assert_called_once_with("page1")


def test_scrape_books_respects_max_pages():
    with (
        patch("main.get_page") as mock_get_page,
        patch("main.parse_page") as mock_parse_page,
        patch("main.has_next_page") as mock_has_next,
    ):
        mock_get_page.return_value = "page"
        mock_parse_page.return_value = [{"title": "Book"}]
        mock_has_next.return_value = True

        result = scrape_books(max_pages=2)

        assert len(result) == 2
        assert mock_get_page.call_count == 2
        assert mock_parse_page.call_count == 2
        assert mock_has_next.call_count == 2


def test_has_next_page_true():
    html = """
            <li class="next"><a href="catalogue/page-2.html">next</a></li>
            """
    soup = BeautifulSoup(html, "html.parser")
    assert has_next_page(soup) is True


def test_has_next_page_false():
    html = ""
    soup = BeautifulSoup(html, "html.parser")
    assert has_next_page(soup) is False


def test_parse_page_returns_empty_list_when_no_books():
    html = ""
    soup = BeautifulSoup(html, "html.parser")
    assert parse_page(soup) == []


def test_parse_page_returns_one_book(make_book):
    book = make_book()
    html = f"<div>{book}</div>"
    soup = BeautifulSoup(html, "html.parser")

    result = parse_page(soup)

    assert len(result) == 1
    assert result[0]["title"] == "Test Book"
    assert result[0]["price"] == 51.77
    assert result[0]["rating"] == 4
    assert result[0]["link"] == "https://books.toscrape.com/example.html"


def test_parse_page_returns_multiple_books(make_book):
    book1 = make_book("Two")
    book2 = make_book()
    html = f"<div>{book1}\n{book2}</div>"
    soup = BeautifulSoup(html, "html.parser")
    result = parse_page(soup)

    assert len(result) == 2
    assert result[0]["rating"] == 2
    assert result[1]["rating"] == 4


def test_scrape_books_collects_books_from_two_pages(make_book):
    book1 = make_book("Two")
    book2 = make_book("Four")
    page1 = BeautifulSoup(
        f"<div>{book1}<li class='next'><a href='page-2.html'>next</a></li></div>",
        "html.parser",
    )
    page2 = BeautifulSoup(f"<div>{book2}</div>", "html.parser")
    with patch("main.get_page", side_effect=[page1, page2]):
        result = scrape_books()
    assert len(result) == 2
    assert result[0]["rating"] == 2
    assert result[1]["rating"] == 4
