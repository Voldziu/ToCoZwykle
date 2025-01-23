import tkinter as tk
from tkinter import messagebox, simpledialog
from database import MongoDB
from seeder import *
import threading
import time
import paho.mqtt.client as mqtt
from receiver import MqttClient
from PyQt6.QtCore import QCoreApplication
import sys
import random
import json
# Konfiguracja MQTT







class KioskApp:
    """Aplikacja Tkinter dla kiosku samoobsługowego."""

    def __init__(self, master, db, mqtt_client):
        self.master = master
        self.db = db
        master.title("To co zwykle - Kiosk Samoobsługowy")
        master.geometry("1000x600")

        self.current_rfid = None

        # Layout główny
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Lewy panel z kategoriami
        self.categories_frame = tk.Frame(self.main_frame, bg="lightgray", width=200)
        self.categories_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self.categories_label = tk.Label(
            self.categories_frame, text="Kategorie", font=("Helvetica", 16), bg="lightgray"
        )
        self.categories_label.pack(pady=10)

        self.categories_listbox = tk.Listbox(self.categories_frame, width=20, height=25)
        self.categories_listbox.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
        self.categories_listbox.bind("<<ListboxSelect>>", self.on_category_select)

        # Przycisk "Moje Zestawy"
        self.my_sets_button = tk.Button(
            self.categories_frame, text="Moje Zestawy", command=self.show_user_sets
        )
        self.my_sets_button.pack(side=tk.BOTTOM, pady=10)

        # Środkowy panel z produktami
        self.products_frame = tk.Frame(self.main_frame, bg="white")
        self.products_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.products_label = tk.Label(
            self.products_frame, text="Produkty", font=("Helvetica", 16), bg="white"
        )
        self.products_label.pack(pady=10)

        self.products_grid_frame = tk.Frame(self.products_frame, bg="white")
        self.products_grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Prawy panel z koszykiem
        self.cart_frame = tk.Frame(self.main_frame, bg="lightgray", width=200)
        self.cart_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        self.cart_label = tk.Label(
            self.cart_frame, text="Koszyk", font=("Helvetica", 16), bg="lightgray"
        )
        self.cart_label.pack(pady=10)

        self.cart_listbox = tk.Listbox(self.cart_frame, width=20, height=25)
        self.cart_listbox.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.clear_cart_button = tk.Button(self.cart_frame, text="Wyczyść Koszyk", command=self.clear_cart)
        self.clear_cart_button.pack(pady=5)

        self.checkout_button = tk.Button(self.cart_frame, text="Zamów", command=self.checkout)
        self.checkout_button.pack(pady=5)

        # Wczytanie kategorii z bazy danych
        self.load_categories()
        self.mqtt_client = mqtt_client
        self.mqtt_client.message_received.connect(self.handle_mqtt_message)

        # Koszyk
        self.cart = {}
    def load_categories(self):
        """Ładuje kategorie z bazy danych i wyświetla w lewym panelu."""
        categories = self.db.get_categories()
        self.categories_listbox.delete(0, tk.END)
        for category in categories:
            self.categories_listbox.insert(tk.END, category["name"])

    def on_category_select(self, event):
        """Obsługa wyboru kategorii."""
        selected_index = self.categories_listbox.curselection()
        if not selected_index:
            return
        category = self.categories_listbox.get(selected_index)
        self.load_products(category)

    def load_products(self, category):
        """Ładuje produkty z wybranej kategorii i wyświetla w widoku grid."""
        for widget in self.products_grid_frame.winfo_children():
            widget.destroy()

        products = self.db.get_products_by_category(category)
        row, col = 0, 0

        for product in products:
            # Tworzenie ramki dla produktu
            product_frame = tk.Frame(self.products_grid_frame, bg="lightblue", bd=2, relief=tk.RAISED)
            product_frame.grid(row=row, column=col, padx=10, pady=10)

            # Etykieta z nazwą produktu
            product_name_label = tk.Label(product_frame, text=product["name"], font=("Helvetica", 14), bg="lightblue")
            product_name_label.pack(pady=5)

            # Etykieta z ceną produktu
            product_price_label = tk.Label(product_frame, text=f"{product['price']} PLN", font=("Helvetica", 12), bg="lightblue")
            product_price_label.pack(pady=5)

            # Przycisk dodania do koszyka
            add_button = tk.Button(product_frame, text="Dodaj", command=lambda p=product: self.add_to_cart(p))
            add_button.pack(pady=5)

            col += 1
            if col == 3:  # Grid o szerokości 3
                col = 0
                row += 1

    def add_to_cart(self, product,quantity=1):
        print(product)

        """Dodaje produkt do koszyka."""
        product_name = product["name"]
        product_price = product["price"]

        if product_name in self.cart:
            # Produkt już istnieje w koszyku - zwiększ ilość
            self.cart[product_name]["quantity"] += quantity
        else:
            # Produkt nie istnieje w koszyku - dodaj nowy
            self.cart[product_name] = {"quantity": quantity, "price": product_price}

        self.update_cart_list()

    def add_set_to_cart(self,set_items_list):
        print(f"debug {set}")
        for set_item in set_items_list:
            product = set_item["product"]

            product_quantity = set_item['quantity']
            self.add_to_cart(product,product_quantity)

        self.update_cart_list()


    def update_cart_list(self):
        """Aktualizuje listę produktów w koszyku."""
        self.cart_listbox.delete(0, tk.END)
        for product_name, details in self.cart.items():
            print(product_name)
            print(details)
            quantity = details["quantity"]
            unit_price = details["price"]
            total_price = quantity * unit_price
            self.cart_listbox.insert(tk.END, f"{product_name} - {quantity}x - {total_price:.2f} PLN")

    def clear_cart(self):
        """Czyści koszyk."""
        self.cart = {}
        self.update_cart_list()

    def checkout(self):
        """Symuluje zamówienie produktów."""
        if not self.cart:
            messagebox.showwarning("Koszyk Pusty", "Nie możesz złożyć zamówienia z pustym koszykiem.")
            return

        total_price = sum(product["price"] for product in self.cart)
        messagebox.showinfo("Zamówienie złożone", f"Twoje zamówienie o wartości {total_price:.2f} PLN zostało złożone!")
        self.clear_cart()

    def show_user_sets(self):
        """Wyświetla zestawy użytkownika jako menu kontekstowe w głównym oknie."""
        if self.current_rfid is None:
            messagebox.showwarning("Brak karty", "Nie zeskanowano karty. Zeskanuj kartę, aby zobaczyć swoje zestawy.")
        else:
            user_sets = self.db.get_sets_by_rfid(self.current_rfid)
            if not user_sets:
                messagebox.showinfo("Moje Zestawy", "Nie znaleziono zestawów przypisanych do Twojej karty.")
            else:
                # Usuwanie istniejącego menu kontekstowego, jeśli już istnieje
                if hasattr(self, "context_menu") and self.context_menu.winfo_exists():
                    self.context_menu.destroy()

                # Tworzenie menu kontekstowego jako ramki
                self.context_menu = tk.Frame(self.master, bg="white", bd=2, relief=tk.RAISED)
                self.context_menu.place(relx=0.5, rely=0.5, anchor="center")  # Wyśrodkowanie menu

                # Tytuł menu
                title_label = tk.Label(self.context_menu, text="Twoje Zestawy", font=("Helvetica", 16), bg="white")
                title_label.pack(pady=10)

                # Scrollowalna ramka w menu
                scroll_frame = tk.Frame(self.context_menu, bg="white")
                scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                canvas = tk.Canvas(scroll_frame, bg="white", highlightthickness=0)
                scrollbar = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
                scrollable_frame = tk.Frame(canvas, bg="white")

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                # Dodanie zestawów do scrollowalnej ramki
                for set_name, set_items_list in user_sets.items():
                    set_frame = tk.LabelFrame(scrollable_frame, text=set_name, font=("Helvetica", 14), padx=10, pady=10,
                                              bg="white")
                    set_frame.pack(fill=tk.X, pady=5)

                    for set_item in set_items_list:
                        product = set_item["product"]
                        product_name = product["name"]
                        product_quantity = set_item['quantity']
                        product_label = tk.Label(set_frame, text=f"{product_name}: {product_quantity}", font=("Helvetica", 12),
                                                 bg="white")
                        product_label.pack(anchor="w", padx=5, pady=2)

                    button_frame = tk.Frame(set_frame, bg="white")
                    button_frame.pack(fill=tk.X, pady=5)

                    # Przycisk "Usuń zestaw"
                    delete_button = tk.Button(button_frame, text="Usuń", command=lambda s=set_name: self.delete_set(s))
                    delete_button.pack(side=tk.LEFT, padx=5)

                    # Przycisk "Dodaj do koszyka"
                    add_to_cart_button = tk.Button(button_frame, text="Dodaj do koszyka",
                                                   command=lambda s=set_items_list: self.add_set_to_cart(s))
                    add_to_cart_button.pack(side=tk.LEFT, padx=5)

                    # Przycisk "Zmień nazwę"
                    rename_button = tk.Button(button_frame, text="Zmień nazwę",
                                              command=lambda s=set_name: self.rename_set(s))
                    rename_button.pack(side=tk.LEFT, padx=5)

                # Przycisk zamknięcia menu
                close_button = tk.Button(self.context_menu, text="Zamknij", command=self.context_menu.destroy)
                close_button.pack(pady=10)

    def handle_mqtt_message(self, data):
        """Obsługa wiadomości MQTT."""
        if "rfid" in data:
            rfid = data["rfid"]
            self.set_current_rfid(rfid)
    def set_current_rfid(self,rfid):
        print(f"Succesfully registered rfid: {rfid}")
        self.current_rfid = rfid


