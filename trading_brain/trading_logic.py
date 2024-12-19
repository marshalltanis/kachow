from metatrader4 import MT4
import multiprocessing
import asyncio
import time
import sys

RUNNING_TASKS = {}

def recv_handler(trade_api):
    while True:
        if trade_api.is_connected():
            print("Connection Identified")
            tick = trade_api.receive_tick_info()
            if not tick:
                print("Socket is disconnected")
                return

        else:
            print("Disconnected")
            return

def control(trade_api):
    global RUNNING_TASKS
    while True:
        print("Please enter a command. Type help for more information:")
        command = input()
        if command == "help":
            help_info = f"""
                help - display help commands
                c - connect to MT4 server
                d - disconnect from MT4 server
                s - display current connection status
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
                    RUNNING_TASKS["receive"] = multiprocessing.Process(target=recv_handler, args=(trade_api, ))
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
            continue
        if command == "e":
            if trade_api.is_connected():
                RUNNING_TASKS["receive"].terminate()
                RUNNING_TASKS.pop("receive")
            return


def initialize_model():
    return True

def create_sessions(trade_api):
    trade_api.create_session()
    return True

def keep_alive(trade_api):
    return True

def main():
    global RUNNING_TASKS
    trade_api = MT4("demo_config.json")
    control(trade_api)

if __name__ == "__main__":
    main()
