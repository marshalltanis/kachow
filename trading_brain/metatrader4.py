import socket
import json
import os
import time
import uuid
import sys
import ssl


BYTES_TO_RECEIVE = 1024

class Mt4Tick:
    time: str
    ask: str
    bid: str
    volume: str
    spread: str
    open: str
    close: str



class MT4:
    address: str
    port: int
    mt4_connect = None
    receive_buffer: list


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
        if not self.is_connected():
            print("Nothing to disconnect")
            return
        else:
            print("Closing connection")
            self.mt4_connect.close()
            self.mt4_connect = None

    def create_session(self):
        if not self.connect():
            print("Failed to create session\n")
            return
        print("Connection established with server\n")


    def receive_tick_info(self):
        data = []
        self.mt4_connect.settimeout(10)
        while True:
            try:
                data_chunk = self.mt4_connect.recv(BYTES_TO_RECEIVE)
            except socket.timeout:
                print("No data received within 10 seconds\n")
                if self.is_connected():
                    continue
                else:
                    return None
            if b'\n\r' in data_chunk:
                print(f"Received tick info from socket: {data_chunk}")
                data.append(data_chunk)
                break
            else:
                data.append(data_chunk)
        string_data = b''.join(data).decode("UTF-8")
        print(string_data)
        string_data.strip()
        symbols = string_data.split(',')
        previous_tick = Mt4Tick()
        for symbol in symbols:
            symbol.strip()
            current_field = symbol.split(':')
            setattr(previous_tick, current_field[0], current_field[1])
        return previous_tick

    def is_connected(self):
        if self.mt4_connect and self.mt4_connect.fileno != -1:
            print("Socket connected!")
            return True
        else:
            return False

    def print_stats(self):
        connection_status = "connected" if self.is_connected() else "disconnected"
        print(f"At some point, stats will be printed here. For now, the session is {connection_status}\n")