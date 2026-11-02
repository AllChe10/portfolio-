import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.exceptions import RequestException


def parse_book(book):
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    base_url = "https://books.toscrape.com/"
    try:
        title = book.find("h3").find("a")["title"]
        price = float(book.find("p", class_="price_color").text.replace("£", ""))

        rating = rating_map.get(book.find("p", class_="star-rating")["class"][1])
        if rating is None:
            raise ValueError(f"Неизвестный рейтинг книги: {title}")
        link = urljoin(base_url, book.find("h3").find("a")["href"])

        return {"title": title, "price": price, "rating": rating, "link": link}
    except ValueError:
        raise
    except Exception as e:
        print("Ошибка", e)


def get_page(page_url):
    attempt = 0
    while attempt < 3:
        try:
            response = requests.get(page_url, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            break
        except RequestException as e:
            print("Ошибка запроса страницы:", page_url, "\n", e)
            attempt += 1
    if attempt == 3:
        return None
    return soup


def parse_page(soup):
    books = soup.select("article.product_pod")
    books_data = []
    for book in books:
        result = parse_book(book)
        if result is not None:
            books_data.append(result)
    return books_data


def has_next_page(soup):
    return bool(soup.select_one("li.next"))


def scrape_books(max_pages=4):
    books_data = []
    page = 1

    while page <= max_pages:
        print(page)

        if page == 1:
            page_url = "https://books.toscrape.com/"
        else:
            page_url = f"https://books.toscrape.com/catalogue/page-{page}.html"

        soup = get_page(page_url)

        if soup is None:
            break

        books_data += parse_page(soup)

        if not has_next_page(soup):
            break

        page += 1

    return books_data


if __name__ == "__main__":
    books_data = scrape_books()

    print(len(books_data))
    print(
        all(
            isinstance(book["rating"], int) and 1 <= book["rating"] <= 5
            for book in books_data
        )
    )
    print(len(books_data) == len(set(book["link"] for book in books_data)))
    print(all(book["price"] > 0 for book in books_data))
    with open("result.csv", "w", encoding="UTF-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "price", "rating", "link"])
        writer.writeheader()
        writer.writerows(books_data)
