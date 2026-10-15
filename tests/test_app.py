
import unittest
from pathlib import Path


class TestOnlineBookstore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_folder = Path(__file__).resolve().parent.parent
        cls.html = (project_folder / "index.html").read_text(
            encoding="utf-8"
        )

    def test_six_books_are_available(self):
        self.assertGreaterEqual(self.html.count("{id:"), 6)

    def test_book_search_exists(self):
        self.assertIn('id="search"', self.html)
        self.assertIn("book.title.toLowerCase()", self.html)
        self.assertIn("book.author.toLowerCase()", self.html)

    def test_category_filter_exists(self):
        self.assertIn('id="category"', self.html)
        self.assertIn('value="Programming"', self.html)
        self.assertIn('value="Fiction"', self.html)

    def test_prices_and_stock_are_displayed(self):
        self.assertIn("price:", self.html)
        self.assertIn("stock:", self.html)
        self.assertIn("Out of stock", self.html)

    def test_cart_and_order_features_exist(self):
        self.assertIn("function addToCart", self.html)
        self.assertIn("function displayCart", self.html)
        self.assertIn("function placeOrder", self.html)
        self.assertIn("Order placed successfully!", self.html)

    def test_order_status_and_confirmation(self):
        self.assertIn("Status: Confirmed", self.html)
        self.assertIn("Thank you for shopping with us!", self.html)


if __name__ == "__main__":
    unittest.main()
