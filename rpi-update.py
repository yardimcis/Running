#!/usr/bin/python

from argparse import ArgumentParser

import xml.etree.ElementTree as ET
import re
import sys
import os
import shutil
import uuid
import subprocess

def get_system_info():
    #Kernel version
    kernel = subprocess.check_output(['uname','-r'])
    #Mac address 
    interface = subprocess.check_output(['ifconfig','eth0'])
    mac_address = re.search('HWaddr',interface)
    Mac_ID = interface[mac_address.end():][1:18]
    ip_address = re.search('inet',interface)
    IP_address = interface[ip_address.end():][1:15]
    return kernel,Mac_ID,IP_address

def get_Serial_ID(kernel):
    if kernel == "4.0.8-v7\n":
        Network_file = ET.parse("/opt/Engine/Settings/Network.xml")
        N_root = Network_file.getroot()
        Network = N_root.find('Network')
        Sender = Network.find('Sender')
        Serial_ID = Sender.find('CustomerID').text + Sender.find('DeviceID').text
        return Serial_ID
    elif kernel == "4.4.9-v7+\n":
        Environment_file = ET.parse("/opt/Engine/Settings/Environment.xml")
        E_root = Environment_file.getroot()
        Device = E_root.find('Device')
        Serial = Device.find('SerialID')
        Serial_ID = Serial.find('CustomerID').text + Serial.find('DeviceID').text
        return Serial_ID
    else :
        return 0

def get_Engine():
    links = subprocess.check_output('ls -al /opt/ | grep ^l', shell=True)
    engine = re.search('Engine ->',links)
    old_engine = links[engine.end():][1:12]
    return old_engine

def erase_old_engine(old_engine):
    subprocess.call(['rm','-r','3g','ReadME','TimeSync','WiFiSatellite','WiFiSlave','lib'])
    subprocess.call('mv /opt/{old_engine} /opt/OldEngine', shell=True)

def clean_up():
    subprocess.call('rm /var/log/*', shell=True)

def parse_xml(Serial_ID,Mac_ID,Version_ID, address='192.168.1.241',device=0):
    #Parse XML files
    Network_file = ET.parse("/opt/Engine/Settings/Network.xml")
    Environment_file = ET.parse("/opt/Engine/Settings/Environment.xml")
    WebServer_file = ET.parse("/opt/Engine/Settings/WebServer.xml")
    W_root = WebServer_file.getroot()
    N_root = Network_file.getroot()
    E_root = Environment_file.getroot()
    if Version_ID  == "4.0.8-v7\n":
        #Customer ID and Device ID correction
        Network = N_root.find('Network')
        Sender = Network.find('Sender')
        Sender.find('CustomerID').text=Serial_ID[0:6]
        Sender.find('DeviceID').text=Serial_ID[6:]

        #IP Address correction
        BootArgs = E_root.find('BootArgs')
        DefaultNetworkParams = BootArgs.find('DefaultNetworkParams')
        DefaultNetworkParams.find('IP').text = address
        if address[8] == "1":
            DefaultNetworkParams.find('Gateway').text = "192.168.1.1"
            DefaultNetworkParams.find('Netmask').text = "255.255.255.0"
        elif address[8] == "2":
            DefaultNetworkParams.find('Gateway').text = "192.168.2.1"
            DefaultNetworkParams.find('Netmask').text = "255.255.255.0"
        else:
            print("IP address does not match please check the correct address")

        #Mac address correction
        DefaultNetworkParams.find('Mac').text = Mac_ID

        #MQQT Correction
        mqtt = N_root.find('MQTT')
        mqtt.find('IsActive').text = "1"
        mqtt.find('ServerURI').text = "85.111.53.134:1883"
        mqtt.find('Username').text = "_key_535199912233292681"
        mqtt.find('Password').text = "3f5aa9fe100d4e2282acbae9492ab78b"
        mqtt.find('QoS').text = "2"

        return Network_file,Environment_file

    elif Version_ID == "4.4.9-v7+\n":
        #Customer ID and Device ID correction
        Device = E_root.find('Device')
        SerialID = Device.find('SerialID')
        SerialID.find('CustomerID').text=Serial_ID[0:6]
        SerialID.find('DeviceID').text=Serial_ID[6:]

        #Default Network Correction
        BootArgs = E_root.find('BootArgs')
        DefaultNetworkParams = BootArgs.find('DefaultNetworkParams')
        DefaultNetworkParams.find('IP').text = address
        DefaultNetworkParams.find('Gateway').text = "192.168.1.1"
        DefaultNetworkParams.find('Netmask').text = "255.255.255.0"

        #Mac address correction
        DefaultNetworkParams.find('Mac').text=Mac_ID

        #MQQT Correction
        mqtt = N_root.find('MQTT')
        mqtt.find('IsActive').text = "1"
        mqtt.find('EnableACK').text = "0"
        mqtt.find('EnableSSL').text = "0"
        mqtt.find('UseSerialIDAsClientID').text = "0"
        mqtt.find('ServerURI').text = "85.111.53.134:1883"
        mqtt.find('Username').text = "_key_535199912233292681"
        mqtt.find('Password').text = "3f5aa9fe100d4e2282acbae9492ab78b"
        mqtt.find('QoS').text = "2"
        mqtt_cloud = mqtt.find('Cloud')
        mqtt_cloud.find('EnableACK').text = "0"
        mqtt_cloud.find('UseSerialIDAsClientID').text = "0"

        return Network_file,Environment_file
    
    else:
        return 0

#Serial_ID = sys.argv[1]
def main():
    ap = ArgumentParser()
    ap.add_argument('-v', '--version', type=int, help='Enter version 0 is Rpi-2, 1 is Rpi-3 oldcase, 2 is Rpi-3 Alpha')
    ap.add_argument('-s', '--serial', type=str, default='00010002', help='use Serial ID to re-configure xml files')
    ap.add_argument('-i', '--address', default=0, help='set given IP address for second or third device')
    ap.add_argument('-p', '--port', default=12100 , help='set starting port number for second or third device it reserve ten port for device')
    ap.add_argument('-u', '--update', help='update current engine')
    args = ap.parse_args()

    
    

    version,Mac_ID,IP_address = get_system_info()
    Serial_ID = get_Serial_ID(version)
    current_engine = get_Engine()
    Network_file, Environment_file = parse_xml(Serial_ID,Mac_ID,version)



    print("CustomerID : "+Serial_ID[0:6])
    print("DeviceID : "+Serial_ID[6:])
    print("Mac Adress : "+Mac_ID)
    print("Kernel version : "+version)
    print("Current Engine version : "+current_engine)


    question = raw_input("Continue ? y(yes)/n(no) : ")

    if question == 'y'or question == 'yes':
        print("Stopping CommonEngine service...")
        subprocess.call('services CommonEngine stop',shell=True)
        print("Environment and Network variables writing...done!")
        #writing files
        Network_file.write("/opt/Engine/Settings/Network.xml")
        Environment_file.write("/opt/Engine/Settings/Environment.xml")
    else :
        print("exit.")

if __name__ == "__main__":
    main()