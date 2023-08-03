import json
import os
import threading
import time
from datetime import datetime, timedelta
from random import choice

from bus_web.Defin.data_define import parameter
from bus_web.Defin.sqlite_define import WebDate_operate
from bus_web.Defin.web_define import Amap_webdata
from bus_web.Message import line_message

cur_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
proj_path = cur_path[:cur_path.find('bus_web')]


class Request_Filter:

    def __init__(self, target_db):
        self.target_db = target_db

    @staticmethod
    def web_connect(line, bus_data_collect, bus_data_no):
        print(line['Line'])  # 输出线名
        receive, code = Amap_webdata(line['Line'], line['Direction'], line['Ent'], line['In'],
                                     line['Csid']).data_receive()
        if code == 200:
            # 正常响应
            bus_data_collect = bus_data_collect + receive
        elif code == 201:
            # 无数据
            bus_data_no[line['LineID']] = line['Line']
        elif code == 203:
            # 备用，处理代理ip
            pass
        else:
            # 其他特殊情况
            print(f'服务器代码{code}')

        print("_______________")
        return bus_data_collect, bus_data_no

    def web_day_normal(self):
        """
        适用范围，0-24不跨日期线路
        :return: 数据列表
        """
        ctime = datetime.now()
        hour = ctime.hour
        # minute = ctime.minute
        query_collect = []

        # 初筛——待启用数据
        update_collect_1 = []
        sql_start = f" where STime_H <= {hour + 1} and ETime_H > {hour} and Model = 5"
        bus_query_st = WebDate_operate(self.target_db).fetchall(sql_start)
        if len(bus_query_st) != 0:
            for each in bus_query_st:
                ctime = datetime.now()
                s_clock = datetime.strptime(each['STime'], "%H:%M")
                e_clock = datetime.strptime(each['ETime'], "%H:%M")
                stime = datetime(year=ctime.year, month=ctime.month, day=ctime.day,
                                 hour=s_clock.hour, minute=s_clock.minute)
                etime = datetime(year=ctime.year, month=ctime.month, day=ctime.day,
                                 hour=e_clock.hour, minute=e_clock.minute)
                # print(stime,etime)
                # print(stime - timedelta(hours=1))
                # print(ctime)

                if stime - timedelta(hours=1) < ctime:
                    if each['Ext'] is None:
                        time_json = {"STime": stime.timestamp(),
                                     "ETime": etime.timestamp(),
                                     "EMark": 0}
                    else:
                        time_json = json.loads(each['Ext'])
                        time_json['STime'] = stime.timestamp()
                        time_json["ETime"] = etime.timestamp()
                        time_json['EMark'] = 0

                    update_collect_1.append([1, json.dumps(time_json), each['LineID']])
            # 更新Model数据
            print(update_collect_1)
            if len(update_collect_1) > 0:
                WebDate_operate(
                    table="amap", data=update_collect_1).update(
                    query_row="LineID", target_row1="Model", target_row2="Ext")

        # 初筛——即将结束运营线路
        update_collect_2 = []
        sql_end = f" where ETime_H <= {hour} and Model = 1"
        bus_query_end = WebDate_operate(self.target_db).fetchall(sql_end)
        if len(bus_query_end) != 0:
            for each in bus_query_end:
                ctime = datetime.now()
                try:
                    ext = json.loads(each['Ext'])

                    if ext['ETime'] < ctime.timestamp():
                        ext['EMark'] = 1
                        # 已过末班发车时间
                        update_collect_2.append([2, json.dumps(ext), each['LineID']])

                except TypeError:
                    print(f"WebData/{self.target_db}/{each['LineID']}:{each['Line']}/Ext数据缺失!已补充")
                    # 数据补足
                    ctime = datetime.now()
                    s_clock = datetime.strptime(each['STime'], "%H:%M")
                    e_clock = datetime.strptime(each['ETime'], "%H:%M")
                    stime = datetime(year=ctime.year, month=ctime.month, day=ctime.day,
                                     hour=s_clock.hour, minute=s_clock.minute)
                    etime = datetime(year=ctime.year, month=ctime.month, day=ctime.day,
                                     hour=e_clock.hour, minute=e_clock.minute)
                    time_json = {"STime": stime.timestamp(),
                                 "ETime": etime.timestamp(),
                                 "EMark": 0}
                    update_collect_2.append([2, json.dumps(time_json), each['LineID']])

            # 更新Model数据
            print(update_collect_2)
            if len(update_collect_2) > 0:
                WebDate_operate(
                    table="amap", data=update_collect_2).update(
                    query_row="LineID", target_row1="Model", target_row2="Ext")

        # 二筛——符合范围
        bus_data_collect = []
        bus_data_no = {}
        sql_all = f" where Model = 1 or Model = 2"
        bus_query_all = WebDate_operate(self.target_db).fetchall(sql_all)
        # print(bus_query_all)

        if len(bus_query_all) > 0:
            bus_data_collect, bus_data_no = Request_Web("amap").thread_connect(bus_query_all)
        # for line in bus_query_all:
        #     bus_data_collect, bus_data_no = Request_Filter.web_connect(line, bus_data_collect, bus_data_no)

        # 三筛——清除结束运营线路
        update_collect_3 = []
        sql_extra = f" where Model = 2"
        bus_query_extra = WebDate_operate(self.target_db).fetchall(sql_extra)
        if len(bus_query_extra) != 0:
            for each in bus_query_extra:
                ext = json.loads(each['Ext'])

                try:
                    var = bus_data_no[each['LineID']]
                    ext['EMark'] += 1
                    # print(ext['EMark'])
                except KeyError as reason:
                    ext['EMark'] = 1

                if ext['EMark'] >= 4:
                    update_collect_3.append([5, None, each['LineID']])
                elif json.dumps(ext) != each['Ext']:
                    update_collect_3.append([2, json.dumps(ext), each['LineID']])

            # 更新Model数据
            print(update_collect_3)
            if len(update_collect_3) > 0:
                WebDate_operate(
                    table="amap", data=update_collect_3).update(
                    query_row="LineID", target_row1="Model", target_row2="Ext")

        return bus_data_collect

    def web_night_normal(self):
        """
        适用范围：跨日期线路
        :return:数据列表
        """
        ctime = datetime.now()
        hour = ctime.hour
        query_collect = []

        # 初筛——待启用数据
        update_collect_1 = []
        sql_start = f" where STime_H <= {hour + 1} and ETime_H > {hour - 24} and Model = 15"
        bus_query_st = WebDate_operate(self.target_db).fetchall(sql_start)
        if len(bus_query_st) != 0:
            for each in bus_query_st:
                ctime = datetime.now()
                s_clock = datetime.strptime(each['STime'], "%H:%M")
                e_clock = datetime.strptime(each['ETime'], "%H:%M")
                stime = datetime(year=ctime.year, month=ctime.month, day=ctime.day,
                                 hour=s_clock.hour, minute=s_clock.minute)
                etime = datetime(year=ctime.year, month=ctime.month, day=ctime.day,
                                 hour=e_clock.hour, minute=e_clock.minute) + timedelta(days=1)
                # print(stime,etime)
                # print(stime - timedelta(hours=1))
                # print(ctime)

                if stime - timedelta(hours=1) < ctime:
                    if each['Ext'] is None:
                        time_json = {"STime": stime.timestamp(),
                                     "ETime": etime.timestamp(),
                                     "EMark": 0}
                    else:
                        time_json = json.loads(each['Ext'])
                        time_json['STime'] = stime.timestamp()
                        time_json["ETime"] = etime.timestamp()
                        time_json['EMark'] = 0

                    update_collect_1.append([11, json.dumps(time_json), each['LineID']])
            # 更新Model数据
            print(update_collect_1)
            if len(update_collect_1) > 0:
                WebDate_operate(
                    table="amap", data=update_collect_1).update(
                    query_row="LineID", target_row1="Model", target_row2="Ext")

        # 初筛——即将结束运营线路
        update_collect_2 = []
        sql_end = f" where ETime_H <= {hour} and Model = 11"
        bus_query_end = WebDate_operate(self.target_db).fetchall(sql_end)
        if len(bus_query_end) != 0:
            for each in bus_query_end:
                ctime = datetime.now()
                try:
                    ext = json.loads(each['Ext'])

                    if ext['ETime'] < ctime.timestamp():
                        ext['EMark'] = 1
                        # 已过末班发车时间
                        update_collect_2.append([12, json.dumps(ext), each['LineID']])

                except TypeError:
                    print(f"WebData/{self.target_db}/   {each['LineID']}:{each['Line']}/Ext数据缺失!已补充")
                    # 数据补足
                    ctime = datetime.now()
                    s_clock = datetime.strptime(each['STime'], "%H:%M")
                    e_clock = datetime.strptime(each['ETime'], "%H:%M")
                    stime = datetime(year=ctime.year, month=ctime.month, day=ctime.day,
                                     hour=s_clock.hour, minute=s_clock.minute)
                    etime = datetime(year=ctime.year, month=ctime.month, day=ctime.day,
                                     hour=e_clock.hour, minute=e_clock.minute)
                    if ctime.hour > 12:
                        etime = etime + timedelta(days=1)
                    elif ctime.hour < 12:
                        stime = stime - timedelta(days=1)

                    time_json = {"STime": stime.timestamp(),
                                 "ETime": etime.timestamp(),
                                 "EMark": 0}
                    update_collect_2.append([2, json.dumps(time_json), each['LineID']])
            # 更新Model数据
            print(update_collect_2)
            if len(update_collect_2) > 0:
                WebDate_operate(
                    table="amap", data=update_collect_2).update(
                    query_row="LineID", target_row1="Model", target_row2="Ext")

        # 二筛——符合范围
        bus_data_collect = []
        bus_data_no = {}
        sql_all = f" where Model = 11 or Model = 12"
        bus_query_all = WebDate_operate(self.target_db).fetchall(sql_all)
        # print(bus_query_all)

        if len(bus_query_all) > 0:
            bus_data_collect, bus_data_no = Request_Web("amap").thread_connect(bus_query_all)
        # for line in bus_query_all:
        #     bus_data_collect, bus_data_no = Request_Filter.web_connect(line, bus_data_collect, bus_data_no)

        # 三筛——清除结束运营线路
        update_collect_3 = []
        sql_extra = f" where Model = 12"
        bus_query_extra = WebDate_operate(self.target_db).fetchall(sql_extra)
        if len(bus_query_extra) != 0:
            for each in bus_query_extra:
                ext = json.loads(each['Ext'])

                try:
                    var = bus_data_no[each['LineID']]
                    ext['EMark'] += 1
                except KeyError as reason:
                    ext['EMark'] = 1

                if ext['EMark'] >= 4:
                    update_collect_3.append([15, None, each['LineID']])
                elif json.dumps(ext) != each['Ext']:
                    update_collect_3.append([12, json.dumps(ext), each['LineID']])

            # 更新Model数据
            print(update_collect_3)
            if len(update_collect_3) > 0:
                WebDate_operate(
                    table="amap", data=update_collect_3).update(
                    query_row="LineID", target_row1="Model", target_row2="Ext")

        return bus_data_collect


