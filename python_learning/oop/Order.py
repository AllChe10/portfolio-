from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


# ДОБАВЛЕНО: клиент хранится отдельным объектом с контактными данными.
class Client:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone


# ИЗМЕНЕНО: цена и округление относятся к отдельной позиции заказа.
class OrderItem:
    def __init__(self, name, quantity, unit_price):
        self.name = name
        self.quantity = quantity
        self.unit_price = unit_price

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("Количество должно быть целым числом больше нуля")

        self._quantity = value

    @property
    def unit_price(self):
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value):
        try:
            value = Decimal(str(value))
        except InvalidOperation:
            raise ValueError("Цена услуги должна быть числом")

        if not value.is_finite():
            raise ValueError("Цена услуги должна быть конечным числом")

        value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if value <= 0:
            raise ValueError("Цена услуги должна быть больше нуля")

        self._unit_price = value

    @property
    def total(self):
        return self.unit_price * self.quantity


# ИЗМЕНЕНО: цена заказа рассчитывается по списку позиций.
class Order:
    def __init__(self, client, items):
        self.client = client
        self.items = items
        self._status = "Новый"

    @property
    def status(self):
        return self._status

    @property
    def price(self):
        total = Decimal("0.00")
        for position in self.items:
            total += position.total
        return total

    def start_work(self):
        if self._status == "Новый":
            self._status = "В работе"
            print("Работа началась")
        else:
            print("Нельзя начать работу")

    def complete(self):
        if self._status == "В работе":
            self._status = "Завершён"
            print("Заказ завершён")
        else:
            print("Нельзя завершить заказ")

    # ИЗМЕНЕНО: выводятся имя и телефон из объекта Client.
    def show_info(self):
        print(
            f"Клиент: {self.client.name}\n"
            f"Телефон: {self.client.phone}\n"
            f"Цена: {self.price}\n"
            f"Статус: {self.status}"
        )

    def get_total_price(self):
        return self.price

    def cancel(self):
        if self._status in ["Новый", "В работе"]:
            self._status = "Отменён"
        else:
            print("Отмена невозможна")


# ИЗМЕНЕНО: срочный заказ получает позиции и доплату.
class UrgentOrder(Order):
    def __init__(self, client, items, surcharge):
        super().__init__(client, items)
        self.surcharge = surcharge

    @property
    def surcharge(self):
        return self._surcharge

    @surcharge.setter
    def surcharge(self, surcharge):
        try:
            surcharge = Decimal(str(surcharge))
        except InvalidOperation:
            raise ValueError("Доплата должна быть числом")

        if not surcharge.is_finite():
            raise ValueError("Доплата должна быть конечным числом")

        if surcharge < 0:
            raise ValueError("Доплата не должна быть меньше нуля")

        self._surcharge = surcharge.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def show_info(self):
        super().show_info()
        print(f"Доплата за срочность: {self.surcharge}")
        print(f"Сумма вместе с доплатой: {self.get_total_price()}")

    def get_total_price(self):
        return self.price + self.surcharge


# ИЗМЕНЕНО: демонстрационные заказы используют Client и список позиций.
if __name__ == "__main__":
    orders = [
        Order(
            Client("Иван", "+7 000 000-00-00"),
            [OrderItem("Подшив брюк", 1, 5000)],
        ),
        UrgentOrder(
            Client("Анна", "+7 000 000-00-00"),
            [OrderItem("Подшив брюк", 1, 5000)],
            1500,
        ),
        Order(
            Client("Пётр", "+7 000 000-00-00"),
            [OrderItem("Ремонт рукава", 1, 3000)],
        ),
        UrgentOrder(
            Client("Мария", "+7 000 000-00-00"),
            [OrderItem("Подгонка платья", 1, 7000)],
            2000,
        ),
    ]
    for order in orders:
        print(order.get_total_price())