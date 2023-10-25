from flask import Flask, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Define the MQTT broker (use localhost for testing)
broker_address = "localhost"

# Create an MQTT client for subscription
mqtt_client = mqtt.Client("subscriber")

# Define a callback function to handle incoming messages
def on_message(client, userdata, message):
    if client.is_connected():
        payload = message.payload.decode()
        print(f"Received message: {payload}")  # Print the received message
    else:
        print("Not connected to the MQTT broker. Message not processed.")

# Set the callback function for the MQTT client
mqtt_client.on_message = on_message

# Connect to the MQTT broker
mqtt_client.connect(broker_address)
# Subscribe to the topic you want to listen to
topic = "example_topic"  # Make sure this topic matches the one used by the publisher
mqtt_client.subscribe(topic)
# Start the MQTT client loop in the background
mqtt_client.loop_start()

@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")

if __name__ == '__main__':
    app.run(debug=False)
