import json

import asyncio
import threading

import requests
import websockets as ws
from websockets import ConnectionClosed

global bot


def _init():
    global bot


def r_bot():
    return bot


class http:
    def __init__(self, end_str, msg, QQ=None, Group=None):
        self.end_str = end_str
        self.Group = Group
        self.QQ = QQ
        self.msg = msg

    def http_get(self):
        url = f"http://localhost:15202{self.end_str}"
        data = {
            'group_id': self.Group,
            'user_id': self.QQ,
            'message': self.msg
        }
        response = requests.get(url=url, params=data).text
        return response


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

