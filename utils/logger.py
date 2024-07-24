import logging
import sys


LOGGING_LEVEL = logging.DEBUG

class logger():
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(LOGGING_LEVEL)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(LOGGING_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def debug(self, msg: str):
        self.logger.debug(msg)
    
    def error(self, msg: str):
        self.logger.error(msg, stack_info=True, exc_info=True)
    
    def critical(self, msg: str):
        self.logger.critical(msg, stack_info=True, exc_info=True)