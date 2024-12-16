import socket
import json
import os
from time import time,sleep
import uuid
import sys
import ssl

class MT4:
    address: str
    port: int
    mt4_connect = None


    def __init__(self, config:str):
        if not os.path.exists(config):
            print("Bad file path provided for config\n")
            sys.exit(2)
        with open(config, 'r') as file:
            configuration = json.load(file)
            if not configuration:
                print("Bad JSON format in config file\n")
                sys.exit(2)
            self.address = configuration['address']
            self.port = configuration['port']

    def connect(self):
        try:
            if not self.mt4_connect:
                self.mt4_connect = socket.create_connection((self.address, self.port))
                return True
        except Exception as e:
            print(f"Issue connecting to MT4 - {e}")
            return False

    def disconnect(self):
        if not self.mt4_connect:
            return
        else:
            self.mt4_connect.close()

    def create_session(self):
        if not self.connect():
            print("Failed to create session\n")
            return
        print("Connection established with server\n")