"""DEBUG ONLY"""

def start_terminal_rfid_listener(kiosk_app):
    """Funkcja działająca w osobnym wątku, która nasłuchuje na RFID wpisywany w terminalu."""
    while True:
        try:
            rfid = int(input("Wprowadź kod RFID (z terminala): ").strip())
            if rfid:
                # Symuluj dane odebrane z RFID i przekazuj do aplikacji
                data = {"rfid": rfid}
                kiosk_app.handle_mqtt_message(data)
        except KeyboardInterrupt:
            print("Zatrzymano nasłuch RFID z terminala.")
            break
        except Exception as e:
            print(f"Błąd podczas nasłuchiwania RFID: {e}")


"""/DEBUG ONLY"""
def main():
    MQTT_BROKER = "10.108.33.128"
    MQTT_PORT = 1883
    MQTT_TOPIC = "rfid/read"

    # Utwórz klienta MQTT
    mqtt_client = MqttClient(MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)

    # Uruchom klienta MQTT w tle
    mqtt_client.run()

    # Utwórz połączenie z bazą danych (musisz zaimplementować klasę Database)
    db = MongoDB()
    seed(db)

    # Stwórz aplikację Tkinter (GUI)
    root = tk.Tk()
    kiosk_app = KioskApp(root, db, mqtt_client)
    threading.Thread(target=start_terminal_rfid_listener, args=(kiosk_app,), daemon=True).start()

    # Uruchom pętlę Tkintera
    try:
        root.mainloop()
    except KeyboardInterrupt:
        # Obsługa zatrzymania aplikacji
        mqtt_client.stop()
        print("Zamknięto aplikację.")
        sys.exit()


if __name__ == "__main__":
    main()
