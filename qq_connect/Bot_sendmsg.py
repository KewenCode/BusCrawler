import json

import asyncio
import threading

import requests
import websockets as ws
from websockets import ConnectionClosed


class http:
    def __init__(self, end_str, msg, QQ=None, Group=None):
        self.end_str = end_str
        self.Group = Group
        self.QQ = QQ
        self.msg = msg

    def http_get(self):
        host = ['localhost', '192.168.1.215']
        data = {
            'group_id': self.Group,
            'user_id': self.QQ,
            'message': self.msg
        }
        for each in host:
            try:
                url = f"http://{each}:15202{self.end_str}"
                response = requests.get(url=url, params=data)
            except:
                continue
                # return 'QQ未登录'
            if response == 404:
                return 'API不存在，请核实终结点！'
            else:
                return response.text
        return 'QQ Bot未启动！'


class websocket:
    @staticmethod
    async def clientSend(msg, ADDR='localhost', PORT='15203', Endpoint=''):
        async with ws.connect("ws://" + ADDR + ":" + PORT + "/" + Endpoint) as BOT_API:
            global bot
            bot = BOT_API
            await BOT_API.send(msg)
            print(f">>> {'a'}")
            await asyncio.sleep(3)
            await BOT_API.close()

    def WebSocketServer(self):
        asyncio.run(self.clientRun())

    @staticmethod
    async def clientRun(ADDR='localhost', PORT='15203', Endpoint=''):
        async with ws.connect("ws://" + ADDR + ":" + PORT + "/" + Endpoint) as BOT_API:
            await websocket.clientRead(BOT_API)

    @staticmethod
    async def clientRead(bot_api):
        while True:
            msg = await bot_api.recv()
            print(f"<<<: {msg}")

