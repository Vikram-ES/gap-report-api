from flask import Flask, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name)

# Define the MQTT broker (replace with your MQTT broker address)
broker_address = "mqtt.eclipse.org"

# Create an MQTT client for subscription
mqtt_client = mqtt.Client("subscriber")

# Define a callback function to handle incoming messages
def on_message(client, userdata, message):
    payload = message.payload.decode()
    print(f"Received message: {payload}")

# Set the callback function for the MQTT client
mqtt_client.on_message = on_message

# Connect to the MQTT broker
mqtt_client.connect(broker_address)
# Subscribe to the topic you want to listen to
mqtt_client.subscribe("example_topic")
# Start the MQTT client loop in the background
mqtt_client.loop_start()

@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")

if __name__ == '__main__':
    app.run(debug=True)
