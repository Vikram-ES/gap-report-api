import paho.mqtt.client as mqtt

# Define the MQTT broker (replace with your MQTT broker address)
broker_address = "mqtt.eclipse.org"

# Create an MQTT client
client = mqtt.Client("publisher")

# Connect to the broker
client.connect(broker_address)

# Publish a message to a topic
topic = "example_topic"
message = "Hello, MQTT!"

# Publish the message
client.publish(topic, message)

# Disconnect from the broker
client.disconnect()
