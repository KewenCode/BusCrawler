import json
import os
from datetime import datetime, date, timedelta

from qq_connect.Bot_sendmsg import http

global gl_msgs, gl_send, gl_websocket
"""
gl_msgs = {'100': {'id':{}}, '200': {}, '300': {}}
"""

cur_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
proj_path = cur_path[:cur_path.find('bus_web')]


def _init():
    """
    初始化全局变量
    :return:
    """
    global gl_msgs, gl_send, gl_websocket
    Tools.File_Read()  # 加载gl_msgs起始文件
    gl_send = {100: [], 200: [], 300: [], 888: []}


def MSG_IN(data):
    """
    {type:'LINE_LOG', code:'LINE_SUPPORT', time:xx, append:{class:1, id:x, line:xx, direction:xx, support:xx}}
    class 消息重要性 100-重要(立即发布) 200-次要(消息简报发送) 300-普通(记录日志)
    msgs = {'100': [], '200': [], '300': []}
    LINE_SUPPORT: 支援消息

    :param data: 输入dict或list对象，自动判断类型
    :return: 返回待发布消息
    """

    def LINE_LOG(log: dict):
        if log['code'] == 'LINE_SUPPORT':
            LINE.LINE_SUPPORT(D=log['append'], T=log['time'])
        elif log['code'] == 'LINE_SUPPORT_DAILY':
            LINE.LINE_SUPPORT_DAILY(D=log['append'], T=log['time'])
        elif log['code'] == 'LINE_RUNNING':
            LINE.LINE_RUNNING(D=log['append'], T=log['time'])

    def ERROR_LOG(log: dict):
        if log['code'] == 'ERROR_PROXIES':
            ERROR.ERROR_PROXIES(D=log['append'], T=log['time'])

    if type(data) == dict:
        if data['type'] == 'LINE_LOG':
            LINE_LOG(data)
        if data['type'] == 'ERROR_LOG':
            ERROR_LOG(data)
    else:
        for info in data:
            if info['type'] == 'LINE_LOG':
                LINE_LOG(info)
            if info['type'] == 'ERROR_LOG':
                ERROR_LOG(info)

    # 数据记录


class Tools:
    @staticmethod
    def Write_Msg(*args, **kwargs):
        def wrapper(func):
            def inner_wrapper(D: dict, T: int):
                Time = datetime.fromtimestamp(int(T) / 1000).strftime('%H:%M')
                Type, IDs, Log_Msg = func(D, Time)  # 目标函数

                gl_msgs[D['class']][IDs] = [Log_Msg, T, Type]
                Log_input = f'{D["class"]}[{IDs}]:{Log_Msg}' + '\n'
                File = open(proj_path + f'bus_web/DateFile/Log/{str(date.today())}.log', mode='a', encoding='utf-8')
                File.write(Log_input)
                File.close()

            return inner_wrapper

        return wrapper

    @staticmethod
    def Send_Msg(Class=None):
        if Class is None:
            Class = [100, 888]
        cq_receive = []
        for C in Class:
            for msgs in gl_send[C]:
                if C == 888:
                    receive = http(end_str='/send_msg', QQ=3353670285, msg=f"{msgs}", ).http_get()
                else:
                    receive = http(end_str='/send_msg', Group=826224229, msg=f"{msgs}").http_get()
                cq_receive.append(receive)
            gl_send[C].clear()
        print(cq_receive)

    @staticmethod
    def Clear_Msg():
        global gl_msgs
        for C in list(gl_msgs):
            for U in list(gl_msgs[C]):
                if int(gl_msgs[C][U][1]) / 1000 < int((datetime.now() - timedelta(hours=12)).timestamp()):
                    gl_msgs[C].pop(U)

    @staticmethod
    def Print_Msg(ways='http', Class=None):

        def Single_Class(C):
            output = ''
            title_type = ''
            for obj in list(gl_msgs[C]):
                if gl_msgs[C][obj][2] not in title_type:
                    title_type = title_type + '[' + str(gl_msgs[C][obj][2]) + ']'
                output = '\n' + gl_msgs[C][obj][0]

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
            if ways == 'http':
                R = Single_Class(Class)
                if R is None:
                    R = '暂无数据'
                receive = http(end_str='/send_msg', Group=826224229, msg=f"{R}").http_get()
            elif ways == 'socket':
                receive = Single_Class(Class)
        elif type(Class) is list:
            send_m = ''
            for num in Class:
                R = Single_Class(num)
                if R is not None:
                    send_m = send_m + R + '\n==========\n'
            if ways == 'http':
                if send_m == '':
                    send_m = '暂无数据'
                receive = http(end_str='/send_msg', Group=826224229, msg=f"{send_m}").http_get()
            elif ways == 'socket':
                receive = send_m

        return receive

    @staticmethod
    def File_Read(msgs=None, mode='r+'):
        global gl_msgs
        Request = open(proj_path + 'bus_web/DateFile/Temp/Temp_Log.txt', mode=mode)
        if msgs is not None:
            Request.write(json.dumps(msgs))
        else:
            gl_msgs = Tools.convert_json_key(json.loads(Request.read()))
            if not gl_msgs:
                gl_msgs = {100: {}, 200: {}, 300: {}}
        Request.close()

    @staticmethod
    def File_Write(msgs=None, mode="w+"):
        global gl_msgs
        Request = open(proj_path + 'bus_web/DateFile/Temp/Temp_Log.txt', mode=mode)
        if msgs is not None:
            Request.write(json.dumps(msgs))
        else:
            Request.write(json.dumps(gl_msgs))
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
                res_dict = Tools.convert_json_key(value)
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

    @staticmethod
    def Msg_ID(head=None, append=None):
        return f'{str(date.today())}/{head}({append})'


