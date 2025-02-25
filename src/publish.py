# Please run this file on -> Thonny IDE

import network # type: ignore
import time
from machine import Pin # type: ignore
import machine # type: ignore
import dht # type: ignore
import ujson # type: ignore
from umqtt.simple import MQTTClient # type: ignore
import urequests as requests # type: ignore

# WIFI Connection
WIFI_SSID = "Galaxy A14 5G 403a"
WIFI_PASSWORD = "*$Tyuerdysr7"

print("Connecting to WiFi")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
while not sta_if.isconnected():
  print("Connecting")
  time.sleep(0.1)
print(" Connected!")

# MQTT Server Parameters
MQTT_CLIENT_ID = "UNI083_GenkDijkstra"
MQTT_BROKER = "broker.emqx.io"
MQTT_USER = "GenkDijkstra"
MQTT_PASSWORD = "PastiLolosSampaiStage4"
MQTT_TOPIC_SENSOR = "UNI083/GenkDijkstra/data_sensor"

# MQTT Server connection
print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()
print("Connected!")

# Ubiodots Parameters
DEVICE_ID = "esp32-sic"
WIFI_SSID = "Galaxy A14 5G 403a"
WIFI_PASSWORD = "*$Tyuerdysr7"
TOKEN = "BBUS-4rWaCx6yeo86ROkhRcRq8WDBtRY2Wa"

def did_receive_callback(topic, message):
    print('\n\nData Received! \ntopic = {0}, message = {1}'.format(topic, message))

def create_json_data(temperature, humidity, motion_val):
    data = ujson.dumps({
        "device_id": DEVICE_ID,
        "temperature": temperature,
        "humidity": humidity,
        "motion": motion_val,
        "type": "sensor"
    })
    return data

def send_data(temperature, humidity, motion_val):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "motion": motion_val
    }
    response = requests.post(url, json=data, headers=headers)
    print("Done Sending Data!")
    print("Response:", response.text)

# Sensor Connection
dht_sensor = dht.DHT11(machine.Pin(2))
pir_sensor = Pin(5, Pin.IN)

# Build the message in JSON format and send the message only if there is a change
prev_weather = ""
while True:
  dht_sensor.measure() 
  year, month, day, hour, minute, second, *_ = time.localtime(time.time())
  formatted_time = f"{day:02d}-{month:02d}-{year} {hour:02d}:{minute:02d}:{second:02d}"

  message = ujson.dumps({
    "timestamp": formatted_time,
    "temperature": dht_sensor.temperature(),
    "humidity": dht_sensor.humidity(),
    "motion": pir_sensor.value()
  })
  if message != prev_weather:
    print("Updated!")
    print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC_SENSOR, message))
    # Send the message
    client.publish(MQTT_TOPIC_SENSOR, message)
    prev_data = message
    # Send to Ubidots Variable
    telemetry_data_new = create_json_data(dht_sensor.temperature(), dht_sensor.humidity(), pir_sensor.value())
    send_data(dht_sensor.temperature(), dht_sensor.humidity(), pir_sensor.value())
    
  time.sleep(4)