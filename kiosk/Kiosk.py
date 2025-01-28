import threading
from tkinter import Tk
from kiosk_model import KioskModel
from kiosk_view import KioskView
from kiosk_controller import KioskController
from database import SQLDatabase
from seeder import seed


def start_terminal_rfid_listener(controller):
    """Function to simulate RFID input in the console."""
    while True:
        try:
            rfid = input("Enter RFID (simulation from terminal): ").strip()
            if rfid:
                # Pass the RFID to the controller
                controller.handle_rfid_input(rfid)
        except KeyboardInterrupt:
            print("RFID input listener stopped.")
            break
        except Exception as e:
            print(f"Error while listening for RFID input: {e}")


def main():
    # Initialize database and seed data
    db = SQLDatabase()
    seed(db)

    # Initialize root window
    root = Tk()

    # Initialize Model and View
    model = KioskModel(db)
    view = KioskView(root)  # Do not pass the controller here yet

    # Initialize Controller
    controller = KioskController(model, view)

    # Start RFID input listener in a separate thread
    threading.Thread(target=start_terminal_rfid_listener, args=(controller,), daemon=True).start()

    print(db.get_sets_by_rfid('1112223334'))

    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()