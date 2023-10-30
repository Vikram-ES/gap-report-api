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
import os


config = cfg.getconfig()
PUBLIC_DATACENTER_URL = config["api"].get("public_datacenter_url", "NA")


topic_line1 = "u/60ae9143e284d016d3559dfb/GAP_GAP04.PLC04.MLD2_DATA_Anode_Geometric"
topic_line2 = "u/60ae9143e284d016d3559dfb/GAP_GAP03.PLC03.SCHENCK2_FEED_RATE"
topic_line3 ="example/result/gap"

port = 1883

client = paho.Client()

def on_log(client, userdata, obj, buff):
    print ("log:" + str(buff))


def on_connect(client, userdata, flags, rc):
    client.subscribe(topic_line1)
    client.subscribe(topic_line2)
    client.publish(topic_line3, 'Hello')
    print ("Connected!")


count1 = 0  # Initialize the global count variable
count2 = 0 
unique_timestamps1 = set()  # Create a set to store unique timestamps
unique_responses1 = []  # Create a list to store unique responses based on timestamp
unique_timestamps2 = set()  # Create a set to store unique timestamps
unique_responses2 = []  # Create a list to store unique responses based on timestamp
alertList = []


def calculation(input_df):
    df = input_df.copy()

    df = df[(df['SCHENCK2_FEED_RATE'] >= 5500) & (df['SCHENCK2_FEED_RATE'] < 6700)]
    df = df[(df['Geo_density'] >= 1.56) & (df['Geo_density'] <= 1.69)]

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')

    # Define the benchmark value
    benchmark = 1.67

    # Calculate the standard deviation of 'Geo_density'
    data = df['Geo_density'].values
    benchmark_std = np.std(data)

    print("debug.. benchmark_std", benchmark_std)

    df['z_scores'] = np.nan

    # Calculate 'z_scores' based on the benchmark and standard deviation
    if benchmark_std > 0:
        df['z_scores'] = (df['Geo_density'] - benchmark) / benchmark_std
    
    print('...............Output z scores:.............')

    print(df)
    
    if(len(df)):
        alert_time = df['timestamp'].iloc[0]

    negative_z_scores = df[df['z_scores'] < 0]

    result = {}
    
    if len(negative_z_scores) > 5:
        result = {'flag':True, 'alert_time':alert_time, 'sample': len(negative_z_scores)}
        return result
    
    return {'flag':False, 'alert_time':0, 'sample': len(negative_z_scores)}

def process_responses():
    global count1,count2, unique_responses1, unique_timestamps1, unique_responses2, unique_timestamps2
    print("count1", count1)
    print("count2", count2)
    
    if count1 >= 13:
        # print("Received 5 unique responses with unique timestamps:")
        # for response in unique_responses1:
        #     print(response)

        df1 = pd.DataFrame(unique_responses1)
        # Print the DataFrame
        # print("DataFrame for topic_line1:")
        # print(df1)
        
    if count2 >= 13:
        # print("Received 5 unique responses with unique timestamps:")
        # for response in unique_responses2:
        #     print(response)
        
        # Print the DataFrame
        df2 = pd.DataFrame(unique_responses2)
        # print("DataFrame for topic_line2:")
        # print(df2)

    if count1 >= 13 and count2 >= 13:
        merged_df = df1.merge(df2, on="timestamp", how="inner")
        print("Inner Joined DataFrame:")
        print(merged_df)

        result = calculation(merged_df)
        flag = result.get('flag')
        alert_time = result.get('alert_time')

        if not flag:
            for i in range(5):
                print("...???????.... NO! need to generate alert ......?????????....")
        elif flag:
            for i in range(5):
                print("...???????....Generate alert at time.......?????????....", alert_time)
            sendAlmEmail(result)

        

        # send_alert_request()

        count1 = 0
        unique_responses1[:] = []  # Clear the list
        unique_timestamps1 = set()  # Clear the set

        count2 = 0
        unique_responses2[:] = []  # Clear the list
        unique_timestamps2 = set()  # Clear the set

