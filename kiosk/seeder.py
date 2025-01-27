import random
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
    163425166062,
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

def seed_products(db):

    for category, items in product_names.items():
        for item in items:

            for product_id,product_name in item.items():

                price = round(random.uniform(4.99, 19.99), 2)  # Generujemy losową cenę

                db.add_product(product_id, product_name, price, category)
                product_id += 1

def seed_categories(db):
    for category in categories:
        id = category["id"]
        name = category["name"]

        db.add_category(id,name)



def seed_sets( products, num_sets=10, min_products=2, max_products=5):
    """
    Generuje zestawy produktów na podstawie kategorii i produktów.

    :param categories: Lista słowników z kategoriami (zawierających id i name).
    :param product_names: Słownik z produktami w każdej kategorii.
    :param num_sets: Liczba zestawów do wygenerowania.
    :param min_products: Minimalna liczba produktów w zestawie.
    :param max_products: Maksymalna liczba produktów w zestawie.
    :return: Słownik z zestawami.
    """
    sets = {}

    for i in range(1, num_sets + 1):
        set_name = f"Set {i}"  # Unikalna nazwa zestawu
        num_products = random.randint(min_products, max_products)  # Liczba produktów w zestawie

        # Wybierz losowe kategorie i produkty
        selected_products = {}
        set_list=[]
        for _ in range(num_products):
            product = random.choice(products)  # Wybierz losowy produkt
            print(product)
            product_name = product[1]

            # Dodaj produkt do zestawu (jeśli jeszcze go nie ma)
            if product_name not in selected_products:
                set_list.append( {
                    "product": product,  # Cały obiekt produktu
                    "quantity": random.randint(1, 3)  # Ilość produktu (1-3)
                })

        # Dodaj zestaw do wynikowego słownika
        sets[set_name] = set_list

    return sets


def generate_sets_to_rfid(sets,rfid_list=rfid_list , min_sets=1, max_sets=3):
    """
    Przypisuje zestawy do RFID.

    :param rfid_list: Lista RFID.
    :param sets: Słownik zestawów (wygenerowany wcześniej).
    :param min_sets: Minimalna liczba zestawów na RFID.
    :param max_sets: Maksymalna liczba zestawów na RFID.
    :return: Słownik mapujący RFID na zestawy.
    """
    rfid_mappings = {}

    for rfid in rfid_list:
        # Liczba zestawów przypisanych do danego RFID
        num_sets = random.randint(min_sets, max_sets)

        # Losowy wybór zestawów
        selected_sets = random.sample(list(sets.keys()), num_sets)

        # Przypisanie zestawów do RFID
        rfid_mappings[rfid] = {set_name: sets[set_name] for set_name in selected_sets}
    print(rfid_mappings)

    return rfid_mappings

def seed_mappings(db,rfid_mappings):
    for rfid,sets_dict in rfid_mappings.items():
        db.assign_sets_to_rfid(rfid,sets_dict)




def seed(db):
    db.clear_all_tables()
    seed_categories(db)
    seed_products(db)

    products = db.get_products()


    sets = seed_sets(products)
    generated_sets_with_rfid = generate_sets_to_rfid(sets)
    seed_mappings(db,generated_sets_with_rfid)