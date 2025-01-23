from pymongo import MongoClient

class MongoDB:
    """Klasa obsługująca połączenie z MongoDB."""
    def __init__(self, uri="mongodb://localhost:27017/", db_name="kiosk_db"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.products = self.db["products"]
        self.categories = self.db["categories"]
        self.rfid_mappings = self.db["rfid_mappings"]

    def get_products_by_category(self, category):
        """Pobiera produkty z danej kategorii."""
        return list(self.products.find({"category": category}))

    def get_products(self):
        return list(self.products.find())

    def get_categories(self):
        """Pobiera unikalne kategorie produktów."""
        return list(self.categories.find())

    def add_category(self, category_id, name):
        """Dodaje nową kategorię do kolekcji."""
        self.categories.update_one(
            {"_id": category_id},
            {"$set": {"name": name}},
            upsert=True
        )



    def add_product(self, product_id, name, price,category):
        """Dodaje nowy produkt do kolekcji."""
        self.products.update_one(
            {"_id": product_id},
            {"$set": {"name": name, "price": price,"category":category}},
            upsert=True
        )

    def assign_sets_to_rfid(self, rfid, sets):
        """Przypisuje zestawy do RFID.

        Struktura:
        {
            "_id": rfid,
            "sets": {
                "Set Name": {
                    "Product 1": quantity,
                    "Product 2": quantity
                },
                ...
            }
        }
        """
        self.rfid_mappings.update_one(
            {"_id": rfid},
            {"$set": {"sets": sets}},
            upsert=True
        )

    def get_sets_by_rfid(self, rfid):
        """Pobiera zestawy przypisane do RFID."""
        l = (list(self.rfid_mappings.find()))

        mapping_list = list(self.rfid_mappings.find({"_id": rfid}))
        mapping = mapping_list[0] # nie mam pojecia czemu ja tak tu sie musze gimnastykowac nie
        if mapping and "sets" in mapping:
            return mapping["sets"]
        return {}

    def clear_all_collections(self):
        """Czyści wszystkie kolekcje w bazie danych."""
        for collection_name in self.db.list_collection_names():
            self.db[collection_name].delete_many({})
        print("Wszystkie kolekcje zostały wyczyszczone.")