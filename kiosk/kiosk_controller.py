from tkinter import simpledialog

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
        self.cart = self.model.add_product_to_cart(self.cart, product, quantity)
        self.view.load_cart_list(self.cart)

    def clear_cart(self):
        """Clears the cart."""
        self.cart = self.model.clear_cart()
        self.view.load_cart_list(self.cart)

    def checkout(self):
        """Handles the checkout process."""
        if not self.cart:
            self.view.show_warning("Koszyk Pusty", "Nie możesz złożyć zamówienia z pustym koszykiem.")
            return

        total_price = self.model.calculate_total(self.cart)
        self.view.show_info("Zamówienie złożone", f"Twoje zamówienie o wartości {total_price:.2f} PLN zostało złożone!")
        self.clear_cart()

    def show_user_sets(self):
        """Handles showing user sets."""
        if self.current_rfid is None:
            self.view.show_warning("Brak karty", "Nie zeskanowano karty. Zeskanuj kartę, aby zobaczyć swoje zestawy.")
        else:
            user_sets = self.model.get_sets_by_rfid(self.current_rfid)
            
            self.view.display_user_sets(user_sets, self.add_set_to_cart, self.delete_set, self.rename_set)

    def add_set_to_cart(self, set_items):
        """Adds all items in the set to the cart."""
        for item in set_items:
            self.cart = self.model.add_product_to_cart(self.cart, item["product"], item["quantity"])
        self.view.load_cart_list(self.cart)

    def delete_set(self, set_name):
        """Deletes a set."""
        self.model.delete_set(set_name)
        self.view.show_info("Usunięto zestaw", f"Zestaw {set_name} został usunięty.")
        self.show_user_sets()

    def rename_set(self, set_name):
        """Renames a set."""
        new_name = simpledialog.askstring("Zmiana nazwy", f"Podaj nową nazwę dla zestawu {set_name}:")
        if new_name:
            self.model.rename_set(set_name, new_name)
            self.view.show_info("Zmiana nazwy", f"Zestaw {set_name} został zmieniony na {new_name}.")
            self.show_user_sets() 

    def handle_rfid_input(self, rfid):
        """Handles the input from the RFID terminal."""
        self.current_rfid = rfid
        self.view.update_rfid_display(rfid)