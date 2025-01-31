import threading
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

        self.my_sets_button = tk.Button(self.categories_frame, text="Moje Zestawy", state=tk.DISABLED)
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

        self.cart_listbox = tk.Listbox(self.cart_frame, width=20, height=20)
        self.cart_listbox.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        # Dodanie Scrollbara do koszyka
        self.cart_scrollbar = tk.Scrollbar(self.cart_frame, orient="vertical")
        self.cart_scrollbar.config(command=self.cart_listbox.yview)
        self.cart_listbox.config(yscrollcommand=self.cart_scrollbar.set)
        self.cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Przycisk do edytowania koszyka
        # self.edit_cart_button = tk.Button(self.cart_frame, text="Edytuj Koszyk", command=self.edit_cart)
        # self.edit_cart_button.pack(pady=2)

        # Przycisk do zapisywania koszyka jako zestaw
        self.save_set_button = tk.Button(self.cart_frame, text="Zapisz jako Zestaw", command=lambda: self.save_cart_as_set(self.cart), state=tk.DISABLED)
        self.save_set_button.pack(pady=2)

        self.clear_cart_button = tk.Button(self.cart_frame, text="Wyczyść Koszyk", command=self.controller.clear_cart if self.controller else None)
        self.clear_cart_button.pack(pady=5)

        self.checkout_button = tk.Button(self.cart_frame, text="Zamów", command=self.start_checkout if self.controller else None)
        self.checkout_button.pack(pady=5)

        # Mini-panel dla "Moje Zestawy"
        self.user_sets_panel = tk.Frame(self.main_frame, bg="white", bd=2, relief=tk.RIDGE)
        self.user_sets_panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.user_sets_panel.place_forget()  # Ukryj panel domyślnie

        self.user_sets_label = tk.Label(self.user_sets_panel, text="Moje Zestawy", font=("Helvetica", 16), bg="white")
        self.user_sets_label.pack(pady=10)

        self.user_sets_content = tk.Frame(self.user_sets_panel, bg="white")
        self.user_sets_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.close_sets_panel_button = tk.Button(self.user_sets_panel, text="Zamknij", command=self.hide_user_sets_panel)
        self.close_sets_panel_button.pack(pady=10)


    def bind_controller(self, controller):
        """Binds the controller to the view and connects events."""
        self.controller = controller
        self.categories_listbox.bind("<<ListboxSelect>>", controller.on_category_select)
        self.my_sets_button.config(command=controller.show_user_sets)
        self.clear_cart_button.config(command=controller.clear_cart)
        self.checkout_button.config(command=self.start_checkout)

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
            self.categories_listbox.insert(tk.END, category['name'])

    def load_products(self, products):
        """Displays products in the grid."""
        for widget in self.products_grid_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        for product in products:
            product_frame = tk.Frame(self.products_grid_frame, bg="lightblue", bd=2, relief=tk.RAISED)
            product_frame.grid(row=row, column=col, padx=10, pady=10)

            tk.Label(product_frame, text=product['name'], font=("Helvetica", 14), bg="lightblue").pack(pady=5)
            tk.Label(product_frame, text=f"{product['price']} PLN", font=("Helvetica", 12), bg="lightblue").pack(pady=5)
            tk.Button(product_frame, text="Dodaj", command=lambda p=product: self.controller.add_to_cart(p)).pack(
                pady=5)

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
        self.cart = self.controller.cart

    def display_user_sets(self, user_sets, add_set_to_cart, delete_set, rename_set, select_set_callback=None):
        """Displays user-defined sets in a mini-panel."""
        self.user_sets_content.destroy()  # Usuń poprzednią zawartość
        self.user_sets_content = tk.Frame(self.user_sets_panel, bg="white")
        self.user_sets_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if not user_sets or user_sets == {}:
            tk.Label(self.user_sets_content, text="Nie znaleziono zestawów przypisanych do Twojej karty.", bg="white",
                     font=("Helvetica", 12)).pack(pady=10)


        # Scrollbar i Canvas dla przewijania, jeśli zestawów jest dużo
        canvas = tk.Canvas(self.user_sets_content, bg="white")
        if(user_sets!={}):
            scrollbar = tk.Scrollbar(self.user_sets_content, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="white")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        # Create frames for each set
            for set_name, set_items_list in user_sets.items():
                set_frame = tk.LabelFrame(scrollable_frame, text=set_name, font=("Helvetica", 14), padx=10, pady=10,
                                          bg="white")
                set_frame.pack(fill=tk.X, pady=5, padx=5)

                # Display items in the set
                for set_item in set_items_list:
                    product_name = set_item["name"]
                    product_quantity = set_item["quantity"]
                    product_label = tk.Label(set_frame, text=f"{product_name}: {product_quantity}", font=("Helvetica", 12),
                                             bg="white")
                    product_label.pack(anchor="w", padx=5, pady=2)

                # Create a frame for buttons
                button_frame = tk.Frame(set_frame, bg="white")
                button_frame.pack(fill=tk.X, pady=5)
                if not select_set_callback:
                # "Add to Cart" button
                    add_to_cart_button = tk.Button(button_frame, text="Dodaj do koszyka",
                                                command=lambda s=set_items_list: add_set_to_cart(s))
                    add_to_cart_button.pack(side=tk.LEFT, padx=5)

                    # "Delete" button with confirmation
                    delete_button = tk.Button(button_frame, text="Usuń",
                                            command=lambda s=set_name: self._confirm_and_delete_set(s, delete_set))
                    delete_button.pack(side=tk.LEFT, padx=5)

                    # "Rename" button
                    rename_button = tk.Button(button_frame, text="Zmień nazwę", command=lambda s=set_name: rename_set(s))
                    rename_button.pack(side=tk.LEFT, padx=5)

                if select_set_callback:
                    select_button = tk.Button(button_frame, text="Wybierz do nadpisania",
                                              command=lambda s=set_name: select_set_callback(s))
                    select_button.pack(side=tk.LEFT, padx=5)

        self.show_user_sets_panel()

    def start_checkout(self):
        """Rozpoczyna proces checkout w osobnym wątku."""
        # Wyłącz przycisk, aby zapobiec wielokrotnym kliknięciom
        self.checkout_button.config(state=tk.DISABLED)

        # Uruchomienie checkout w nowym wątku
        thread = threading.Thread(target=self.run_checkout)
        thread.start()

    def run_checkout(self):
        """Wykonuje checkout w osobnym wątku."""
        # Wykonanie checkout
        cart = self.controller.checkout()
        self.checkout_button.config(state=tk.NORMAL)

    def _confirm_and_delete_set(self, set_name, delete_set_callback):
        """
        Prompts the user to confirm deletion of a set.

        Parameters:
            set_name (str): The name of the set to delete.
            delete_set_callback (function): The callback function to delete the set.
        """
        confirm = messagebox.askyesno("Potwierdzenie Usunięcia", f"Czy na pewno chcesz usunąć zestaw '{set_name}'?")
        if confirm:
            delete_set_callback(set_name)
            self.show_info("Usunięto Zestaw", f"Zestaw '{set_name}' został pomyślnie usunięty.")
        else:
            # Użytkownik anulował operację
            self.show_info("Anulowano", f"Usuwanie zestawu '{set_name}' zostało anulowane.")

    def save_cart_as_set(self,cart):
        """Handles saving the current cart as a set."""
        if not cart:
            self.show_warning("Koszyk Pusty", "Nie możesz zapisać pustego koszyka jako zestaw.")
            return


        # Zapytaj użytkownika, czy chce stworzyć nowy zestaw czy nadpisać istniejący
        choice = messagebox.askquestion("Zapisz Zestaw",
                                        "Czy chcesz stworzyć nowy zestaw? Kliknij 'Tak' aby stworzyć nowy, lub 'Nie' aby nadpisać istniejący.")

        if choice == 'yes':
            # Tworzenie nowego zestawu
            set_name = simpledialog.askstring("Nazwa Zestawu", "Wprowadź nazwę dla nowego zestawu:")
            if set_name:
                try:
                    self.controller.add_set(set_name, cart)
                    self.show_info("Zapisano Zestaw", f"Zestaw '{set_name}' został pomyślnie zapisany.")
                except Exception as e:
                    self.show_warning("Błąd", f"Nie udało się zapisać zestawu: {str(e)}")
        else:
            # Nadpisywanie istniejącego zestawu
            # Wybierz zestaw do nadpisania
            self.controller.show_user_sets(self.select_set_to_overwrite)

    def select_set_to_overwrite(self, set_name):
        """Handles the selection of a set to overwrite."""
        # Ask if the user wants to rename the set before overwriting
        rename_choice = messagebox.askyesno("Nadpisz Zestaw",
                                            f"Czy chcesz zmienić nazwę zestawu '{set_name}' przed nadpisaniem?")

        if rename_choice:
            new_set_name = simpledialog.askstring("Zmiana Nazwy", f"Podaj nową nazwę dla zestawu '{set_name}':")
            if not new_set_name:
                self.show_warning("Brak Nazwy", "Nie podałeś nowej nazwy zestawu. Operacja została anulowana.")
                return
        else:
            new_set_name = set_name  # Keep the same name

        try:
            self.controller.overwrite_set(set_name, new_set_name, self.cart)
            self.show_info("Nadpisano Zestaw", f"Zestaw '{set_name}' został nadpisany.")
        except Exception as e:
            self.show_warning("Błąd", f"Nie udało się nadpisać zestawu: {str(e)}")

    def show_user_sets_panel(self):
        """Pokazuje mini-panel z zestawami użytkownika."""
        self.user_sets_panel.lift()  # Przenieś panel na wierzch
        self.user_sets_panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def hide_user_sets_panel(self):
        """Ukrywa mini-panel z zestawami użytkownika."""
        self.user_sets_panel.place_forget()

    def show_warning(self, title, message):
        """Displays a warning message."""
        messagebox.showwarning(title, message)

    def show_info(self, title, message):
        """Displays an info message."""
        messagebox.showinfo(title, message)

    def update_rfid_display(self, rfid):
        """Updates the display when an RFID is inputted."""
        print(f"RFID: {rfid}")

    def update_buttons_state(self):
        """Aktualizuje stan przycisków zależnie od tego, czy użytkownik ma zeskanowaną kartę."""
        state = tk.NORMAL if self.controller.current_rfid else tk.DISABLED
        self.save_set_button.config(state=state)
        self.my_sets_button.config(state=state)
