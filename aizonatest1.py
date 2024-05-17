#Yiğit Aytekin Aizona Test 1
import asyncio
import websockets
import json
from multiprocessing import Process, Manager

class BybitCoinClass:
    def __init__(self, symbols):
        self.symbols = symbols
        self.manager = Manager()
        self.data = self.manager.dict()
        for symbol in symbols:
            self.data[symbol] = {"ask": [0, 0], "bid": [0, 0]}
        self.websocket_url = "wss://stream.bybit.com/v5/public/linear"
        self.process = Process(target=self.run)

    async def _send_heartbeat(self, websocket):
        while True:
            await asyncio.sleep(30)
            await websocket.send(json.dumps({"op": "ping"}))

    async def _subscribe(self, websocket):
        for symbol in self.symbols:
            await websocket.send(json.dumps({
                "op": "subscribe",
                "args": [f"orderbook.1.{symbol}"]
            }))

    async def _handle_message(self, message):
        data = json.loads(message)
        if "topic" in data and "orderbook" in data["topic"]:
            symbol = data["topic"].split(".")[2]
            for update in data["data"]:
                if "a" in update:  
                    self.data[symbol]["ask"] = update["a"][0]
                if "b" in update:  
                    self.data[symbol]["bid"] = update["b"][0]

    async def _run(self):
        async with websockets.connect(self.websocket_url) as websocket:
            await self._subscribe(websocket)
            asyncio.create_task(self._send_heartbeat(websocket))
            while True:
                try:
                    message = await websocket.recv()
                    await self._handle_message(message)
                except websockets.ConnectionClosed:
                    for symbol in self.symbols:
                        self.data[symbol] = {"ask": [0, 0], "bid": [0, 0]}
                    break

    def run(self):
        asyncio.run(self._run())

    def start(self):
        self.process.start()

    def join(self):
        self.process.join()

    def get_ask(self, symbol):
        return self.data[symbol]["ask"]

    def get_bid(self, symbol):
        return self.data[symbol]["bid"]

if __name__ == "__main__":
    bybit_obj = BybitCoinClass(["BTCUSDT", "ETHUSDT"])
    bybit_obj.start()

    import time
    time.sleep(10)  

    print(bybit_obj.get_bid("BTCUSDT"))
    print(bybit_obj.get_ask("BTCUSDT"))
    print(bybit_obj.get_bid("ETHUSDT"))
    print(bybit_obj.get_ask("ETHUSDT"))

    bybit_obj.join()
