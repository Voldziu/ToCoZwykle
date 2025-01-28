import tkinter as tk
from tkinter import simpledialog, messagebox

class KioskView:
    """View responsible for the GUI."""

    def __init__(self, master):
        self.master = master
        self.controller = None  # Controller will be set later

        # Main window setup
        master.title("To co zwykle - Kiosk Samoobsługowy")
        master.geometry("1000x600")

        self.cart = {}

        # Main layout
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Categories panel
        self.categories_frame = tk.Frame(self.main_frame, bg="lightgray", width=200)
        self.categories_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self.categories_label = tk.Label(self.categories_frame, text="Kategorie", font=("Helvetica", 16), bg="lightgray")
        self.categories_label.pack(pady=10)

        self.categories_listbox = tk.Listbox(self.categories_frame, width=20, height=25)
        self.categories_listbox.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.my_sets_button = tk.Button(self.categories_frame, text="Moje Zestawy")
        self.my_sets_button.pack(side=tk.BOTTOM, pady=10)

        # Products panel
        self.products_frame = tk.Frame(self.main_frame, bg="white")
        self.products_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.products_label = tk.Label(self.products_frame, text="Produkty", font=("Helvetica", 16), bg="white")
        self.products_label.pack(pady=10)

        self.products_grid_frame = tk.Frame(self.products_frame, bg="white")
        self.products_grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Cart panel
        self.cart_frame = tk.Frame(self.main_frame, bg="lightgray", width=200)
        self.cart_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        self.cart_label = tk.Label(self.cart_frame, text="Koszyk", font=("Helvetica", 16), bg="lightgray")
        self.cart_label.pack(pady=10)

        self.cart_listbox = tk.Listbox(self.cart_frame, width=20, height=25)
        self.cart_listbox.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.clear_cart_button = tk.Button(self.cart_frame, text="Wyczyść Koszyk")
        self.clear_cart_button.pack(pady=5)

        self.checkout_button = tk.Button(self.cart_frame, text="Zamów")
        self.checkout_button.pack(pady=5)

    def bind_controller(self, controller):
        """Binds the controller to the view and connects events."""
        self.controller = controller
        self.categories_listbox.bind("<<ListboxSelect>>", controller.on_category_select)
        self.my_sets_button.config(command=controller.show_user_sets)
        self.clear_cart_button.config(command=controller.clear_cart)
        self.checkout_button.config(command=controller.checkout)

    def get_selected_category(self):
        """Returns the name of the currently selected category from the listbox."""
        selected_index = self.categories_listbox.curselection()
        if selected_index:
            return self.categories_listbox.get(selected_index[0])
        else:
            return None

    def load_categories(self, categories):
        """Displays categories in the listbox."""
        self.categories_listbox.delete(0, tk.END)
        for category in categories:
            self.categories_listbox.insert(tk.END, category[1])

    def load_products(self, products):
        """Displays products in the grid."""
        for widget in self.products_grid_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        for product in products:
            product_frame = tk.Frame(self.products_grid_frame, bg="lightblue", bd=2, relief=tk.RAISED)
            product_frame.grid(row=row, column=col, padx=10, pady=10)

            tk.Label(product_frame, text=product[1], font=("Helvetica", 14), bg="lightblue").pack(pady=5)
            tk.Label(product_frame, text=f"{product[2]} PLN", font=("Helvetica", 12), bg="lightblue").pack(pady=5)
            tk.Button(product_frame, text="Dodaj", command=lambda p=product: self.controller.add_to_cart(p)).pack(pady=5)

            col += 1
            if col == 3:
                col = 0
                row += 1

    def load_cart_list(self, cart):
        """Updates the cart display."""
        self.cart_listbox.delete(0, tk.END)
        for product_name, details in cart.items():
            quantity = details["quantity"]
            total_price = quantity * details["price"]
            self.cart_listbox.insert(tk.END, f"{product_name} - {quantity}x - {total_price:.2f} PLN")

    def display_user_sets(self, user_sets, add_set_to_cart, delete_set, rename_set):
        """Displays user-defined sets with options to add to cart, delete, and rename."""
        top = tk.Toplevel(self.master)
        top.title("Moje Zestawy")

        if not user_sets:
            messagebox.showinfo("Moje Zestawy", "Nie znaleziono zestawów przypisanych do Twojej karty.")
            return

        # Create frames for each set
        for set_name, set_items_list in user_sets.items():
            set_frame = tk.LabelFrame(top, text=set_name, font=("Helvetica", 14), padx=10, pady=10)
            set_frame.pack(fill=tk.X, pady=5)

            # Display items in the set
            for set_item in set_items_list:
                product = set_item["product"]
                product_name = product["name"]
                product_quantity = set_item["quantity"]
                product_label = tk.Label(set_frame, text=f"{product_name}: {product_quantity}", font=("Helvetica", 12))
                product_label.pack(anchor="w", padx=5, pady=2)

            # Create a frame for buttons
            button_frame = tk.Frame(set_frame)
            button_frame.pack(fill=tk.X, pady=5)

            # "Add to Cart" button
            add_to_cart_button = tk.Button(button_frame, text="Dodaj do koszyka", command=lambda s=set_items_list: add_set_to_cart(s))
            add_to_cart_button.pack(side=tk.LEFT, padx=5)

            # "Delete" button
            delete_button = tk.Button(button_frame, text="Usuń", command=lambda s=set_name: delete_set(s))
            delete_button.pack(side=tk.LEFT, padx=5)

            # "Rename" button
            rename_button = tk.Button(button_frame, text="Zmień nazwę", command=lambda s=set_name: rename_set(s))
            rename_button.pack(side=tk.LEFT, padx=5)

        # Close button
        close_button = tk.Button(top, text="Zamknij", command=top.destroy)
        close_button.pack(pady=10)

    def show_warning(self, title, message):
        """Displays a warning message."""
        messagebox.showwarning(title, message)

    def show_info(self, title, message):
        """Displays an info message."""
        messagebox.showinfo(title, message)

    def update_rfid_display(self, rfid):
        """Updates the display when an RFID is inputted."""
        print(f"RFID: {rfid}")