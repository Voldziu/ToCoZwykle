class KioskModel:
    """Model responsible for managing data logic."""

    def __init__(self, db):
        self.db = db

    def get_categories(self):
        """Fetches categories from the database."""
        return self.db.get_categories()

    def get_products_by_category(self, category):
        """Fetches products for a specific category."""
        return self.db.get_products_by_category(category)

    def get_sets_by_rfid(self, rfid):
        """Fetches user sets by RFID."""
        return self.db.get_sets_by_rfid(rfid)
    
    def add_product_to_cart(self, cart, product, quantity=1):
        """Adds product to cart and returns the updated cart."""
        product_name = product[1]
        product_price = product[2]
        
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
    
    def delete_set(self, set_name):
        """Deletes a user-defined set from the database."""
        pass

    def rename_set(self, old_name, new_name):
        """Renames a user-defined set in the database."""
        pass