from tkinter import messagebox

class KioskController:
    """Controller responsible for coordinating the View and Model."""

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.cart = {}
        self.current_rfid = None

        # Load initial data
        self.load_categories()

        # Connect View events to Controller methods
        view.bind_controller(self)

    def load_categories(self):
        """Loads categories from the model and displays them in the view."""
        categories = self.model.get_categories()
        self.view.load_categories(categories)

    def on_category_select(self, event):
        """Handles category selection."""
        category = self.view.get_selected_category()
        if category is None:
            return
        
        products = self.model.get_products_by_category(category)
        self.view.load_products(products)

    def add_to_cart(self, product, quantity=1):
        """Adds a product to the cart."""
        product_name = product[1]
        product_price = product[2]

        if product_name in self.cart:
            self.cart[product_name]["quantity"] += quantity
        else:
            self.cart[product_name] = {"quantity": quantity, "price": product_price}

        self.view.load_cart_list(self.cart)

    def add_set_to_cart(self, set_items_list):
        """Adds all items in a user-defined set to the cart."""
        for set_item in set_items_list:
            product = set_item["product"]
            product_quantity = set_item["quantity"]
            self.add_to_cart(product, product_quantity)

        self.view.load_cart_list(self.cart)

    def clear_cart(self):
        """Clears the cart."""
        self.cart = {}
        self.view.load_cart_list(self.cart)

    def checkout(self):
        """Handles the checkout process."""
        if not self.cart:
            self.view.master.bell()
            messagebox.showwarning("Koszyk Pusty", "Nie możesz złożyć zamówienia z pustym koszykiem.")
            return

        total_price = sum(details["price"] * details["quantity"] for details in self.cart.values())
        messagebox.showinfo("Zamówienie złożone", f"Twoje zamówienie o wartości {total_price:.2f} PLN zostało złożone!")
        self.clear_cart()

    def show_user_sets(self):
        """Handles showing user sets."""
        if self.current_rfid is None:
            messagebox.showwarning("Brak karty", "Nie zeskanowano karty. Zeskanuj kartę, aby zobaczyć swoje zestawy.")
        else:
            user_sets = self.model.get_sets_by_rfid(self.current_rfid)
            if not user_sets:
                messagebox.showinfo("Moje Zestawy", "Nie znaleziono zestawów przypisanych do Twojej karty.")
            else:
                self.view.display_user_sets(user_sets, self.add_set_to_cart, self.delete_set, self.rename_set)

    def delete_set(self, set_name):
        """Deletes a user-defined set."""
        self.model.delete_set(set_name)
        messagebox.showinfo("Zestaw usunięty", f"Zestaw '{set_name}' został usunięty.")

    def rename_set(self, old_name):
        """Renames a user-defined set."""
        new_name = self.view.prompt_rename_set(old_name)
        if new_name:
            self.model.rename_set(old_name, new_name)
            messagebox.showinfo("Zestaw Zmieniony", f"Zestaw '{old_name}' został zmieniony na '{new_name}'.")

    def handle_mqtt_message(self, data):
        """Handles incoming MQTT messages."""
        if "rfid" in data:
            self.set_current_rfid(data["rfid"])

    def set_current_rfid(self, rfid):
        """Sets the currently active RFID."""
        self.current_rfid = rfid
        print(f"RFID registered: {rfid}")
    
    def handle_rfid_input(self, rfid):
        """Handles the input from the RFID terminal."""
        print(f"Processing RFID: {rfid}")
        # Pass the RFID to the model (you can store it or use it for further processing)
        self.set_current_rfid(rfid)