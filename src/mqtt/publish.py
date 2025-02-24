import network # type: ignore
import time
from machine import Pin # type: ignore
import machine # type: ignore
import dht # type: ignore
import ujson # type: ignore
from umqtt.simple import MQTTClient # type: ignore

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

# Sensor Connection
dht_sensor = dht.DHT11(machine.Pin(2))
pir_sensor = Pin(5, Pin.IN)

# Build the message in JSON format and send the message only if there is a change
prev_weather = ""
while True:
  time.sleep(5)
  dht_sensor.measure() 

  message = ujson.dumps({
    "timestamp": time.time(),
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