import json
import os
import asyncio
import websocket as ws
from time import time
import uuid
from utils import logger
import sys
from time import sleep
import ssl


class IgUsa:
    def __init__(self, config:str):
        self.config = config
        self.logger = logger.logger()
        self.logger.info("Creating API")
        self.__parse_config()
        ws.enableTrace(True)
        self.pt_ws = ws.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.trade_ws = ws.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.pt_ws.connect(url=self.pretrade)
        self.trade_ws.connect(url=self.trade)
        self.session_id= uuid.uuid4()
    
    def __parse_config(self):
        if not os.path.exists(self.config):
            self.logger.error("Path doesn't exist")
            raise FileNotFoundError
        with open(self.config) as file:
            urls = json.load(file)
            self.pretrade = urls["pretrade"]
            self.trade = urls["trade"]
            self.posttrade = urls["posttrade"]
            self.chart = urls["chart"]
    
    def create_session(self, ws: ws.WebSocket):
        creds = {
            "CredentialsType": "login",
            "Token": f"{os.getenv('IG_USER')}:{os.getenv('IG_PASS')}"
        }
        request = {
            "MessageType": "Negotiate",
            "Timestamp": int(time()),
            "SessionId": f"{self.session_id}",
            "ClientFlow": "Unsequenced",
            "Credentials": creds
        }
        self.logger.info("Creating login Request")
        self.logger.debug(json.dumps(request))
        ws.send(json.dumps(request))
    
    async def handle_incoming(self, ws: ws.WebSocket):
        while True:
            try:
                response = ws.recv()
                print ("Received '%s'" % json.loads(response))
                sleep(3)
            except KeyboardInterrupt:
                sys.exit(2)
            except Exception as e:
                print(f"websocket error: {e}")
    
    async def keep_alive(self, ws: ws.WebSocket):
        msg = {
            "MessageType": "Establish",
            "Timestamp": int(time()),
            "SessionId": f"{self.session_id}",
            "KeepaliveInterval": 65000
        }
        while True:
            try:
                print(f"Sending keep alive msg: {msg} ")
                ws.send(json.dumps(msg))
                sleep(50)
            except KeyboardInterrupt:
                sys.exit(2)
            except Exception as e:
                print(f"websocket error: {e}")