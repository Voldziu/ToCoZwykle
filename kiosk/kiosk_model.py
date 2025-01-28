import requests

class KioskModel:
    """Model responsible for managing data logic and interacting with Flask API."""

    BASE_URL = "http://127.0.0.1:5000"  # Flask server URL

    def get_categories(self):
        """Fetches categories from the Flask API."""
        response = requests.get(f"{self.BASE_URL}/categories")
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_products_by_category(self, category):
        """Fetches products for a specific category from lask FAPI."""
        response = requests.get(f"{self.BASE_URL}/products?category={category}")
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_sets_by_rfid(self, rfid):
        """Fetches user sets by RFID from Flask API."""
        response = requests.get(f"{self.BASE_URL}/rfid/{rfid}/sets")
        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def add_product_to_cart(self, cart, product, quantity=1):
        """Adds product to cart and returns the updated cart."""
        product_name = product["name"]
        product_price = product["price"]
        
        if product_name in cart:
            cart[product_name]["quantity"] += quantity
        else:
            cart[product_name] = {"quantity": quantity, "price": product_price}
        
        return cart

    def calculate_total(self, cart):
        """Calculates the total price of items in the cart."""
        return sum(details["price"] * details["quantity"] for details in cart.values())
    
    def clear_cart(self):
        """Clears the cart."""
        return {}

    def add_category(self, category_id, name):
        """Sends a request to add a category via Flask API."""
        data = {"category_id": category_id, "name": name}
        response = requests.post(f"{self.BASE_URL}/categories", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            return {"message": "Failed to add category"}

    def add_product(self, product_id, name, price, category_id):
        """Sends a request to add a product via Flask API."""
        data = {"product_id": product_id, "name": name, "price": price, "category_id": category_id}
        response = requests.post(f"{self.BASE_URL}/products", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            return {"message": "Failed to add product"}

    def assign_sets_to_rfid(self, rfid, sets_dict):
        """Sends request to assign sets to RFID."""
        data = {"rfid": rfid, "sets": sets_dict}
        response = requests.post(f"{self.BASE_URL}/rfid", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            return {"message": "Failed to assign sets to RFID"}