#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox, simpledialog
import paho.mqtt.client as mqtt
import threading
import time

# Konfiguracja MQTT
MQTT_BROKER = "10.108.33.128"
MQTT_PORT = 1883
MQTT_TOPIC = "rfid/read"
TIME_INTERVAL = 0.5

# Symulowana baza danych użytkowników
# Klucz: ID karty RFID, Wartość: Lista zestawów
USERS_DB = {
    "1234567890": [
        {"nazwa": "Zestaw 1", "skladniki": ["Burger", "Frytki", "Cola"]},
        {"nazwa": "Zestaw 2", "skladniki": ["Chicken", "Nuggets", "Sprite"]}
    ],
    "0987654321": [
        {"nazwa": "Zestaw A", "skladniki": ["Fish Burger", "Sałatka", "Woda"]},
    ]
}

class KioskApp:
    def __init__(self, master):
        self.master = master
        master.title("To co zwykle - Kiosk Samoobsługowy")

        self.current_user = None
        self.cart = []

        # GUI Elements
        self.label = tk.Label(master, text="Witaj w 'To co zwykle'!", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.card_label = tk.Label(master, text="Zeskanuj kartę RFID:", font=("Helvetica", 12))
        self.card_label.pack()

        self.sets_frame = tk.Frame(master)
        self.sets_frame.pack(pady=10)

        self.sets_label = tk.Label(self.sets_frame, text="Twoje Zestawy:", font=("Helvetica", 14))
        self.sets_label.pack()

        self.sets_listbox = tk.Listbox(self.sets_frame, width=50)
        self.sets_listbox.pack()

        self.add_button = tk.Button(master, text="Dodaj do Koszyka", command=self.add_to_cart, state=tk.DISABLED)
        self.add_button.pack(pady=5)

        self.cart_label = tk.Label(master, text="Koszyk:", font=("Helvetica", 14))
        self.cart_label.pack()

        self.cart_listbox = tk.Listbox(master, width=50)
        self.cart_listbox.pack()

        self.save_cart_button = tk.Button(master, text="Zapisz Koszyk", command=self.save_cart, state=tk.DISABLED)
        self.save_cart_button.pack(pady=5)

        # Start MQTT Client in a separate thread
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as e:
            messagebox.showerror("Błąd MQTT", f"Nie można połączyć się z brokerem MQTT: {e}")
            master.destroy()

        self.mqtt_thread = threading.Thread(target=self.client.loop_forever)
        self.mqtt_thread.daemon = True
        self.mqtt_thread.start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Połączono z brokerem MQTT")
            client.subscribe(MQTT_TOPIC)
        else:
            print("Nie udało się połączyć z brokerem MQTT")

    def on_message(self, client, userdata, msg):
        message_decoded = msg.payload.decode("utf-8")
        print(f"Odebrano komunikat o temacie: {msg.topic}: {message_decoded}")
        # Aktualizacja GUI musi być wykonana w wątku głównym
        self.master.after(0, self.handle_rfid_read, message_decoded)

    def handle_rfid_read(self, rfid_id):
        if rfid_id in USERS_DB:
            self.current_user = rfid_id
            self.cart = []
            self.update_sets_list()
            self.update_cart_list()
            self.add_button.config(state=tk.NORMAL)
            self.save_cart_button.config(state=tk.NORMAL)
            messagebox.showinfo("Karta Zeskanowana", f"Zalogowano użytkownika: {rfid_id}")
        else:
            messagebox.showwarning("Nieznana Karta", "Karta RFID nie jest zarejestrowana.")

    def update_sets_list(self):
        self.sets_listbox.delete(0, tk.END)
        if self.current_user:
            for idx, zestaw in enumerate(USERS_DB[self.current_user], start=1):
                self.sets_listbox.insert(tk.END, f"{idx}. {zestaw['nazwa']} - {', '.join(zestaw['skladniki'])}")

    def add_to_cart(self):
        selected_indices = self.sets_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Brak Wybory", "Proszę wybrać zestaw do dodania.")
            return
        for index in selected_indices:
            zestaw = USERS_DB[self.current_user][index]
            self.cart.append(zestaw)
            self.cart_listbox.insert(tk.END, f"{zestaw['nazwa']} - {', '.join(zestaw['skladniki'])}")

    def save_cart(self):
        if not self.cart:
            messagebox.showwarning("Pusty Koszyk", "Koszyk jest pusty.")
            return
        # Zapytanie o nazwę koszyka
        cart_name = simpledialog.askstring("Zapisz Koszyk", "Podaj nazwę koszyka:")
        if cart_name:
            # Sprawdzenie czy nazwa już istnieje
            existing_names = [z['nazwa'] for z in USERS_DB[self.current_user]]
            if cart_name in existing_names:
                overwrite = messagebox.askyesno("Nadpisz", "Koszyk o tej nazwie już istnieje. Czy chcesz go nadpisać?")
                if overwrite:
                    for zestaw in USERS_DB[self.current_user]:
                        if zestaw['nazwa'] == cart_name:
                            zestaw['skladniki'] = [item for z in self.cart for item in z['skladniki']]
                            break
                    messagebox.showinfo("Zapisano", "Koszyk został nadpisany.")
            else:
                # Dodanie nowego koszyka
                USERS_DB[self.current_user].append({
                    "nazwa": cart_name,
                    "skladniki": [item for z in self.cart for item in z['skladniki']]
                })
                messagebox.showinfo("Zapisano", "Koszyk został zapisany.")
            self.update_sets_list()

    def update_cart_list(self):
        self.cart_listbox.delete(0, tk.END)
        for zestaw in self.cart:
            self.cart_listbox.insert(tk.END, f"{zestaw['nazwa']} - {', '.join(zestaw['skladniki'])}")

def main():
    root = tk.Tk()
    app = KioskApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
