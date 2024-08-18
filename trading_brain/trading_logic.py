from ig import IgUsa
import asyncio
from websocket import WebSocket


async def recv_handler(trade_api: IgUsa):
    task_pt = asyncio.create_task(trade_api.handle_incoming(trade_api.pt_ws))
    task_trade = asyncio.create_task(trade_api.handle_incoming(trade_api.trade))
    await task_pt
    await task_trade

async def main():
    trade_api = IgUsa("demo_config.json")
    handler = recv_handler(trade_api)
    trade_api.create_session(trade_api.pt_ws)
    await(handler)
   
    

if __name__=="__main__":
    asyncio.run(main())