class KioskModel:
    """Model responsible for managing data logic."""

    def __init__(self, db):
        self.db = db

    def get_categories(self):
        """Fetches categories from the database."""
        return self.db.get_categories()

    def get_products_by_category(self, category):
        """Fetches products for a specific category."""
        return self.db.get_products_by_category(category)

    def get_sets_by_rfid(self, rfid):
        """Fetches user sets by RFID."""
        return self.db.get_sets_by_rfid(rfid)
    
    