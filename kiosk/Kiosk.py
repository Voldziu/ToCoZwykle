import threading
from tkinter import Tk
from kiosk_model import KioskModel
from kiosk_view import KioskView
from kiosk_controller import KioskController
from receiver import MqttClient


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

    MQTT_BROKER = "10.108.33.128"
    MQTT_PORT = 1883
    MQTT_TOPIC = "rfid/read"
    TIME_INTERVAL = 0.5
    # Initialize root window
    root = Tk()

    # Initialize Model and View
    model = KioskModel()
    view = KioskView(root)  # Do not pass the controller here yet
    receiver = MqttClient(MQTT_BROKER,MQTT_PORT,MQTT_TOPIC)
    receiver.run()
    # Initialize Controller
    controller = KioskController(model, view)
    receiver.setController(controller=controller)

    # Start RFID input listener in a separate thread
    threading.Thread(target=start_terminal_rfid_listener, args=(controller,), daemon=True).start()

    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()