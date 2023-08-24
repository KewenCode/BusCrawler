import json
import os
import sys

import requests
from nakuru import (
    CQHTTP,
    GroupMessage,
    Notify,
    GroupMessageRecall,
    FriendRequest,
    FriendMessage
)
from nakuru.entities.components import Plain, Image
from nakuru.network import fetch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from bus_web.Request import amap
from qq_connect.Nakurut.Bot_QA import QA

global gl_msgs
QA_Obj = {}


def hostcheck():
    host = ['localhost', '192.168.1.215']
    for each in host:
        try:
            response = requests.get(url=f'http://{each}:15202/get_login_info', timeout=1)  # 设置timeout，使响应等待1s
        except:
            continue
        if response.status_code == 200:
            json_re = json.loads(response.text)
            if json_re['retcode'] == 0:
                print(f'已登录QQ:{json_re["data"]["user_id"]}，用户名：{json_re["data"]["nickname"]}')
                return each
    exit('未登录go-cqhttp，无法发送消息!')


app = CQHTTP(
    host=hostcheck(),
    port=15203,
    http_port=15202,
    token=None  # 可选，如果配置了 Access-Token
)


@app.receiver("GroupMessage")
async def _(app: CQHTTP, source: GroupMessage):
    global QA_Obj
    if source.sender.user_id in list(QA_Obj):
        if source.raw_message == 'Exit':
            del QA_Obj[source.sender.user_id]
            await app.sendGroupMessage(source.group_id, f'[CQ:at,qq={source.sender.user_id}]\n' + '查询结束')
        else:
            source_list = source.raw_message.split('|')
            try:
                QU = QA_Obj[source.sender.user_id].send(
                    source_list if len(source_list) == 2 else (source.raw_message, None)
                )
                await app.sendGroupMessage(source.group_id, f'[CQ:at,qq={source.sender.user_id}]\n' + QU)
            except StopIteration as AN:
                del QA_Obj[source.sender.user_id]
                await app.sendGroupMessage(source.group_id, f'[CQ:at,qq={source.sender.user_id}]\n' + str(AN))

    # 通过纯 CQ 码处理
    if source.raw_message == "戳我":
        await app.sendGroupMessage(source.group_id, f"[CQ:poke,qq={source.user_id}]")
    if source.raw_message == "事件简报":
        global gl_msgs
        Tool().File_Read()
        await app.sendGroupMessage(source.group_id, Tool.Print_Msg())
    if source.raw_message == "测试":
        # 创建生成器
        QA_Obj[source.sender.user_id] = QA(
            {'1': {'11': 'A', '12': 'A'}, '2': {'21': {'211': 'A', '212': 'A'}, '22': 'A'}, '3': 'A'},
            {'1': '车号索引', '11': '最近运行记录', '12': '支援记录',
             '2': '线路索引', '21': '历史运营*', '211': '日期索引', '212': '月份索引', '22': '当日运营',
             '3': '日期索引'},
            {'A': 'LAST_RUN_TIME'}
        ).yield_Object()
        await app.sendGroupMessage(source.group_id,
                                   f'[CQ:at,qq={source.sender.user_id}]\n' + next(QA_Obj[source.sender.user_id]))
    if source.raw_message.find('车辆信息查询') == 0:
        data = source.raw_message.split(' ')
        del data[0]
        # 创建生成器
        QA_Obj[source.sender.user_id] = QA(
            {'0': {'1': 'A', '2': {'21': 'B', '22': 'C'}, '3': 'D'}},
            {'0': '请输入车号*', '1': '记录状态',
             '2': '运营状态', '21': '运营历史', '22': '配属历史',
             '3': '支援情况'},
            {'A': 'BUS_STATE', 'B': 'BUS_OPERATE_HIS', 'C': 'BUS_BELONG_HIS', 'D': 'BUS_SUPPORT_HIS'}
        ).yield_Object(arg_list=data if len(data) > 0 else None)
        await app.sendGroupMessage(source.group_id,
                                   f'[CQ:at,qq={source.sender.user_id}]\n' + next(QA_Obj[source.sender.user_id]))
    # 通过消息链处理
    # chain = source.message
    # if isinstance(chain[0], Plain):
    #     if chain[0].text == "看":
    #         await app.sendGroupMessage(source.group_id, [
    #             Plain(text="给你看"),
    #             # Image.fromFileSystem("D:/好康的.jpg")
    #         ])


