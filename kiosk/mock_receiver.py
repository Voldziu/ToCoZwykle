
import threading

class SimulatedRFIDReader(threading.Thread):
    """Symulowany czytnik RFID działający w osobnym wątku."""
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.running = True

    def run(self):
        while self.running:
            rfid = input("Wpisz ID RFID (lub 'exit' aby zakończyć): ")
            if rfid.lower() == "exit":
                self.running = False
                break
            self.callback(rfid)

    def stop(self):
        """Zatrzymanie symulowanego wątku."""
        self.running = False