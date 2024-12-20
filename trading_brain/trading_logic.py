from metatrader4 import MT4
import multiprocessing
import os
import datetime
import asyncio
import time
import sys
import models.RNN as RNN
import logging
import builtins

# Redisgn this into a config
RUNNING_TASKS = {}
TRAINING_DATA = "..\\data\EURUSD_H1.csv"
PROCESS_QUEUE = multiprocessing.Queue()
RECV_LOG = f"log\\recv_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
MODEL_LOG = f"log\\model_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
COMMAND_LOG = f"log\\command_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def setup_log(filename):
    file_handler = logging.FileHandler(filename, mode="a", encoding=None, delay=False)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    file_handler.stream = open(file_handler.baseFilename, mode="a", buffering=1)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    builtins.print = logger.debug
def recv_handler(trade_api, data_manager):
    global PROCESS_QUEUE, RECV_LOG
    setup_log(RECV_LOG)
    while True:
        if not data_manager["receive"]["run_flag"]:
            print("Run flag transitioned, exiting program")
            return
        if trade_api.is_connected():
            tick = trade_api.receive_tick_info()
            if not tick:
                print("Socket is disconnected")
                return
            PROCESS_QUEUE.put(tick)

        else:
            print("Disconnected")
            return

def update_shared_mem(data_manager, process, item: dict):
    if process not in data_manager:
        print(f"Creating process info for {process}")
        data_manager[process] = {"Process": process}
        data_manager[process].update(item)
    else:
        print(f"Adding {item} to {process}")
        data_manager[process].update(item)
def control(trade_api, model):
    global RUNNING_TASKS
    data_manager = multiprocessing.Manager().dict()
    recv_run_flag = True

    while True:
        print("Please enter a command. Type help for more information:")
        command = input()
        if command == "help":
            help_info = f"""
                help - display help commands
                c - connect to MT4 server
                d - disconnect from MT4 server
                s - display current connection status
                m - generate & train model
                e - kill program
                r - disconnect, refetch & train model, reconnect
            """
            print(f"Please select from the following commands:{help_info}")
            continue
        if command == "c":
            if trade_api.is_connected():
                print("Already connected, please choose a different command")
            else:
                trade_api.create_session()
                if "receive" not in RUNNING_TASKS:
                    print("Starting receive thread")
                    update_shared_mem(data_manager, "receive", {"run_flag": recv_run_flag})
                    RUNNING_TASKS["receive"] = multiprocessing.Process(target=recv_handler, args=(trade_api, data_manager))
                    RUNNING_TASKS["receive"].start()
                print("New session created")
            continue
        if command == "d":
            if trade_api.is_connected():
                trade_api.disconnect()
                RUNNING_TASKS["receive"].terminate()
                RUNNING_TASKS.pop("receive")
            print("Session disconnected")
            continue
        if command == "s":
            trade_api.print_stats()
            if "model" in RUNNING_TASKS:
                process_alive = RUNNING_TASKS['model'].is_alive()
                if process_alive:
                    pid = RUNNING_TASKS['model'].pid
                    print(f"Process running model - {pid} is alive")
                else:
                    print("Process has finished")
                    RUNNING_TASKS.pop("model")
            continue

        if command == "e":
            data_manager["receive"]["run_flag"] = False
            trade_api.disconnect()
            RUNNING_TASKS["receive"].join()
            RUNNING_TASKS.pop("receive")
            return


def initialize_model():
    global PROCESS_QUEUE
    model: RNN.Model = None
    if not model:
        if not os.path.exists(TRAINING_DATA):
            print(f"Check the path of the data folder - {TRAINING_DATA}")
        model = RNN.Model(TRAINING_DATA, 3)
        print("Model initialized, waiting for commands")
    return model


def create_sessions(trade_api):
    trade_api.create_session()
    return True

def keep_alive(trade_api):
    return True

def main():
    global RUNNING_TASKS
    trade_api = MT4("demo_config.json")
    model = initialize_model()
    control(trade_api, model)

if __name__ == "__main__":
    main()
