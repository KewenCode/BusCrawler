import asyncio
import json
import threading

import websockets as ws
from websockets import ConnectionClosed

from qq_connect import Bot_sendmsg, Bot_Nakurut
from qq_connect.Bot_sendmsg import websocket

count = 0

Bot_Nakurut.Bot_run()



# url = "ws://localhost:15203"
# # 初始化websocket连接
# ws = websocket
# # 发送请求并接收回复
# ws.send("Hello, websocket!")
# result = ws.recv()
# # 输出回复内容
# print(result)
# # 关闭websocket连接
# ws.close()

# async def hello():
#     uri = "ws://localhost:15203"
#
#     while True:
#         try:
#             async with ws.connect(uri) as websocket:
#                 jsona = {
#                     "action": "get_friend_list",
#                     # "params": {
#                     #     "user_id": "参数值",
#                     #     "参数名2": "参数值"
#                     # },
#                     "echo": "1"
#                 }
#                 a = json.dumps(jsona)
#                 print(a)
#                 await websocket.send(a)
#                 while True:
#                     try:
#                         re = await websocket.recv()
#                         print(re)
#                     except ConnectionClosed as e:
#                         # 1000 正常关闭码
#                         # 1006 服务端内部错误异常关闭码
#                         print(e.code)
#                         if e.code == 1006:
#                             print('restart')
#                             await asyncio.sleep(2)
#                             break
#         except ConnectionRefusedError as e:
#             print(e)
#             global count
#             if count == 10:
#                 return
#             count += 1
#             await asyncio.sleep(2)
#
#
# asyncio.get_event_loop().run_until_complete(hello())

# WS_URL = "ws://localhost:15203/api"
# jsona = {
#     "action": "get_friend_list",
#     # "params": {
#     #     "user_id": "参数值",
#     #     "参数名2": "参数值"
#     # },
#     "echo": "1"
# }
# a = json.dumps(jsona)
#
#
# async def read(bot_api):
#     while True:
#         msg = await bot_api.recv()
#         print(f"<<<: {msg}")
#
#
# async def hello():
#     uri = WS_URL
#     async with ws.connect(uri) as bot_api:
#         asyncio.create_task(read(bot_api))
#
#         while True:
#             if a is not None:
#                 await bot_api.send(a)
#                 print(f">>> {a}")
#                 await asyncio.sleep(3)
#
#
# if __name__ == "__main__":
#     asyncio.run(hello())
