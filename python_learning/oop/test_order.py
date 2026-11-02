from decimal import Decimal

import pytest

# ИЗМЕНЕНО: тестам нужен объект Client наряду с классами заказов.
from Order import Client, Order, OrderItem, UrgentOrder


# ДОБАВЛЕНО: общая тестовая фабрика контактных данных клиента.
def make_client(name="Иван", phone="+7 000 000-00-00"):
    return Client(name, phone)


# ИЗМЕНЕНО: тестовые заказы создаются с клиентом и списком позиций.
def make_items(price=500):
    return [OrderItem("Услуга", 1, price)]


@pytest.fixture
def make_order():
    def _make_order(client="Иван", price=500):
        return Order(make_client(client), make_items(price))

    return _make_order


def test_client_stores_contact_details():
    client = Client("Иван Петров", "+7 000 000-00-00")

    assert client.name == "Иван Петров"
    assert client.phone == "+7 000 000-00-00"


def test_cancel_now(make_order):
    order = make_order()

    order.cancel()
    assert order.status == "Отменён"


def test_cancel_work(make_order):
    order = make_order()
    order.start_work()
    order.cancel()
    assert order.status == "Отменён"


def test_cancel_complete(make_order, capsys):
    order = make_order()
    order.start_work()
    order.complete()
    order.cancel()
    assert order.status == "Завершён"
    assert (
        "Работа началась\nЗаказ завершён\nОтмена невозможна\n"
        in capsys.readouterr().out
    )


def test_cancel_already_cancelled_order(make_order, capsys):
    order = make_order()
    order.cancel()
    order.cancel()

    assert order.status == "Отменён"
    assert "Отмена невозможна" in capsys.readouterr().out


def test_urgent_cancel():
    urgent_order = UrgentOrder(make_client(), make_items(), 500)
    urgent_order.cancel()
    assert urgent_order.status == "Отменён"


# ИЗМЕНЕНО: проверки цены услуги относятся к OrderItem.
@pytest.mark.parametrize("price", [0, -0.01])
def test_rejects_non_positive_price(price):
    with pytest.raises(ValueError):
        OrderItem("Услуга", 1, price)


@pytest.mark.parametrize("surcharge", [-0.01, -1, "-0.004"])
def test_rejects_negative_surcharge(surcharge):
    with pytest.raises(ValueError):
        UrgentOrder(make_client(), make_items(), surcharge)


def test_zero_surcharge_is_allowed():
    order = UrgentOrder(make_client(), make_items(), 0)

    assert order.surcharge == 0
    assert order.get_total_price() == Decimal("500.00")


def test_complete_not_work(make_order, capsys):
    order = make_order()
    order.complete()
    assert order.status == "Новый"
    assert "Нельзя завершить заказ" in capsys.readouterr().out


def test_show_info(make_order, capsys):
    order = make_order()
    order.show_info()
    output = capsys.readouterr().out

    assert "Клиент: Иван" in output
    assert "Телефон: +7 000 000-00-00" in output
    assert "Цена: 500" in output
    assert "Статус: Новый" in output


def test_urgent_show_info(capsys):
    urgent_order = UrgentOrder(make_client(), make_items(), 500)
    urgent_order.show_info()
    output = capsys.readouterr().out

    assert "Клиент: Иван" in output
    assert "Телефон: +7 000 000-00-00" in output
    assert "Цена: 500" in output
    assert "Статус: Новый" in output
    assert "Доплата за срочность: 500" in output
    assert "Сумма вместе с доплатой: 1000" in output


def test_start_twice(make_order, capsys):
    order = make_order()
    order.start_work()
    assert order.status == "В работе"
    order.start_work()
    assert order.status == "В работе"
    output = capsys.readouterr().out
    assert "Работа началась" in output
    assert "Нельзя начать работу" in output


def test_urgent_order_calculates_fractional_total():
    order = UrgentOrder(make_client(), make_items("0.1"), "0.2")
    assert order.get_total_price() == Decimal("0.30")


@pytest.mark.parametrize("price", ["NaN", "Infinity", "-Infinity"])
def test_rejects_non_finite_price(price):
    with pytest.raises(ValueError):
        OrderItem("Услуга", 1, price)


@pytest.mark.parametrize("surcharge", ["NaN", "Infinity", "-Infinity"])
def test_rejects_non_finite_surcharge(surcharge):
    with pytest.raises(ValueError):
        UrgentOrder(make_client(), make_items(), surcharge)


@pytest.mark.parametrize(
    ("price", "expected"),
    [("2.674", "2.67"), ("2.675", "2.68")],
)
def test_price_rounds_to_kopecks(price, expected):
    position = OrderItem("Услуга", 1, price)
    assert position.unit_price == Decimal(expected)


def test_price_that_rounds_to_zero_is_rejected():
    with pytest.raises(ValueError):
        OrderItem("Услуга", 1, "0.004")


@pytest.mark.parametrize(
    ("surcharge", "expected"),
    [("2.674", "2.67"), ("2.675", "2.68"), ("0.004", "0.00")],
)
def test_surcharge_rounds_to_kopecks(surcharge, expected):
    order = UrgentOrder(make_client(), make_items(), surcharge)
    assert order.surcharge == Decimal(expected)


def test_order_item_stores_service_data():
    position = OrderItem("Подшив брюк", 2, Decimal("500.00"))

    assert position.name == "Подшив брюк"
    assert position.quantity == 2
    assert position.unit_price == Decimal("500.00")


def test_order_item_calculates_total():
    position = OrderItem("Подшив брюк", 2, Decimal("500.00"))

    assert position.total == Decimal("1000.00")


# ДОБАВЛЕНО: несколько позиций суммируются в цену заказа.
def test_order_price_is_sum_of_positions():
    positions = [
        OrderItem("Подшив брюк", 2, Decimal("500.00")),
        OrderItem("Ремонт рукава", 1, Decimal("300.00")),
    ]

    order = Order(make_client(), positions)

    assert order.price == Decimal("1300.00")


@pytest.mark.parametrize("value", ["abc", ""])
def test_rejects_non_numeric_price(value):
    with pytest.raises(ValueError):
        OrderItem("Услуга", 1, value)


@pytest.mark.parametrize("value", ["abc", ""])
def test_rejects_non_numeric_surcharge(value):
    with pytest.raises(ValueError):
        UrgentOrder(make_client(), make_items(), value)


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True])
def test_rejects_invalid_quantity(quantity):
    with pytest.raises(ValueError):
        OrderItem("Подшив брюк", quantity, Decimal("500.00"))