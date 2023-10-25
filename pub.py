import paho.mqtt.client as mqtt
import time


# Define a function to handle received data from Broker B
def handle_data_from_broker_b(client, userdata, message):
    payload = message.payload.decode()
    print(f"Received data from Broker B: {payload}")
    # Perform calculations using the received data (payload)
    # result = calculate_something(payload)
    # message = f"Response {response_number}: Calculated Result - {result}"
    # client.publish(topic, message)
    # print(f"Published message to Broker A: {message}")

# Connect to Broker B for receiving data
broker_b_address = "broker_b_address"  # Replace with the address of Broker B
data_topic = "data_topic"  # Replace with the topic from which you want to receive data
data_client = mqtt.Client("data_subscriber")
data_client.on_message = handle_data_from_broker_b
data_client.connect(broker_b_address)
data_client.subscribe(data_topic)
data_client.loop_start()








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



