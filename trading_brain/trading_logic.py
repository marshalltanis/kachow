from ig import IgUsa
import concurrent.futures as cf
from websocket import WebSocket
import asyncio
import sys


async def recv_handler(trade_api: IgUsa):
    with cf.ThreadPoolExecutor(max_workers=2):
        trade_api.handle_incoming(trade_api.pt_ws)
        task_trade = asyncio.create_task(trade_api.handle_incoming(trade_api.trade_ws))
    await task_pt
    await task_trade
    return True

def create_sessions(trade_api: IgUsa):
    print("Creating Sessions (in sync)")
    trade_api.create_session(trade_api.pt_ws)
    trade_api.create_session(trade_api.trade_ws)
    return True

async def keep_alive(trade_api: IgUsa):
    task_pt = asyncio.create_task(trade_api.keep_alive(trade_api.pt_ws))
    task_trade = asyncio.create_task(trade_api.keep_alive(trade_api.trade_ws))
    await task_pt
    await task_trade
    return True

async def main():
    trade_api = IgUsa("demo_config.json")
    print("Creating Session")
    try:
        sessions = create_sessions(trade_api)
    except Exception as e:
        print(f"Error creating session: {e}")
    if not sessions:
        print("Yikes")
        sys.exit(2)
    handler = asyncio.create_task(recv_handler(trade_api))
    alive = asyncio.create_task(keep_alive(trade_api))
    await handler
    await alive
   
    

if __name__=="__main__":
    asyncio.run(main())