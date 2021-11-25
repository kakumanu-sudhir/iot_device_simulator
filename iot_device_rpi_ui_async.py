#!/usr/bin/env python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START iot_mqtt_includes]
import argparse
import datetime
import logging
import os
import random
import ssl
import time

import jwt
import paho.mqtt.client as mqtt
# [END iot_mqtt_includes]

import json
import math
import numpy
from collections import OrderedDict
import sys
import psutil
from bluetooth import *
from tkinter import *
import time
import csv
import traceback
import asyncio
import threading

with open('config.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cloud_region = row['cloud_region']
        num_messages=row['num_messages']
        project_id=row['project_id']
        device_id=row['device_id']
        dev_lat=row['dev_lat']
        dev_long=row['dev_long']
        bt_addr=row['bt_addr']

# print(cloud_region)
# print(num_messages)
# print(project_id)
# print(device_id)
# print(dev_lat)
# print(dev_long)

build_date = datetime.date(2021,11,20)
today = datetime.date.today()
diff = today-build_date
remaining_days = diff.days
to_detect = True
Error_response = -1

# The initial backoff time after a disconnection occurs, in seconds.
minimum_backoff_time = 1

# The maximum backoff time before giving up, in seconds.
MAXIMUM_BACKOFF_TIME = 3#32

# Whether to wait with exponential backoff before publishing.
should_backoff = False

bt_data_xfer = False

# [START iot_mqtt_jwt]
def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
        Args:
         project_id: The cloud project ID this device belongs to
         private_key_file: A path to a file containing either an RSA256 or
                 ES256 private key.
         algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
        Returns:
            A JWT generated from the given project_id and private key, which
            expires in 20 minutes. After 20 minutes, your client will be
            disconnected, and a new JWT will have to be generated.
        Raises:
            ValueError: If the private_key_file does not contain a known key.
        """

    token = {
            # The time that the token was issued at
            'iat': datetime.datetime.utcnow(),
            # The time the token expires.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=20),
            # The audience field should always be set to the GCP project id.
            'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
            algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)
# [END iot_mqtt_jwt]


# [START iot_mqtt_config]
def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', mqtt.connack_string(rc))

    # After a successful connect, reset backoff time and stop backing off.
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))

    # Since a disconnect occurred, the next loop iteration will wait with
    # exponential backoff.
    global should_backoff
    should_backoff = True


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print('on_publish')


def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload.decode('utf-8'))
    print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id, cloud_region, registry_id, device_id)
    print('Device client_id is \'{}\''.format(client_id))

    client = mqtt.Client(client_id=client_id)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # The topic that the device will receive commands on.
    mqtt_command_topic = '/devices/{}/commands/#'.format(device_id)

    # Subscribe to the commands topic, QoS 1 enables message acknowledgement.
    print('Subscribing to {}'.format(mqtt_command_topic))
    client.subscribe(mqtt_command_topic, qos=0)

    return client
# [END iot_mqtt_config]


def detach_device(client, device_id):
    """Detach the device from the gateway."""
    # [START iot_detach_device]
    detach_topic = '/devices/{}/detach'.format(device_id)
    print('Detaching: {}'.format(detach_topic))
    client.publish(detach_topic, '{}', qos=1)
    # [END iot_detach_device]


def attach_device(client, device_id, auth):
    """Attach the device to the gateway."""
    # [START iot_attach_device]
    attach_topic = '/devices/{}/attach'.format(device_id)
    attach_payload = '{{"authorization" : "{}"}}'.format(auth)
    client.publish(attach_topic, attach_payload, qos=1)
    # [END iot_attach_device]

def input_and_send():
    print("\nType something\n")
    try:
        while True:
            data = input()
            if len(data) == 0: 
                break
            sock.send(data)
            sock.send("\n")
    except Exception as err:
        print(err)
        
def rx_and_echo(sock):
    sock.send("\nsend anything\n")
    try:
        while True:
            data = sock.recv(buf_size)
            if data:
                print(data)
                sock.send(data)
    except Exception as err:
        print(err)

def setup_bt_conn(addr):
    #uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    #service_matches = find_service( uuid = uuid, address = addr )
    print("setup_bt_conn")
    service_matches = find_service( address = addr )
    if len(service_matches) == 0:
        print("couldn't find the SampleServer service =(, Bluetooth issue")
        return 0

    for s in range(len(service_matches)):
        print("\nservice_matches: [" + str(s) + "]:")
        print(service_matches[s])
        
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    port=1
    print("connecting to \"%s\" on %s, port %s" % (name, host, port))

    # Create the client socket
    sock=BluetoothSocket(RFCOMM)
    sock.connect((host, port))

    print("connected")

    return sock

def mqtt_device(args, points, sock):
    """Connects a device, sends data, and receives data."""
    print("mqtt_device")
    # [START iot_mqtt_run]
    global minimum_backoff_time
    global MAXIMUM_BACKOFF_TIME
    global to_detect
    
    # Publish to the events or state topic based on the flag.
    sub_topic = 'events' if args['message_type'] == 'event' else 'state'

    mqtt_topic = '/devices/{}/{}'.format(args['device_id'], sub_topic)

    jwt_iat = datetime.datetime.utcnow()
    jwt_exp_mins = args['jwt_expires_minutes']
    client = get_client(
        args['project_id'], args['cloud_region'], args['registry_id'],
        args['device_id'], args['private_key_file'], args['algorithm'],
        args['ca_certs'], args['mqtt_bridge_hostname'], args['mqtt_bridge_port'])

    buf_size = 1024;
    # 1: NoLeak, 2: Leak, 3: SensorOffline
    gas_sensor_status = 1

    try:
        sock.send("\n Initiat BT start data \n")
    except Exception as err:
        gas_sensor_status = 3

    # Publish num_messages messages to the MQTT bridge once per second.
    for i in range(1, args['num_messages'] + 1):

        if to_detect == True:
            # Process network events.
            client.loop()

            # Wait if backoff is required.
            if should_backoff:
                # If backoff time is too large, give up.
                if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                    print('Exceeded maximum backoff time. Giving up.')
                    break

                # Otherwise, wait and connect again.
                delay = minimum_backoff_time + random.randint(0, 20) / 20.0
                print('Waiting for {} before reconnecting.'.format(delay))
                time.sleep(delay)
                minimum_backoff_time += 2
                client.connect(args['mqtt_bridge_hostname'], args['mqtt_bridge_port'])

            
            max_coords = len(points)
            cur_index = i+1 if i+1 < max_coords else max_coords-1
            lat = points[cur_index][0]
            longitude = points[cur_index][1]
            
            #curr_cpu_temp = psutil.sensors_temperatures()['cpu_thermal'][0][1]

            try:
                data = sock.recv(buf_size)
                if data:
                    if(str(data).lower().find('gas leakage') != -1):
                        gas_sensor_status = 2
                    elif(str(data).lower().find('no gas') != -1):
                        gas_sensor_status = 1
                    sock.send(data)
            except Exception as err:
                gas_sensor_status = 3
            
            c_dt = datetime.datetime.now()
            # payload = '{}/{}-{}-{}-{}'.format(args['registry_id'], args['device_id'], lat, longitude, i) # Publishing message 100/1000: 'iotlab-registry/tempDevice-12.91833-77.62187-100'
            #payload = {"time_stamp": time.asctime( time.localtime(time.time())),"registry":args['registry_id'] , "device": args['device_id'], "latitude": lat, "longitude": longitude, "gas_sensor_status": gas_sensor_status}                
            payload = {"time_stamp": c_dt.strftime("%Y-%m-%d %H:%M:%S"),"registry":args['registry_id'] , "device": args['device_id'], "latitude": lat, "longitude": longitude, "gas_sensor_status": gas_sensor_status}
            print('Publishing message {}/{}: \'{}\''.format(i, args['num_messages'], payload))

            # [START iot_mqtt_jwt_refresh]
            seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
            if seconds_since_issue > 4 * jwt_exp_mins:
                print('Refreshing token after {}s'.format(seconds_since_issue))
                jwt_iat = datetime.datetime.utcnow()
                client.loop()
                client.disconnect()
                client = get_client(
                    args['project_id'], args['cloud_region'],
                    args['registry_id'], args['device_id'], args['private_key_file'],
                    args['algorithm'], args['ca_certs'], args['mqtt_bridge_hostname'],
                    args['mqtt_bridge_port'])
            # [END iot_mqtt_jwt_refresh]
            # Publish "payload" to the MQTT topic. qos=1 means at least once
            # delivery. Cloud IoT Core also supports qos=0 for at most once
            # delivery.
            client.publish(mqtt_topic, json.dumps(payload), qos=1)

            # Send events every second. State should not be updated as often
            for i in range(0, 2):
                time.sleep(0.1)
                client.loop()
            
            if gas_sensor_status == 3:
                try:
                    print(" BT reconnection attempt ")
                    sock = setup_bt_conn(args['bt_addr'])
                except:
                    print(" BT reconnection attempt failure ")
        else:
            print("detection stopped")
            break

    # [END iot_mqtt_run]


def sensor_detection(limit):
    print("sensor_detection ")
    #args = parse_command_line_args()    
    if limit < 1:
        print("root authentication passed")
        pass
    else:
        print("root authentication issue")
        return

    kphb_lat = round(float(dev_lat), 5)
    kpbh_long = round(float(dev_long), 5)

    coords = []
    coords.append((kphb_lat, kpbh_long))

    #print(coords)
    args = {'algorithm': 'RS256', 
            'ca_certs': 'roots.pem', 
            'cloud_region': cloud_region, 
            'data': 'Hello there', 
            'device_id': device_id,
            'gateway_id': None, 
            'jwt_expires_minutes': 20, 
            'listen_dur': 60, 
            'message_type': 'event', 
            'mqtt_bridge_hostname': 'mqtt.googleapis.com', 
            'mqtt_bridge_port': 8883,
            'num_messages': int(num_messages), 
            'private_key_file': 'rsa_private.pem', 
            'project_id': project_id, 
            'registry_id': 'iotlab-registry', 
            'service_account_json': None, 
            'command': None,
            'bt_addr':bt_addr} 
    
    #MAC address of ESP32
    #addr = "80:7D:3A:C5:02:6A"

    try:
        sock = setup_bt_conn(bt_addr)
    except Exception as err:
        print("Bluetooth connection failed, check device power")
        print(err)
        print(traceback.print_stack())
        print('Process Finished.')
        return Error_response

    try:
        mqtt_device(args, coords, sock)
    except Exception as err:
        print("Detection failed")
        print(err)
        print(traceback.print_stack())
        print('Process Finished.')
        return Error_response
    
    to_detect = True

    print('Process Finished.')
    return 0

# def myFunction(configlabel): #Device Configuration
#     configlabel.config(text='Button pressed')
#     print("myFunction")
#     i = 0
#     while i<0xfffffff:
#         i=i+1

#     #configlabel.config(text='Device info entered is:'+str(dataRegion.get()+str(dataProjectID.get()+str(dataDeviceID.get()+str(dataNumberofMessages.get())))))
#     configlabel.config(text='Button processing done')
#     return


async def start_fn(configlabel): #Device Configuration
    print("start_fn")
    configlabel.config(text='Detection Started!')    
    global to_detect
    to_detect = True
    resp = sensor_detection(remaining_days)
    await asyncio.sleep(1)
    if resp ==0:
        configlabel.config(text='Detection done!')
    else:
        configlabel.config(text='Detection Failed!')
    print("start_fn done")

def _asyncio_thread(async_loop, configlabel):
    print("_asyncio_thread")
    try:
        async_loop.run_until_complete(start_fn(configlabel))
    except Exception as err:
        print("_asyncio_thread stop")
        print(err)
        # print(traceback.print_stack())

    # finally:
    #     async_loop.close()

    print("_asyncio_thread done")


def do_tasks(async_loop, configlabel):
    """ Button-Event-Handler starting the asyncio part. """
    print("do_tasks")
    worker = threading.Thread(target=_asyncio_thread, args=(async_loop,configlabel, ))
    worker.start()
    # async_loop.run_until_complete(start_fn(configlabel))
    print("do_tasks done")

def stop_fn(async_loop, configlabel):
    global to_detect
    to_detect = False
    async_loop.stop()
    # async_loop.close()
    # async_loop.run_until_complete(async_loop.shutdown_asyncgens())
    configlabel.config(text='Detection Stopped!')

def main(async_loop):
    window=Tk()
    window.title("Device Config Tool")
    window.geometry('600x400')

    #button1=Button(window,text='Register Device', fg="#263D75", font=('Arial',14))
    #button1.grid(row=0, column=1, sticky=E)


    lable1=Label(window, text= 'Region Name', fg='blue', bg='white', font=('Arial',14))
    lable1.grid(row=1, column=1, padx=5, pady=10)
            
    dataRegion=StringVar()#Region name entry data type

    textbox1=Entry(window, textvariable=dataRegion, fg='black', font=('Arial',14))
    textbox1.grid(row=1, column=2)

    lable2=Label(window, text= 'Project ID', fg='blue', bg='white', font=('Arial',14))
    lable2.grid(row=2, column=1, padx=5, pady=10)

    dataProjectID=StringVar()#Project ID name entry data type

    textbox2=Entry(window,textvariable=dataProjectID, fg='black', font=('Arial',14))
    textbox2.grid(row=2, column=2)

    lable3=Label(window, text= 'Device ID', fg='blue', bg='white', font=('Arial',14))
    lable3.grid(row=3, column=1, padx=5, pady=10)

    dataDeviceID=StringVar()#Device ID name entry data type

    textbox3=Entry(window, textvariable=dataDeviceID, fg='black', font=('Arial',14))
    textbox3.grid(row=3, column=2)

    lable4=Label(window, text= 'Number of Messages', fg='blue', bg='white', font=('Arial',14))
    lable4.grid(row=4, column=1, padx=5, pady=10)

    dataNumberofMessages=StringVar()#Number of messages to be output by edge sensor

    textbox4=Entry(window, textvariable=dataNumberofMessages, fg='black', font=('Arial',14))
    textbox4.grid(row=4, column=2)

    dataRegion.set(cloud_region)
    dataProjectID.set(project_id)
    dataDeviceID.set(device_id)
    dataNumberofMessages.set(num_messages)

    configlabel=Label(window, fg='purple',font=('Arial',14))
    configlabel.grid(row=6, column=1, sticky=W, pady=10)
    
    #button2=Button(window, text='Start Detection', command=lambda:myFunction(configlabel), bg='blue', fg="yellow", font=('Arial',14))
    button2=Button(window, text='Start Detection', command=lambda:do_tasks(async_loop, configlabel), bg='blue', fg="yellow", font=('Arial',14))
    button2.grid(row=5, column=1, sticky=E)
    # button2.pack()

    button3=Button(window, text='Stop Detection', command=lambda:stop_fn(async_loop, configlabel), bg='blue', fg="yellow", font=('Arial',14))
    button3.grid(row=5, column=2, sticky=E)

    window.mainloop()


if __name__ == '__main__':
    async_loop = asyncio.get_event_loop()
    main(async_loop)
    



