#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
from config import *  
from mfrc522 import MFRC522
import paho.mqtt.client as mqtt
import json
client = mqtt.Client()

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "rfid/read"
TIME_INTERVAL = 0.5
class RFID():

    def __init__(self,reader):
        self.reader= reader
    
    def read(self):
        (status, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        if status == self.reader.MI_OK:
            (status, uid) = self.reader.MFRC522_Anticoll()
            if status == self.reader.MI_OK:
                 return self.uid_to_int(uid)
        return None    
                

    def uid_to_int(self,uid:list):
        return int("".join(f"{x:02X}" for x in uid),16)
    

def beep_and_blink():
    GPIO.output(buzzerPin,GPIO.LOW)
    GPIO.output(led1,GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(buzzerPin,GPIO.HIGH)
    GPIO.output(led1,GPIO.HIGH)


def main():
    
    reader = MFRC522()
    rfid = RFID(reader)

    
    try:
        client.connect(MQTT_BROKER,MQTT_PORT,60)
        client.loop_start()
        previous_read_timestamp = time.time()
        previous_rfid = None
        while True:
            rfid_read = rfid.read()
            
            current_rfid = rfid_read
            current_timestamp = time.time()
            if rfid_read:
                if current_timestamp - previous_read_timestamp> TIME_INTERVAL or current_rfid != previous_rfid:
                    message = f"{rfid_read}"

                    client.publish(MQTT_TOPIC,message)
                    print(f"Opublikowano {message}")

                    beep_and_blink()
                    #print(f"previous: {previous_rfid}, current: {current_rfid}")
            
                previous_read_timestamp= time.time()
                previous_rfid = current_rfid
            

    except KeyboardInterrupt:
        print("zatrzymano program")

    finally:
        client.loop_stop()
        GPIO.cleanup()



if __name__ == "__main__":
    
    main()

    