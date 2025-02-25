import paho.mqtt.client as mqtt
import json
from flask import Flask, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MQTT Variable
MQTT_TOPIC = "UNI083/GenkDijkstra/data_sensor"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

# MongoDB Connection
URI = "mongodb://masbaguss001:DJWMIyNJUKrsQWfN@cluster0-shard-00-00.haham.mongodb.net:27017,cluster0-shard-00-01.haham.mongodb.net:27017,cluster0-shard-00-02.haham.mongodb.net:27017/?replicaSet=atlas-mw8som-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0"
CLIENT = MongoClient(URI, server_api=ServerApi('1'))
DATABASE = CLIENT['ESP32']
collection = DATABASE['data_sensor']

try:
    CLIENT.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# MQTT Subscription
# Callback when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT with result code {reason_code}")
    client.subscribe(MQTT_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode()) 
        print(f"Received Message: {payload}")

        collection.insert_one(payload)
        print(f"Data inserted to MongoDB: {payload}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Flask Routing
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify(message="Welcome to IoT project developed with love by Genk Dijkstra")

@app.route("/get_data_sensor", methods=["GET"])
def get_data():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqttc.loop_start()

    return jsonify(message="Data successfully retrieved")

if __name__ == '__main__':
    app.run(debug=True)