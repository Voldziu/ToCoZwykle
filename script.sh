#!/bin/bash

echo "Installing paho-mqtt..."
pip3 install paho-mqtt

echo "Installing Mosquitto and Mosquitto clients..."
sudo apt update
sudo apt install -y mosquitto mosquitto-clients

echo "Starting Mosquitto service..."
sudo systemctl start mosquitto.service

echo "Modifying Mosquitto configuration..."

# Check if 'allow_anonymous true' already exists, and add it if not
if ! grep -q "allow_anonymous true" /etc/mosquitto/mosquitto.conf; then
    sudo bash -c "echo 'allow_anonymous true' >> /etc/mosquitto/mosquitto.conf"
fi

# Check if 'listener 1883 0.0.0.0' already exists, and add it if not
if ! grep -q "listener 1883 0.0.0.0" /etc/mosquitto/mosquitto.conf; then
    sudo bash -c "echo 'listener 1883 0.0.0.0' >> /etc/mosquitto/mosquitto.conf"
fi

echo "Restarting Mosquitto service..."
sudo systemctl restart mosquitto.service

echo "Setup complete. Mosquitto is running and configured."