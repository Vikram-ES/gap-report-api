###########################################################
import requests
import json
import pandas as pd 
import numpy as np
import paho.mqtt.client as paho
import string
import random
import time
import app_config.app_config as cfg
import re
import messaging as mg
import shutil

config = cfg.getconfig()




unitId = 0
topic_line = "u/+/GAP_GAP04.PLC04.MLD2_DATA_Anode_Geometric"


port = 1883

client = paho.Client()

def on_log(client, userdata, obj, buff):
    print ("log:" + str(buff))


def on_connect(client, userdata, flags, rc):
    client.subscribe(topic_line)
    print ("Connected!")


count = 0  # Initialize the global count variable

def on_message(client, userdata, message):
    global count  # Declare 'count' as a global variable
    incoming_msg = json.loads(message.payload)

    # Ensure that the message is a list with at least one element
    if isinstance(incoming_msg, list) and len(incoming_msg) > 0:
        data = incoming_msg[0]  # Assuming the first element contains the data

        # Extract 'r' and 't' values
        geo_density = data.get("r", None)
        timestamp = data.get("t", None)

        # Create a dictionary to store the values
        result = {
            "Geo_density": geo_density,
            "timestamp": timestamp
        }
    else:
        # If the message is not in the expected format, set values to None
        result = {
            "Geo_density": None,
            "timestamp": None
        }

    count += 1  # Increment the count variable
    print("Response {0}: {1}".format(count, result))  # Print the response number and the message


   
try:
    client.username_pw_set(username=config["BROKER_USERNAME"], password=config["BROKER_PASSWORD"])
except:
    pass
client.connect(config['BROKER_ADDRESS'], port)
client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()

