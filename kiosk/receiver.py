from PyQt6.QtCore import QObject, pyqtSignal
import paho.mqtt.client as mqtt
import json
import threading


class MqttClient(QObject):
    message_received = pyqtSignal(dict)  # Deklaracja sygnału

    def __init__(self, broker_address, port, topic):
        super().__init__()
        self.broker_address = broker_address
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.is_listening = True  # Flaga kontrolująca nasłuchiwanie RFID
        self.message = None
        self.Kiosk = None
        self.controller=None

    def setMessage(self, message):
        self.message = message

    def setKiosk(self, kiosk):
        self.kiosk = kiosk

    def setController(self,controller):
        
        self.controller = controller

    def run(self):
        # Konfiguracja klienta MQTT
        print("receiver sie lonczy")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start()  # Uruchomienie pętli MQTT w tle
            self.start_rfid_listener()  # Start osobnego wątku do nasłuchiwania RFID
        except Exception as e:
            self.message_received.emit({"error": f"Błąd połączenia: {e}"})

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.message_received.emit({"status": "Połączono z brokerem MQTT."})
            print("polaczylem sie")
            client.subscribe(self.topic)
        else:
            self.message_received.emit({"error": f"Błąd połączenia: kod {rc}"})

    def on_message(self, client, userdata, msg):
        print(msg)
        try:
            rfid = msg.payload.decode("utf-8")
            print(rfid)
            
            
            self.controller.handle_rfid_input(rfid)
           
        except json.JSONDecodeError as e:
            print("exzce")
            self.message_received.emit({"error": f"Błąd dekodowania JSON: {e}"})

    def start_rfid_listener(self):
        """Rozpoczyna nasłuchiwanie na RFID w osobnym wątku."""
        threading.Thread(target=self._rfid_listener, daemon=True).start()

    def _rfid_listener(self):
        """Nasłuchuje danych wejściowych z terminala (RFID)."""
        while self.is_listening:
            try:
                # Wczytaj dane RFID z terminala
                rfid = input("Wprowadź RFID: ").strip()
                if rfid:
                    # Symulacja danych odebranych z RFID
                    data = {"rfid": rfid, "status": "RFID odczytano"}
                    self.message_received.emit(data)  # Emit sygnału z danymi
            except Exception as e:
                self.message_received.emit({"error": f"Błąd w nasłuchiwaniu RFID: {e}"})

    def stop(self):
        """Zatrzymuje nasłuchiwanie na RFID."""
        self.is_listening = False
        self.client.loop_stop()  # Zatrzymanie pętli MQTT