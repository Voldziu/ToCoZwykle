import sqlite3

DB_NAME = "kiosk_db.sqlite"

def get_db():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id   INTEGER PRIMARY KEY,
            name          TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id    INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            price         REAL NOT NULL,
            category_id   INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfid (
            rfid_id       TEXT PRIMARY KEY
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zestawy (
            zestaw_id     INTEGER PRIMARY KEY,
            zestaw_name   TEXT NOT NULL,
            rfid_id       TEXT NOT NULL,
            FOREIGN KEY (rfid_id) REFERENCES rfid(rfid_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_zestaw (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id    INTEGER NOT NULL,
            zestaw_id     INTEGER NOT NULL,
            quantity      INTEGER DEFAULT 1,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (zestaw_id) REFERENCES zestawy(zestaw_id)
        )
    """)
    connection.commit()
    connection.close()