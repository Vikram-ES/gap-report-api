import paho.mqtt.client as mqtt
import time

# Define the MQTT broker (use localhost for testing)
broker_address = "localhost"

# Create an MQTT client
client = mqtt.Client("publisher")

# Connect to the broker
client.connect(broker_address)

# Publish a message to a topic every 10 seconds
topic = "example_topic"
response_number = 1  # Initialize the response number

while True:
    message = f"Response {response_number}: Hello, MQTT!"
    client.publish(topic, message)
    print(f"Published message: {message}")
    response_number += 1  # Increment the response number
    time.sleep(10)  # Wait for 10 seconds before publishing the next message

# Disconnect from the broker (This will never be reached in this code)
client.disconnect()
