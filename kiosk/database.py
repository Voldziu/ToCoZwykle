import sqlite3

class SQLDatabase:
    """Klasa obsługująca połączenie z relacyjną bazą danych (np. SQLite)."""
    def __init__(self, db_name="kiosk_db.sqlite"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Tworzy tabele, jeśli jeszcze nie istnieją."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id   INTEGER PRIMARY KEY,
                name          TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id    INTEGER PRIMARY KEY,
                name          TEXT NOT NULL,
                price         REAL NOT NULL,
                category_id   INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rfid (
                rfid_id       TEXT PRIMARY KEY
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS zestawy (
                zestaw_id     INTEGER PRIMARY KEY,
                zestaw_name   TEXT NOT NULL,
                rfid_id       TEXT NOT NULL,
                FOREIGN KEY (rfid_id) REFERENCES rfid(rfid_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_zestaw (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id    INTEGER NOT NULL,
                zestaw_id     INTEGER NOT NULL,
                quantity      INTEGER DEFAULT 1,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (zestaw_id) REFERENCES zestawy(zestaw_id)
            )
        """)
        self.connection.commit()

    # -----------------------------
    # Metody do obsługi kategorii:
    # -----------------------------
    def get_categories(self):
        """Pobiera wszystkie kategorie."""
        self.cursor.execute("SELECT category_id, name FROM categories")
        return self.cursor.fetchall()

    def add_category(self, category_id, name):
        """Dodaje nową kategorię lub aktualizuje istniejącą."""
        # Sprawdzamy czy istnieje kategoria o danym ID
        self.cursor.execute("SELECT COUNT(*) FROM categories WHERE category_id = ?", (category_id,))
        (count,) = self.cursor.fetchone()

        if count == 0:
            # INSERT
            self.cursor.execute("""
                INSERT INTO categories (category_id, name) VALUES (?, ?)
            """, (category_id, name))
        else:
            # UPDATE
            self.cursor.execute("""
                UPDATE categories
                SET name = ?
                WHERE category_id = ?
            """, (name, category_id))

        self.connection.commit()

    # ---------------------------
    # Metody do obsługi produktów:
    # ---------------------------
    def get_products(self):
        """Pobiera wszystkie produkty."""
        self.cursor.execute("SELECT product_id, name, price, category_id FROM products")
        return self.cursor.fetchall()

    def get_products_by_category(self, category_id):
        """Pobiera produkty o danej category_id."""
        self.cursor.execute("""
            SELECT product_id, name, price, category_id
            FROM products
            WHERE category_id = ?
        """, (category_id,))
        return self.cursor.fetchall()

    def add_product(self, product_id, name, price, category_id):
        """Dodaje nowy produkt lub aktualizuje istniejący."""
        self.cursor.execute("SELECT COUNT(*) FROM products WHERE product_id = ?", (product_id,))
        (count,) = self.cursor.fetchone()

        if count == 0:
            # INSERT
            self.cursor.execute("""
                INSERT INTO products (product_id, name, price, category_id)
                VALUES (?, ?, ?, ?)
            """, (product_id, name, price, category_id))
        else:
            # UPDATE
            self.cursor.execute("""
                UPDATE products
                SET name = ?, price = ?, category_id = ?
                WHERE product_id = ?
            """, (name, price, category_id, product_id))

        self.connection.commit()

    # --------------------------------------------------------
    # Metody do obsługi zestawów i RFID (wiele zestawów na 1 RFID)
    # --------------------------------------------------------
    def assign_sets_to_rfid(self, rfid, sets_dict):
        """
        Przypisuje zestawy do konkretnego rfid.
        Parametr sets_dict powinien mieć strukturę:
        {
            "Set Name": {
                "Product Name 1": quantity,
                "Product Name 2": quantity
            },
            "Inny Zestaw": {
                "Product Name X": quantity,
                ...
            }
        }
        1) Upewniamy się, że w tabeli rfid istnieje rfid_id = rfid.
        2) Dla każdego 'set_name' tworzymy/aktualizujemy wpis w 'zestawy' (z przypisanym rfid).
        3) Dla każdego produktu w zestawie tworzymy rekord w 'product_zestaw'.
        """
        # 1) Upewniamy się, że w tabeli rfid istnieje dany rfid_id
        self.cursor.execute("SELECT COUNT(*) FROM rfid WHERE rfid_id = ?", (rfid,))
        (count_rfid,) = self.cursor.fetchone()
        if count_rfid == 0:
            # Jeżeli nie ma, to wstawiamy
            self.cursor.execute("INSERT INTO rfid (rfid_id) VALUES (?)", (rfid,))

        # 2) Dla każdego zestawu (np. "Set Name") i produktów wewnątrz
        for set_name, products_map in sets_dict.items():
            # Szukamy czy już istnieje taki zestaw dla tego RFID
            self.cursor.execute("""
                SELECT zestaw_id FROM zestawy
                WHERE zestaw_name = ? AND rfid_id = ?
            """, (set_name, rfid))
            row = self.cursor.fetchone()

            if row is None:
                # Tworzymy nowy zestaw
                self.cursor.execute("""
                    INSERT INTO zestawy (zestaw_name, rfid_id)
                    VALUES (?, ?)
                """, (set_name, rfid))
                zestaw_id = self.cursor.lastrowid
            else:
                # Zestaw już istnieje
                (zestaw_id,) = row

            # 3) Dla każdego produktu w danym zestawie dodajemy wpis do product_zestaw
            print(products_map)
            for product_name, quantity in products_map[0].items():
                # Najpierw musimy znaleźć product_id po nazwie
                self.cursor.execute("""
                    SELECT product_id FROM products
                    WHERE name = ?
                """, (product_name,))
                product_row = self.cursor.fetchone()

                if product_row is None:
                    # Jeżeli produkt nie istnieje, możemy np. zignorować
                    # lub dodać go dynamicznie. Tu dla przykładu – pomijamy.
                    # Można też rzucić wyjątek, zależnie od potrzeb.
                    print(f"UWAGA: brak produktu '{product_name}' w bazie - pomijam.")
                    continue
                else:
                    (product_id,) = product_row

                # Sprawdzamy czy istnieje już wpis w product_zestaw
                self.cursor.execute("""
                    SELECT id FROM product_zestaw
                    WHERE product_id = ? AND zestaw_id = ?
                """, (product_id, zestaw_id))
                link_row = self.cursor.fetchone()

                if link_row is None:
                    # Dodajemy nowe powiązanie
                    self.cursor.execute("""
                        INSERT INTO product_zestaw (product_id, zestaw_id, quantity)
                        VALUES (?, ?, ?)
                    """, (product_id, zestaw_id, quantity))
                else:
                    # Aktualizujemy istniejące powiązanie
                    (link_id,) = link_row
                    self.cursor.execute("""
                        UPDATE product_zestaw
                        SET quantity = ?
                        WHERE id = ?
                    """, (quantity, link_id))

        # Zatwierdzamy całą transakcję
        self.connection.commit()

    def get_sets_by_rfid(self, rfid):
        """
        Zwraca słownik w strukturze:
        {
            "Set Name": {
                "Product Name": quantity,
                "Inny produkt": quantity
            },
            ...
        }
        """
        # 1) Znajdujemy wszystkie zestawy dla danego RFID
        self.cursor.execute("""
            SELECT zestaw_id, zestaw_name
            FROM zestawy
            WHERE rfid_id = ?
        """, (rfid,))
        zestawy_rows = self.cursor.fetchall()

        result = {}

        # 2) Dla każdego zestawu pobieramy produkty
        for zestaw_id, zestaw_name in zestawy_rows:
            self.cursor.execute("""
                SELECT p.name, pz.quantity
                FROM product_zestaw pz
                JOIN products p ON p.product_id = pz.product_id
                WHERE pz.zestaw_id = ?
            """, (zestaw_id,))
            product_rows = self.cursor.fetchall()

            # Tworzymy wewnętrzny słownik {product_name: quantity}
            inner_dict = {}
            for product_name, quantity in product_rows:
                inner_dict[product_name] = quantity

            result[zestaw_name] = inner_dict

        return result

    # ----------------------------
    # Czyszczenie wszystkich tabel:
    # ----------------------------
    def clear_all_tables(self):
        """Czyści wszystkie tabele w bazie danych."""
        self.cursor.execute("DELETE FROM product_zestaw")
        self.cursor.execute("DELETE FROM zestawy")
        self.cursor.execute("DELETE FROM rfid")
        self.cursor.execute("DELETE FROM products")
        self.cursor.execute("DELETE FROM categories")
        self.connection.commit()
        print("Wszystkie tabele zostały wyczyszczone.")