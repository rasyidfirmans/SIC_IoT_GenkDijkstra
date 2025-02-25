from machine import Pin, ADC # type: ignore
import machine # type: ignore
import ujson # type: ignore
import network # type: ignore
import utime as time # type: ignore
import dht # type: ignore
import urequests as requests # type: ignore

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

wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print("Connecting")
    time.sleep(0.1)
print("WiFi Connected!")
print(wifi_client.ifconfig())

dht_sensor = dht.DHT11(machine.Pin(2))
pir_sensor = Pin(5, Pin.IN)
telemetry_data_old = ""

while True:
    try:
        dht_sensor.measure()
        if pir_sensor.value() == 1:
            print("Motion Detected")
        else:
            print("No Motion Detected")
    except:
        pass

    time.sleep(0.5)

    telemetry_data_new = create_json_data(dht_sensor.temperature(), dht_sensor.humidity(), pir_sensor.value())
    send_data(dht_sensor.temperature(), dht_sensor.humidity(), pir_sensor.value())

    time.sleep(0.5)