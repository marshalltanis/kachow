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
import keyboard
import msvcrt

# Redisgn this into a config
RUNNING_TASKS = {}
TRAINING_DATA = "..\\data\EURUSD_H1.csv"
PROCESS_QUEUE = multiprocessing.Queue()
COMMAND_TARGET = multiprocessing.Value('u')
RECV_LOG = f"log\\recv_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
MODEL_LOG = f"log\\model_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
COMMAND_LOG = f"log\\command_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def recv_handler(trade_api, data_manager, do_commmand):
    global PROCESS_QUEUE, RECV_LOG
    print("Receive thread started")
    do_commmand.set()
    while True:
        sys.stdout.flush()
        print(data_manager["receive"]["run_flag"])
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
        data_manager[process] = item
        print(data_manager[process])
    else:
        print(f"Adding {item} to {process}")
        data_manager[process].update(item)
def control(trade_api, model, do_command, data_manager):
    global RUNNING_TASKS, COMMAND_TARGET
    recv_run_flag = True
    while True:
        command = input("Please enter a command. Type help for more information: ")
        print(f"Received Command {command}")
        if command == "h":
            help_info = f"""
                h - display help commands
                c - connect to MT4 server
                d - disconnect from MT4 server
                s - display current connection status
                m - validate model
                p - show graph of model predictions
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
                    RUNNING_TASKS["receive"] = multiprocessing.Process(target=recv_handler,
                                                                       args=(trade_api, data_manager, do_command))
                    RUNNING_TASKS["receive"].start()
                    # make sure process actually starts
                    do_command.wait()
                    do_command.clear()
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
        if command == "m":
            if "model" in RUNNING_TASKS:
                print(f"Model is already running")
            else:
                print("Starting model thread")
                update_shared_mem(data_manager, "model", {"run_flag": True})
                RUNNING_TASKS["model"] = multiprocessing.Process(target=model_controller, args=(data_manager, model, do_command))
                RUNNING_TASKS["model"].start()
                do_command.wait()
                do_command.clear()
                print("Started model controller")

        if command == "p":
            test_data = model.create_test_data(model.test_data)
            model.plot_prediction(test_data[0], test_data[1])
        if command == "e":
            if "receive" in data_manager:
                data_manager["receive"]["run_flag"] = False
            if "receive" in RUNNING_TASKS:
                trade_api.disconnect()
                RUNNING_TASKS["receive"].join()
                return
            return

def model_controller(data_manager, model):
    while True:
        if "model" in data_manager:
            if "run_flag" in data_manager["model"]:
                if not data_manager["model"]["run_flag"]:
                    print("Run flag is now false, stopping")
                    return
        get_last_tick = PROCESS_QUEUE.get()
        if not get_last_tick:
            print(f"Couldn't find tick info")
        if get_last_tick.open is not None:
            print("Predicting next open")
            model.predict_next_open(get_last_tick.open)


def initialize_model():
    global PROCESS_QUEUE
    model: RNN.Model = None
    if not model:
        if not os.path.exists(TRAINING_DATA):
            print(f"Check the path of the data folder - {TRAINING_DATA}")
        model = RNN.Model(TRAINING_DATA, 2, False)
        print("Model initialized, waiting for commands")
    return model

def create_sessions(trade_api):
    trade_api.create_session()
    return True

def keep_alive(trade_api):
    return True

def main():
    global RUNNING_TASKS
    data_manager = multiprocessing.Manager().dict()
    trade_api = MT4("demo_config.json")
    #model = initialize_model()
    model = None
    command_recvd = multiprocessing.Event()
    finished_command = multiprocessing.Event()
    # command_recvd activated when main process needs to do work, finished_command is indication event is done.
    control(trade_api, model, command_recvd, data_manager)
    print("Leaving!")

if __name__ == "__main__":
    main()