class LINE:
    @staticmethod
    @Tools.Write_Msg()
    def LINE_SUPPORT(D: dict, T: int):
        """
        :param D: {class:100, id:x, line:xx, direction:xx, support:xx, his:xx}
        :param T:
        :return:
        """
        Type = '🅩'
        IDs = Tools.Msg_ID('LINE_SUPPORT', f'{D["support"] + D["id"]}')
        Log_Msg = f"🅩[{D['id']}] {T} {D['line']}»»{D['support']}·{D['direction']}"
        if D['his'] != str(date.today()) and D['class'] == 100:
            gl_send[D['class']].append(Log_Msg + f"·{D['his']}")

        return Type, IDs, Log_Msg

    @staticmethod
    @Tools.Write_Msg()
    def LINE_SUPPORT_DAILY(D: dict, T: str):
        Type = '🅩🅓'
        IDs = Tools.Msg_ID('LINE_SUPPORT_DAILY', f'{D["support"] + D["id"]}')
        Log_Msg = f"🅩🅓[{D['id']}] {T} »»{D['support']}·{D['direction']}"
        if D['his'] != str(date.today()) and D['class'] == 100:
            gl_send[D['class']].append(Log_Msg + f"·{D['his']}")

        return Type, IDs, Log_Msg

    @staticmethod
    @Tools.Write_Msg()
    def LINE_RUNNING(D: dict, T: str):
        Type = '🅡'
        if not D['his']:
            T_str = '首次行驶'
        else:
            T_str = datetime.fromtimestamp(int(D['his']) / 1000).strftime('%Y-%m-%d %H:%M')
        IDs = Tools.Msg_ID('LINE_RUNNING', f'{D["line"] + D["id"]}')
        if not D['support']:
            Log_Msg = f"🅡[{D['id']}] {T} Last:{T_str}"
        elif not D['his']:
            Log_Msg = f"🅡[{D['id']}] {T} {T_str}{D['support']}"
        else:
            Log_Msg = f"🅡[{D['id']}] {T} »»{D['support']}·Last:{T_str}"
            gl_send[D['class']].append(Log_Msg)

        return Type, IDs, Log_Msg


class ERROR:
    @staticmethod
    @Tools.Write_Msg()
    def ERROR_PROXIES(D: dict, T: str):
        """
        :param D: {class:100, msg:xx, cite:xx}
        :param T:
        :return:
        """
        Type = '🅔'
        IDs = Tools.Msg_ID('ERROR_PROXIES', f'{D["cite"]}')
        Log_Msg = f"🅔[ProxiesIP] {D['msg']}"
        gl_send[888].append(f"{D['msg']}")

        return Type, IDs, Log_Msg