@app.receiver("FriendMessage")
async def _(app: CQHTTP, source: FriendMessage):
    if source.raw_message == "停止BOT运行":
        await app.sendGroupMessage(826224229, f"BOT已停止服务")
        app.close()
        sys.exit()
    if source.raw_message == "停止amap运行":
        amap.amap_stop()
        await app.sendGroupMessage(826224229, f"五分钟内将停止车辆数据查询服务")
        await app.canSendImage()


@app.receiver("GroupMessageRecall")
async def _(app: CQHTTP, source: GroupMessageRecall):
    await app.sendGroupMessage(source.group_id, "你撤回了一条消息")


@app.receiver("Notify")
async def _(app: CQHTTP, source: Notify):
    if source.sub_type == "poke" and source.target_id == 114514:
        await app.sendGroupMessage(source.group_id, "不许戳我")


# @app.receiver("FriendRequest")
# async def _(app: CQHTTP, source: FriendRequest):
#     await app.setFriendRequest(source.flag, True)


class Tool:
    cur_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
    proj_path = cur_path[:cur_path.find('qq_connect')]

    @staticmethod
    def Print_Msg(Class=None):

        def Single_Class(C):
            output = ''
            title_type = ''
            for obj in list(gl_msgs[C]):
                if gl_msgs[C][obj][2] not in title_type:
                    title_type = title_type + '[' + str(gl_msgs[C][obj][2]) + ']'
                output = output + '\n' + gl_msgs[C][obj][0]

            if len(title_type) > 0:
                return title[C] + title_type + output
            else:
                return None

        global gl_msgs
        receive = ''
        title = {100: " ★★★ 🔴 ★★★ ", 200: " ☆★★ 🔵 ★★☆ ", 300: " ☆☆★ ⚪ ★☆☆ "}
        if Class is None:
            Class = [100, 200, 300]
        if type(Class) is int:
            R = Single_Class(Class)
            if R is None:
                R = '暂无数据'
            receive = R
        elif type(Class) is list:
            send_m = ''
            for num in Class:
                R = Single_Class(num)
                if R is not None:
                    send_m = send_m + R + '\n==========\n'
            if send_m == '':
                send_m = '暂无数据'
            receive = send_m

        return receive

    def File_Read(self, msgs=None, mode='r+'):
        global gl_msgs
        Request = open(self.proj_path + 'bus_web/DateFile/Temp/Temp_Log.txt', mode=mode)
        if msgs is not None:
            pass
        else:
            gl_msgs = self.convert_json_key(json.loads(Request.read()))
            if not gl_msgs:
                gl_msgs = {100: {}, 200: {}, 300: {}}
        Request.close()

    @staticmethod
    def convert_json_key(param_dict):
        """
        json.dump不支持key是int的dict，在编码存储的时候会把所有的int型key写成str类型的
        所以在读取json文件后，用本方法将所有的被解码成str的int型key还原成int
        """
        new_dict = dict()
        for key, value in param_dict.items():
            if isinstance(value, (dict,)):
                res_dict = Tool.convert_json_key(value)
                try:
                    new_key = int(key)
                    new_dict[new_key] = res_dict
                except:
                    new_dict[key] = res_dict
            else:
                try:
                    new_key = int(key)
                    new_dict[new_key] = value
                except:
                    new_dict[key] = value

        return new_dict


def Bot_run():
    app.run()


if __name__ == '__main__':
    Bot_run()