class Request_Web:
    bus_data_no = {}
    bus_data_collect = []
    Line_List = []
    Proxies_List: list = []
    pool_sema = threading.BoundedSemaphore(value=parameter.lq_thread_num)  # 线程并发数

    def __init__(self, target_db=None):
        self.target_db = target_db

    @staticmethod
    def Proxies(file, modify=False):
        Request = open(proj_path + f'bus_web/DateFile/Proxies/{file}', mode='r')
        L = Request.readlines()
        for i in list(L):
            if i.find("*") > 0:
                L.remove(i)
        Request_Web.Proxies_List = L
        print(Request_Web.Proxies_List)

    @staticmethod
    def web_connect(Line_List, lock, Proxies=None):
        with Request_Web.pool_sema:
            bus_bad_line = []
            for line in Line_List:
                print(line['Line'])  # 输出线名
                receive, code = Amap_webdata(line['Line'], line['Direction'], line['Ent'], line['In'],
                                             line['Csid']).data_receive(Proxies)
                if code == 200:
                    # 正常响应
                    Request_Web.bus_data_collect.extend(receive)
                elif code == 201:
                    # 无数据
                    Request_Web.bus_data_no[line['LineID']] = line['Line']
                elif code == 203:
                    # 备用，处理代理ip
                    bus_bad_line.append(line)
                else:
                    # 其他特殊情况
                    print(f'服务器代码{code}')
                print("_______________")

            lock.acquire()
            Request_Web.Line_List.extend(bus_bad_line)
            bus_bad_line.clear()
            if len(bus_bad_line) > parameter.lq_get_num * 0.6:
                try:
                    # ip失效通知
                    Request_Web.Proxies_List[Request_Web.Proxies_List.index(Proxies)] = f'*{Proxies}'
                    append = {'class': 100, 'msg': f'代理IP{Proxies}失效', 'cite': Line_List.web_connect.__name__}
                    msg = {'type': 'ERROR_LOG', 'code': 'ERROR_PROXIES', 'time': int(time.time() * 1000),
                           'append': append}
                    line_message.MSG_IN(msg)
                finally:
                    pass
            lock.release()

    def thread_connect(self, Line_List: list, Proxies_List: list = None):
        Request_Web.bus_data_no.clear()  # 清空上次循环
        Request_Web.bus_data_collect.clear()  # 清空上次循环
        Request_Web.Line_List = Line_List
        separate_len = parameter.lq_get_num  # 每次抽取线路数量
        thread_end = True
        if not Proxies_List:
            Request_Web.Proxies(f'{self.target_db}_Proxies.txt')

        lock = threading.Lock()

        while thread_end:
            threads = []
            while len(Request_Web.Line_List):
                Target_List = Request_Web.Line_List[0:separate_len]
                if len(Target_List) > 0:
                    del Request_Web.Line_List[0:separate_len]
                    T = threading.Thread(target=Request_Web().web_connect,
                                         args=(Target_List, lock, choice(Request_Web.Proxies_List)))
                    threads.append(T)
                    T.start()
                time.sleep(1)

            for T in threads:
                T.join()

            if len(Request_Web.Line_List) == 0:
                thread_end = False

        return Request_Web.bus_data_collect, Request_Web.bus_data_no
