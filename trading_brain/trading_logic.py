from metatrader4 import MT4
import concurrent.futures as cf
import asyncio
import sys


async def recv_handler(trade_api):
    while True:
        tick = trade_api.receive_tick_info()
        if not tick:
            print("Something bad happened\n")
    return True


def create_sessions(trade_api):
    trade_api.create_session()
    return True

async def keep_alive(trade_api):
    return True

async def main():
    trade_api = MT4("demo_config.json")
    print("Creating Session")
    try:
        trade_api.create_session()
    except Exception as e:
        print(f"Error creating session: {e}")
    await recv_handler(trade_api)

    trade_api.disconnect()


   
    

if __name__=="__main__":
    asyncio.run(main())