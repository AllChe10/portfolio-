class Product:
    currency = "RUB"

    def __init__(self, name, price, quantity):

        self.name = name
        self.price = price
        self.quantity = quantity

    def show_info(self):
        print(
            f"Товар: {self.name}\nЦена: {self.price} {self.currency}\nКоличество: {self.quantity}"
        )

    def get_total_price(self):
        return self.price * self.quantity


product_1 = Product("Ткань", 500, 4)
product_1.currency = "USD"
product_2 = Product("Шторы", 300, 2)
product_1.show_info()
product_2.show_info()
print(product_1.get_total_price())
