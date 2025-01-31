from copy import copy
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
        self.view.cart = self.cart

    def checkout(self):
        """Handles the checkout process."""
        print("checkout")

        if not self.cart:
            self.view.show_warning("Koszyk Pusty", "Nie możesz złożyć zamówienia z pustym koszykiem.")
            return

        total_price = self.model.calculate_total(self.cart)
        self.view.show_info("Zamówienie złożone", f"Twoje zamówienie o wartości {total_price:.2f} PLN zostało złożone!")
        
        cart = copy(self.cart)
        print(cart)
        
        self.clear_cart()
        print(cart)

        # Odlączenie karty po zamówieniu
        if self.current_rfid:
            self.current_rfid = None
            self.view.update_rfid_display(None)
            self.view.update_buttons_state()
        
        
        return cart


    def show_user_sets(self,select_set_callback=None):
        """Handles showing user sets."""
        if self.current_rfid is None:
            self.view.show_warning("Brak karty", "Nie zeskanowano karty. Zeskanuj kartę, aby zobaczyć swoje zestawy.")
        else:
            user_sets = self.model.get_sets_by_rfid(self.current_rfid)
            print(user_sets)
            
            self.view.display_user_sets(user_sets, self.add_set_to_cart, self.delete_set, self.rename_set ,select_set_callback)

    def add_set_to_cart(self, set_items):
        """Adds all items in the set to the cart."""
        for item in set_items:
            print(item)
            self.cart = self.model.add_product_to_cart(self.cart,item)
        self.view.load_cart_list(self.cart)

    def delete_set(self, set_name):
        """Deletes a set."""
        self.model.delete_set(set_name,self.current_rfid)
        #self.view.show_info("Usunięto zestaw", f"Zestaw {set_name} został usunięty.")
        self.show_user_sets()

    def add_set(self, set_name, cart):
        if self.model.does_set_exist(set_name, self.current_rfid):
            self.overwrite_set(set_name, set_name, cart) 
        else:
            self.model.add_set(set_name, cart, self.current_rfid)
        self.show_user_sets()

    def overwrite_set(self,set_name_old,set_name_new,cart):
        self.model.overwrite_set(set_name_old,set_name_new,cart,self.current_rfid)
        self.show_user_sets()

    def rename_set(self, set_name_old):
        """Renames a set."""
        set_name_new = simpledialog.askstring("Zmiana nazwy", f"Podaj nową nazwę dla zestawu {set_name_old}:")
        if set_name_new:
            self.model.rename_set(set_name_old,self.current_rfid, set_name_new)
            self.view.show_info("Zmiana nazwy", f"Zestaw {set_name_old} został zmieniony na {set_name_new}.")
            self.show_user_sets() 

    def handle_rfid_input(self, rfid):
        """Obsługuje wejście RFID - sprawdza i dodaje nowe, jeśli nie istnieje."""
        response = self.model.check_and_add_rfid(rfid)

        if response.get("rfid"):
            self.current_rfid = rfid
            self.view.update_rfid_display(rfid)
            self.view.update_buttons_state() 
            self.view.show_info("RFID", response["message"])
        else:
            self.view.show_warning("Błąd RFID", response["message"])