import random

# Data for seeding
categories = [
    {"id": 1, "name": "Burgers"},
    {"id": 2, "name": "Sides"},
    {"id": 3, "name": "Beverages"},
    {"id": 4, "name": "Wraps"},
    {"id": 5, "name": "Salads"},
    {"id": 6, "name": "Desserts"}
]

product_names = {
    "Burgers": [
        {101: "Classic Burger"},
        {102: "Cheeseburger"},
        {103: "Double Burger"},
        {104: "Chicken Burger"},
        {105: "Veggie Burger"}
    ],
    "Sides": [
        {201: "Fries"},
        {202: "Onion Rings"},
        {203: "Mozzarella Sticks"},
        {204: "Chicken Nuggets"},
        {205: "Sweet Potato Fries"}
    ],
    "Beverages": [
        {301: "Cola"},
        {302: "Sprite"},
        {303: "Fanta"},
        {304: "Iced Tea"},
        {305: "Water"}
    ],
    "Wraps": [
        {401: "Chicken Wrap"},
        {402: "Veggie Wrap"},
        {403: "Beef Wrap"},
        {404: "Spicy Wrap"},
        {405: "Breakfast Wrap"}
    ],
    "Salads": [
        {501: "Caesar Salad"},
        {502: "Greek Salad"},
        {503: "Garden Salad"},
        {504: "Chicken Salad"},
        {505: "Tuna Salad"}
    ],
    "Desserts": [
        {601: "Chocolate Cake"},
        {602: "Ice Cream"},
        {603: "Brownie"},
        {604: "Cheesecake"},
        {605: "Pudding"}
    ]
}

rfid_list = [
    167405560536,
    9876543210,
    1122334455,
    9988776655,
    1231231231,
    9879879879,
    5556667778,
    4443332221,
    1112223334,
    7778889990
]

# Seeder functions
def seed_categories(db):
    """Adds categories to the database."""
    for category in categories:
        db.execute("INSERT INTO categories (category_id, name) VALUES (?, ?)", (category["id"], category["name"]))
    db.commit()

def seed_products(db):
    """Adds products to the database."""
    for category_name, items in product_names.items():
        category_id = next(cat["id"] for cat in categories if cat["name"] == category_name)
        for item in items:
            for product_id, product_name in item.items():
                price = round(random.uniform(4.99, 19.99), 2)
                db.execute(
                    "INSERT INTO products (product_id, name, price, category_id) VALUES (?, ?, ?, ?)",
                    (product_id, product_name, price, category_id)
                )
    db.commit()

def seed_sets(products, num_sets=10, min_products=2, max_products=5):
    """Generates random product sets."""
    sets = {}
    for i in range(1, num_sets + 1):
        set_name = f"Set {i}"
        num_products = random.randint(min_products, max_products)
        selected_products = random.sample(products, num_products)
        sets[set_name] = [
            {
                "product": product,
                "quantity": random.randint(1, 3)
            }
            for product in selected_products
        ]
    return sets

def generate_sets_to_rfid(sets, min_sets=1, max_sets=3):
    """Assigns random sets to RFID tags."""
    rfid_mappings = {}
    for rfid in rfid_list:
        num_sets = random.randint(min_sets, max_sets)
        selected_sets = random.sample(list(sets.keys()), num_sets)
        rfid_mappings[rfid] = {set_name: sets[set_name] for set_name in selected_sets}
    return rfid_mappings

def seed_mappings(db, rfid_mappings):
    """Seeds the RFID mappings into the database."""
    for rfid, sets_dict in rfid_mappings.items():
        db.execute("INSERT INTO rfid (rfid_id) VALUES (?)", (rfid,))
        for set_name, products in sets_dict.items():
            db.execute("INSERT INTO zestawy (zestaw_name, rfid_id) VALUES (?, ?)", (set_name, rfid))
            zestaw_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            for product_entry in products:
                product = product_entry["product"]
                quantity = product_entry["quantity"]
                db.execute(
                    "INSERT INTO product_zestaw (product_id, zestaw_id, quantity) VALUES (?, ?, ?)",
                    (product[0], zestaw_id, quantity)
                )
    db.commit()

def seed_database(db):
    """Clears the database and seeds it with categories, products, and sets."""
    db.execute("DELETE FROM product_zestaw")
    db.execute("DELETE FROM zestawy")
    db.execute("DELETE FROM rfid")
    db.execute("DELETE FROM products")
    db.execute("DELETE FROM categories")
    db.commit()

    # Seeding data
    seed_categories(db)
    seed_products(db)
    products = db.execute("SELECT product_id, name FROM products").fetchall()
    sets = seed_sets(products)
    rfid_mappings = generate_sets_to_rfid(sets)
    seed_mappings(db, rfid_mappings)
    print("Database seeded successfully!")