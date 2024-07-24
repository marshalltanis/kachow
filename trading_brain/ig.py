import json
import os
import logging
from websockets import client
from time import time
import uuid
from utils import logger


class IgUsa:
    def __init__(self, config:str):
        self.config = config
        self.logger = logger.logger()
        self.logger.info("Creating API")
        self.__parse_config()
        self.pt_ws = client.connect(uri=self.pretrade,logger=self.logger)
        self.trade_ws = client.connect(uri=self.trade, logger=self.logger)
    
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
    
    def create_session(self, ws: client):
        creds = {
            "CredentialsType": "login",
            "Token": f"{os.getenv('IG_USER')}:{os.getenv('IG_PASS')}"
        }
        request = {
            "MessageType": "Negotiate",
            "Timestamp": int(time()),
            "SessionId": f"{uuid.uuid4()}",
            "ClientFlow": "Unspecified",
            "Credentials": creds
        }
        self.logger.info("Creating Request")
        self.logger.debug(json.dumps(request))