def on_message(client, userdata, message):
    global count1, count2, unique_timestamps1, unique_responses1, unique_timestamps2, unique_responses2  # Declare global variables

    incoming_msg = json.loads(message.payload)
    topic = message.topic
    # print(topic) # debug

    if topic == topic_line1:
    # Ensure that the message is a list with at least one element
        if isinstance(incoming_msg, list) and len(incoming_msg) > 0:
            data = incoming_msg[0]  # Assuming the first element contains the data

            # Extract 'r' and 't' values
            geo_density = data.get("r", None)
            timestamp = int(data.get("t", None))

            # Create a dictionary to store the values
            result = {
                "Geo_density": geo_density,
                "timestamp":timestamp
            }

            # Check if this result's timestamp is unique
            if timestamp not in unique_timestamps1:
                unique_timestamps1.add(timestamp)  # Add the timestamp to the set of unique timestamps
                unique_responses1.append(result)  # Add the response to the list of unique responses
                count1 += 1  # Increment the count variable

            process_responses()
        
    if topic == topic_line2:
    # Ensure that the message is a list with at least one element
        if isinstance(incoming_msg, list) and len(incoming_msg) > 0:
            data = incoming_msg[0]  # Assuming the first element contains the data

            # Extract 'r' and 't' values
            SCHENCK2_FEED_RATE = data.get("r", None)
            timestamp = int(data.get("t", None))

            # Create a dictionary to store the values
            result = {
                "SCHENCK2_FEED_RATE": SCHENCK2_FEED_RATE,
                "timestamp": timestamp
            }

            # Check if this result's timestamp is unique
            if timestamp not in unique_timestamps2:
                unique_timestamps2.add(timestamp)  # Add the timestamp to the set of unique timestamps
                unique_responses2.append(result)  # Add the response to the list of unique responses
                count2 += 1  # Increment the count variable

            process_responses()

def sendEmail():
    """
    Send Email 
    """
    message = '<h1>Testing Email Sending </h1>'

    try:
        url = config["api"]["meta"].replace("exactapi", "mail/send-mail")
        print("url: ", url)
        payload = json.dumps({
            "from": "vikram.k@exactspace.co",
            "to": [
                "vikramkbgs@gmail.com"
            ],
            "html": message,
            "bcc": [],
            "subject": "Testing Email Sending",
            "body": message
        })
        print("payload: ",payload)

        headers = {
            'Content-Type': 'application/json'
        }

        # response = requests.request("POST", url, headers=headers, data=payload)

        # if response.text == "Success":
        #     return "Success"
        # else:
        #     print("Error in sending mail", response.status_code)
        #     return "Fail"

    except Exception as e:
        print("Error in sending mail", e)
        return "Fail"

def send_alert_request():
    try:
        # Define the URL to which you want to send the POST request
        url = "http://127.0.0.1:5000/alert"

        # Define the data you want to send as a dictionary
        data = {
            "name": "vikram",
            "age": "23"
        }

        # Send the POST request with the provided data
        response = requests.post(url, data=data)
        
        # Check the response status code to determine success
        if response.status_code == 200:
            print("POST request was successful")
            return response.text
        else:
            print("POST request failed with status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None

def sendAlmEmail(alterArg):
    global alertList
    unitName = 'GAP'
    SiteName = 'Mahan'
    CustomerName = 'Birla-Hindalco'
    alert_time = alterArg.get('alert_time')
    alert_sample = alterArg.get('sample')

    if alert_sample >= 8:
        alertLevel = 'critical'
    else:
        alertLevel = 'warning'

    if len(alertList) < 5:
        alertList.append(alterArg)
    else:
        alertList = []

    emailTemplate = os.getcwd() + '/assets/email-template/almEmailTemplate.html'

    with open(emailTemplate, "r") as f:
        templateEmail = f.read()

    with open(os.getcwd() + '/assets/email-template/almEmailTemp.html', "w") as f1:
        f1.write(templateEmail)

    with open(os.getcwd() + '/assets/email-template/almEmailTemp.html', "r") as f2:
        s = f2.read()


    if PUBLIC_DATACENTER_URL != "NA":

        logoLink = """img src=" """ + PUBLIC_DATACENTER_URL + """pulse-files/email-logos/logo.png" """
        s = s.replace("""img src="#" """, logoLink)
    else:
        logoLink = "https://data.exactspace.co/pulse-files/email-logos/logo.png"
        s = s.replace("""img src="#" """, logoLink)        
    
    
    if str(alertLevel) == "warning":
        s = s.replace("""<td colspan="3" align="left" style="border-bottom: solid 1px #CACACA; color:yellow; padding-bottom: 5px; font-size: 15px;"><b>Alarms Active</b></td>""",
                      """<td colspan="3" align="left" style="border-bottom: solid 1px #CACACA; color:#fd7e14; padding-bottom: 5px; font-size: 15px;"><b>Alarms Active</b></td>"""
                     )
        
    if str(alertLevel) == "critical":
        s = s.replace("""<td colspan="3" align="left" style="border-bottom: solid 1px #CACACA; color:red; padding-bottom: 5px; font-size: 15px;"><b>Alarms Active</b></td>""",
                      """<td colspan="3" align="left" style="border-bottom: solid 1px #CACACA; color:#fd7e14; padding-bottom: 5px; font-size: 15px;"><b>Alarms Active</b></td>"""
                     )

    s = s.replace("UnitName", unitName)
    s = s.replace("SiteName", SiteName)
    s = s.replace("CustomerName", CustomerName)
    
    devTable = ""

    if len(alertList) > 0:                    
        devTable =  """
                    <tbody id="devList">
                    """

        for alert in alertList:
            n = 1
            try:
                devTable += """<tr>
                                <td align="center" width="40" style="border-bottom: solid 1px #CACACA;">{}</td>
                                <td align="left" style="font-size: 13px; border-bottom: solid 1px #CACACA;">{}</td>
                                <td align="left" width="100" style="font-size: 13px; border-bottom: solid 1px #CACACA;">{}</td>
                                </tr>"""\
                            .format(n,\
                                    # dev["description"].encode('ascii', 'ignore'),
                                    alert['sample'],
                                    alert['alert_time'])
                
            
            except Exception as e:
                print('error in creating table of alert',e)
                return
            n = n + 1

        s = s.replace("""<tbody id="devList">""", """<tbody id="devList">"""+devTable)
    
    else:
        print("Alarm with no open criticalTags, mail not sent!")
        return 


    with open(os.getcwd() + '/assets/email-template/almEmailTemp.html', "wb") as f:
        f.write(s.encode('utf-8'))

    with open(os.getcwd() + '/assets/email-template/almEmailTemp.html', "r") as f:
        msg_body = f.read()

    # print("BODY", type(msg_body))
    # print("msg_body", type(msg_body))


    try:
        url = config["api"]["meta"].replace("exactapi", "mail/send-mail")
        # print("url: ", url)
        payload = json.dumps({
             "from": "vikram.k@exactspace.co",
            "to": [
                "vikramkbgs@gmail.com"
            ],
            "html": msg_body,
            "bcc": [],
            "subject": "Testing Email Sending",
            "body": msg_body
        })

        # print("payload: ",payload)

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.text == "Success":
            print("Email sent to client.")
            return "Success"
        else:
            print("Error in sending mail", response.status_code)
            return "Fail"

    except Exception as e:
        print("Error in sending mail", e)
        return "Fail"

   
try:
    client.username_pw_set(username=config["BROKER_USERNAME"], password=config["BROKER_PASSWORD"])
except:
    pass
client.connect(config['BROKER_ADDRESS'], port)
# client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()

