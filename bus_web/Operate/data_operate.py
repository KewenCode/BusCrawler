import ast
import hashlib
import json
import time
from datetime import datetime, date, timedelta

from bus_web.Defin.data_define import parameter
from bus_web.Defin.sqlite_define import IDInfo_operate, IDHistory_operate, OperateDate_operate, WebDate_operate
from bus_web.Defin.web_define import Chelaile_webdata
from bus_web.Message import line_message
from bus_web.Message.message_manage import container


class Data_operate:

    def main_operate(self) -> list:
        """
        主数据处理
        :return: 已记录车辆列表
        """
        pass

    def history_operate(self):
        """

        :return:
        """
        pass

    def history_state_operate(self, state) -> str:
        """
        1(营运)，2(公务车)，3(闲置)，4(待报废)，5(报废)，10(待上线)，11(转出)，12(不明)
        :param state: json字符串
        :return: json字符串
        """
        pass

    def history_line_operate(self, line_list, line_json, belong_list) -> (str, str):
        pass

    def history_belong_operate(self, line_json, belong_list, belong_json) -> list:
        pass


class BusIdData_Operate(Data_operate):

    def __init__(self, data_list):
        self.data_list = data_list

    def main_operate(self) -> list:
        IDInfo_Nonecord = []
        IDHistory_Norecord = []
        record = []
        record_time = []

        for each in self.data_list:
            res = IDInfo_operate(data=int(each.gps_id)).retrieve(target_row="ID")
            if len(res) == 0:
                # 新车辆首次记录
                print(f"未记录车辆数据，{each.line_name}{each.gps_id}，准备插入数据库")
                # IDInfo数据首次记录
                IDInfo_Nonecord.append([each.gps_id, "运营", None, each.line_name, None, each.timestamp])
                # IDHistory数据首次记录 插入默认值
                HO_None = History_operate(
                    line=each.line_name, timestamp=each.timestamp, bus_id=each.gps_id, direction=each.direction)
                list_line, json_line = \
                    HO_None.history_line_operate(line_list=None, line_json=None, belong_list=None)
                list_belong, json_belong, support_line = \
                    HO_None.history_belong_operate(line_json=None, belong_list=None, belong_json=None)
                IDHistory_Norecord.append([each.gps_id,
                                           each.timestamp,
                                           HO_None.history_state_operate(state=None),
                                           list_line, json_line,
                                           list_belong, json_belong])
            else:
                # 更新车辆记录时间，输出list
                record.append([each.line_name, each.timestamp, each.gps_id])
                record_time.append([each.line_name, each.timestamp, each.gps_id, each.direction])

        if len(IDInfo_Nonecord) > 0:
            insert1 = IDInfo_operate(data=IDInfo_Nonecord)
            insert2 = IDHistory_operate(data=IDHistory_Norecord)
            print(f"+++---+++---+++\n"
                  f"IDInfo新记录{insert1.batch_insert()}条数据\n"
                  f"IDHistory新记录{insert2.batch_insert()}条数据\n"
                  f"数据对象：{IDHistory_Norecord}\n"
                  f"+++---+++---+++")

        # IDInfo记录时间更新
        IDInfo_operate(record).update(query_row="ID", target_row1="line", target_row2="LRTime")

        return record_time

    def history_operate(self):
        history_update_collect, support_collect = BusIdData_Operate.ho_tools.history_operate_delta(self.data_list)

        IDHistory_operate(history_update_collect).update(query_row='ID',
                                                         target_row1='StateHis',
                                                         target_row2='LineHis_S',
                                                         target_row3="LineHis",
                                                         target_row4="BelongHis_S",
                                                         target_row5="BelongHis"
                                                         )

        return support_collect

    class ho_tools:
        @staticmethod
        def history_operate_delta(data_list, CLL=True) -> (list, list):
            huc_c: list = []
            sc_c: list = []
            huc: list = []
            sc: list = []
            support_check: list = []

            for each in data_list:
                """
                each[0]: line
                each[1]: timestamp
                each[2]: ID
                each[3]: direction
                """
                history_result = IDHistory_operate(each[2]).retrieve("ID")

                HO = History_operate(line=each[0], timestamp=each[1], bus_id=each[2], direction=each[3])
                if len(history_result) == 0:
                    # IDHistory未记录数据处理
                    list_line, json_line = \
                        HO.history_line_operate(line_list=None, line_json=None, belong_list=None)
                    list_belong, json_belong, support_line = \
                        HO.history_belong_operate(line_json=None, belong_list=None, belong_json=None)
                    IDHistory_operate(data=[[each[2],
                                             each[1],
                                             HO.history_state_operate(state=None),
                                             list_line, json_line,
                                             list_belong, json_belong
                                             ]]).batch_insert()
                else:
                    try:
                        # 状态处理
                        json_state = history_result[0]["StateHis"]
                        # 历史线路
                        list_line = history_result[0]["LineHis_S"]
                        json_line = json.loads(history_result[0]["LineHis"])
                        # 历史归属
                        list_belong = history_result[0]["BelongHis_S"]
                        json_belong = json.loads(history_result[0]["BelongHis"])

                        # 运用历史不一致判定
                        if json_line['data']['latest'] != each[0] and CLL is True:
                            line_list = [json_belong['BelLine']]
                            # 判定新线路是否被记录
                            if each[0] not in json_belong['SupportLine']:
                                line_list = [json_belong['BelLine'], each[0]]
                            send = {'info': each,
                                    'lines': line_list + json_belong['SupportLine'] + [each[0]]}
                            support_check.append(send)
                            continue

                        # cll支援数据提取模块
                        if json_belong['BelLine'] != each[0] and CLL is True:
                            # 今日已记录不再核查
                            try:
                                if json_belong['SupportLine_R'][each[0]] != str(date.today()):
                                    send = {'info': each,
                                            'lines': [json_belong['BelLine']] + json_belong['SupportLine'] + [each[0]]}
                                    support_check.append(send)
                                    continue
                            except:
                                send = {'info': each,
                                        'lines': [json_belong['BelLine']] + json_belong['SupportLine'] + [each[0]]}
                                support_check.append(send)
                                continue

                        # 常规数据流程
                        json_state = \
                            HO.history_state_operate(state=json_state)
                        list_line, json_line = \
                            HO.history_line_operate(line_list=list_line, line_json=json_line, belong_list=list_belong)
                        list_belong, json_belong, support_line = \
                            HO.history_belong_operate(line_json=json_line, belong_list=list_belong,
                                                      belong_json=json_belong)

                        # 数据更新
                        huc.append([json_state, list_line, json_line, list_belong, json_belong, each[2]])
                        # 支援数据判空收集处理
                        if len(support_line) != 0:
                            sc.append(support_line)

                    except IndexError as reason:
                        print(f"{each[2]}：IDHistory筛查出现漏网之鱼，注意核查数据库是否空缺。{reason}")

            # 支援车辆核验
            if len(support_check) > 0 and CLL is True:
                # 剔除重复数据
                Target = []
                for L in list(support_check):
                    if L['info'][2] not in Target:
                        Target.append(L['info'][2])
                    else:
                        support_check.remove(L)

                print("_______________")
                print(f"核验对象：{Target}")
                huc_c, sc_c, IDInfo_record = BusIdData_Operate.ho_tools.cll_su_check(support_check)
                print("_______________")
                # 存在即更新IDInfo
                IDInfo_operate(IDInfo_record).update(query_row="ID", target_row1="line", target_row2="LRTime")
            return huc + huc_c, sc + sc_c

        @staticmethod
        def cll_su_check(da_list: list) -> (list, list, list):
            """
            车来了支援车辆核验
            :param da_list: 数据列表
            :return: history_update_collect, support_collect
            """
            union_dict = {}
            update_list = []
            IDInfo_record = []

            def dict_insert(Line, Direction, Id, Line_s: list):
                """
                :param Line: 线路名称
                :param Direction: 方向
                :param Id: 车号
                :param Line_s: 待选线路，list[0]为归属线路
                :return:
                """
                try:
                    union_dict[Line]
                except:
                    union_dict[Line] = {}

                try:
                    union_dict[Line][Direction]
                except:
                    union_dict[Line][Direction] = {}

                union_dict[Line][Direction][Id] = Line_s  # 末尾加Line遍历循环

            # 读取越级临时文件
            Temp_Request = open('DateFile/Temp/Temp_Request.txt', mode='r+')
            TR_json = json.loads(Temp_Request.read())  # 上一循环文件
            Temp_Request.close()
            TR_dict = {
                'Expire': int((datetime.now() + timedelta(minutes=parameter.od_timestamp_interval)).timestamp() * 1000)}
            # 本次循环有效时间记录
            if datetime.now().timestamp() * 1000 > TR_json['Expire']:
                TR_json = {}

            for L in da_list:
                if L['info'][2] in list(TR_json) \
                        and TR_json[L['info'][2]]['RLine'] == L['info'][0] \
                        and TR_json[L['info'][2]]['Direction'] == L['info'][3]:
                    update_list.append([TR_json[L['info'][2]]['BLine'], L['info'][1], L['info'][2], L['info'][3]])
                    TR_dict[L['info'][2]] = TR_json[L['info'][2]]  # 越级记录
                else:
                    dict_insert(L['info'][0], L['info'][3], L['info'][2], L['lines'])

            code_break = {}
            while len(union_dict) > 0:
                # 存在即继续遍历
                for lines in list(union_dict):
                    for directions in list(union_dict[lines]):
                        receive = []
                        sql = f' WHERE "Line" = "{lines}" AND "Direction" = "{directions}"'
                        print(sql)
                        try:
                            cll_query = WebDate_operate('chelaile').fetchall(sql)[0]
                            receive, code = Chelaile_webdata(lines, cll_query['Direction'],
                                                             cll_query['QueryID'],
                                                             cll_query['stationId']).data_receive()
                            time.sleep(3)
                        except:
                            code = 404

                        if code > 201:
                            print(f'车来了数据异常，本次循环取消记录，+1')
                            # 停止循环
                            if f"{lines}/{directions}" in list(code_break):
                                if code_break[f"{lines}/{directions}"] > 3:
                                    union_dict[lines].pop(directions)
                                else:
                                    code_break[f"{lines}/{directions}"] += 1
                                    time.sleep(5)  # 规避检测
                            else:
                                code_break[f"{lines}/{directions}"] = 1
                            break

                        for each in receive:
                            if each.gps_id in list(union_dict[lines][directions]):
                                # 正常记录
                                update_list.append([each.line_name, each.timestamp, each.gps_id, each.direction])
                                TR_dict[each.gps_id] = {'RLine': union_dict[lines][directions][each.gps_id][-1],
                                                        'BLine': lines,
                                                        'Direction': directions}  # 越级记录
                                union_dict[lines][directions].pop(each.gps_id)  # 删除对应记录
                                IDInfo_record.append([each.line_name, each.timestamp, each.gps_id])
                                print(f'车来了核查成功:{each.gps_id}运行于{lines}')

                        if len(union_dict[lines][directions]) > 0:
                            # 未消除id赋值下一目标
                            for ids in list(union_dict[lines][directions]):
                                line_list = union_dict[lines][directions][ids]
                                line_list.remove(lines)  # remove每次只删除一个值
                                if len(line_list) == 1:  # list中只剩最后值——原线路
                                    print(f'{ids}疑似支援{line_list[0]},方向{directions}')
                                else:
                                    dict_insert(line_list[0], directions, ids, line_list)
                                union_dict[lines][directions].pop(ids)

                        if len(union_dict[lines][directions]) == 0:
                            union_dict[lines].pop(directions)

                    if len(union_dict[lines]) == 0:
                        union_dict.pop(lines)

            Temp_Request = open('DateFile/Temp/Temp_Request.txt', mode='w+')
            Temp_Request.write(json.dumps(TR_dict))
            Temp_Request.close()

            history_update_collect, support_collect = BusIdData_Operate.ho_tools.history_operate_delta(
                data_list=update_list, CLL=False)
            return history_update_collect, support_collect, IDInfo_record


class History_operate(Data_operate):

    def __init__(self, line, timestamp, bus_id, direction):
        self.Line = line
        self.Timestamp = timestamp
        self.Id = bus_id
        self.Direction = direction

    def history_state_operate(self, state) -> str:
        """
        1(营运)，2(公务车)，3(闲置)，4(待报废)，5(报废)，10(待上线)，11(转出)，12(不明)
        """
        if state is None:
            # 构建json
            new_json = {'state': 1, 'timestamp': self.Timestamp, 'former': [[1, self.Timestamp]]}
            print(f"{self.Id}：IDHistory/StateHis为新记录，注意核查数据库完整性。")
            return json.dumps(new_json)
        else:
            re_json = json.loads(state)
            # print(f"数据记录：{re_json}")
            if re_json['state'] == 1:
                re_json['timestamp'] = self.Timestamp  # 更新最后记录时间戳
            elif re_json['state'] == 2:
                re_json['timestamp'] = self.Timestamp  # 更新最后记录时间戳
            else:
                if re_json['former'][-1][0] == re_json['state']:
                    re_json['state'] = 1
                    re_json['former'][-1].append(self.Timestamp)
                    re_json['former'].append([1, self.Timestamp])
                    re_json['timestamp'] = self.Timestamp
                else:
                    print(f"IDHistory/StateHis数据错误！\n"
                          f"记录状态：{re_json['former'][-1][0]},记录时间：{re_json['former'][-1][1]}\n"
                          f"完整记录：{re_json['former']}")

        return json.dumps(re_json)

    def history_line_operate(self, line_list, line_json, belong_list) -> (str, str):
        if line_list is None and line_json is None:
            line_list = [self.Line]
            line_json = {'timestamp': self.Timestamp,
                         'night': 0, 'support': 0, 'business': 0,
                         'data': {'latest': self.Line, self.Line: [self.Timestamp]}}
            print(f"{self.Id}：IDHistory/LineHis为新记录，注意核查数据库完整性。")
        elif line_list is not None and line_json is not None:
            try:
                ast.literal_eval(line_list).index(self.Line)  # 查询存在
                # 格式转换
                line_list = ast.literal_eval(line_list)
                # line_json = json.loads(line_json)

                if line_json['data']['latest'] != self.Line:
                    line_json['data'][line_json['data']['latest']].append(line_json['timestamp'])  # 上一记录结束
                    line_json['timestamp'] = self.Timestamp  # 重置时间戳
                    line_json['data']['latest'] = self.Line  # 重置最后线路

                    # print(f"{self.Id}行走{self.Line}，上一次行驶时间为{line_json['data'][self.Line][-1]}")
                    belong_list = json.loads(belong_list)
                    if belong_list[0] != self.Line:
                        # 非原线行驶
                        append = {'class': 100, 'his': line_json['data'][self.Line][-1], 'support': self.Line,
                                  'id': self.Id, 'line': belong_list[0], 'direction': self.Direction}
                    else:
                        # 原线行驶
                        append = {'class': 200, 'his': line_json['data'][self.Line][-1], 'support': None,
                                  'id': self.Id, 'line': belong_list[0], 'direction': self.Direction}

                    msg = {'type': 'LINE_LOG', 'code': 'LINE_RUNNING', 'time': self.Timestamp,
                           'append': append}
                    line_message.MSG_IN(msg)

                    line_json['data'][self.Line].append(self.Timestamp)  # 添加纪录

                elif line_json['data']['latest'] == self.Line:
                    line_json['timestamp'] = self.Timestamp  # 重置时间戳
                else:
                    print(f"{self.Id}：IDHistory/LineHis出现未知错误。")

            except ValueError as reason:
                # print(f"{self.Id}首次行驶{self.Line}")
                belong_list = json.loads(belong_list)
                append = {'class': 100, 'his': None, 'support': self.Line,
                          'id': self.Id, 'line': belong_list[0], 'direction': self.Direction}
                msg = {'type': 'LINE_LOG', 'code': 'LINE_RUNNING', 'time': self.Timestamp, 'append': append}
                line_message.MSG_IN(msg)

                # 格式转换
                line_list = ast.literal_eval(line_list)
                # line_json = json.loads(line_json)

                line_list.append(self.Line)
                line_json['data'][line_json['data']['latest']].append(line_json['timestamp'])  # 上一记录结束
                line_json['timestamp'] = self.Timestamp  # 重置时间戳
                line_json['data']['latest'] = self.Line  # 重置最后线路
                line_json['data'][self.Line] = [self.Timestamp]  # 新纪录
        else:
            print(f"IDHistory/LineHis数据错误!"
                  f"{self.Line} {self.Id}\n"
                  f"LineHis_s:{line_list}\n"
                  f"LineHis:{line_json}\n"
                  f"--------")
            # 格式转换
            line_list = ast.literal_eval(line_list)
            # line_json = json.loads(line_json)

        return json.dumps(line_list), json.dumps(line_json)

    def history_belong_operate(self, line_json, belong_list, belong_json) -> (str, str, dict):
        support_line = []
        today = str(date.today())

        if belong_list is None and belong_json is None:
            belong_list = [self.Line]
            belong_json = {'BelLine': self.Line, 'TimePoint': self.Timestamp,
                           'SupportLine': [], 'SupportLine_R': {},
                           'BelHis': [[self.Line, today]]}
            print(f"{self.Id}：IDHistory/BelongHis为新记录，注意核查数据库完整性。")
            """
            SupportLine 支援线路待定参数
            SupportLine_R 历史出现时间 {‘xx路’:[xx-xx-xx,xx-xx-xx]}
            """
        elif belong_list is not None and belong_json is not None:
            his_day = "-"
            line_json = json.loads(line_json)
            belong_list = json.loads(belong_list)
            # belong_json = json.loads(belong_json)
            if belong_json['BelLine'] == self.Line:
                belong_json['TimePoint'] = self.Timestamp

            elif belong_json['BelLine'] != self.Line:
                if line_json['support'] == 0 or line_json['support'] == 1:
                    try:
                        belong_json['SupportLine'].index(self.Line)
                        # 已存在相应线路
                        his_day = belong_json['SupportLine_R'][self.Line]

                        if belong_json['SupportLine_R'][self.Line] != today:
                            # 今日首次记录修改已有日期
                            belong_json['SupportLine_R'][self.Line] = today
                            support_line = \
                                {"ID": self.Id, "Line": self.Line, "Day": today, "Type": line_json['support']}

                    except ValueError:
                        # 历史未支援 新插入数据
                        belong_json['SupportLine'].append(self.Line)
                        belong_json['SupportLine_R'][self.Line] = today
                        support_line = {"ID": self.Id, "Line": self.Line, "Day": today, "Type": line_json['support']}

                    if line_json['support'] == 0:
                        # 非日常支援
                        container.bus_data.append(
                            {'type': 'LINE', 'code': 'LINE_SUPPORT',
                             'state': 1, 'time': self.Timestamp,
                             'append': {'id': self.Id, 'line': belong_json['BelLine'],
                                        'support': self.Line, 'direction': self.Direction}
                             })
                        # print(f"{belong_json['BelLine']}{self.Id}:支援{self.Line}，上一次支援日期{his_day}")
                        append = {'class': 100, 'his': his_day, 'support': self.Line,
                                  'id': self.Id, 'line': belong_json['BelLine'], 'direction': self.Direction}
                        msg = {'type': 'LINE_LOG', 'code': 'LINE_SUPPORT', 'time': self.Timestamp,
                               'append': append}
                        line_message.MSG_IN(msg)
                    else:
                        # 日常支援车
                        if self.Line != belong_json['BelLine']:
                            # print(f"{self.Id}:日常支援{self.Line}，上一次支援日期{his_day}")
                            append = {'class': 100, 'his': his_day, 'support': self.Line,
                                      'id': self.Id, 'line': belong_json['BelLine'], 'direction': self.Direction}
                            msg = {'type': 'LINE_LOG', 'code': 'LINE_SUPPORT_DAILY', 'time': self.Timestamp,
                                   'append': append}
                            line_message.MSG_IN(msg)

                else:
                    print(f"IDHistory/LineHis/support数据错误!")
        else:
            print(f"IDHistory/BelongHis数据错误!\n"
                  f"{self.Line} {self.Id}\n"
                  f"BelongHis_s:{belong_list}\n"
                  f"BelongHis:{belong_json}\n"
                  f"--------")
            # 格式转换
            try:
                belong_list = json.loads(belong_list)
            except TypeError:
                belong_list = None
            belong_json = json.loads(belong_json)

        return json.dumps(belong_list), json.dumps(belong_json), support_line


class OperateData_Operate(Data_operate):

    def __init__(self, data_list=None, area=3201):
        """
        OperateData记录历史运营数据
        :param data_list: 传入数据列表
        :param area: 线路运营区域
        """
        self.area = area
        self.data_list = data_list

    class OperateData_Operate_tools:

        @staticmethod
        def index_md5(contain: str) -> str:
            m = hashlib.md5()
            m.update(contain.encode(encoding='UTF-8'))
            return m.hexdigest()

        @staticmethod
        def data_collect(data_list) -> dict:

            line_collect: dict = {}

            for each in data_list:

                each.timestamp = datetime.fromtimestamp(int(each.timestamp) / 1000).strftime("%H:%M")

                if line_collect.__contains__(each.line_name):
                    line: dict = line_collect[each.line_name]

                    if line.__contains__(each.direction):
                        direction: dict = line[each.direction]

                        if direction.__contains__(each.gps_id):
                            # 一条线两个相同ID？
                            print(f"{each.line_name}{each.gps_id}数据源疑似有误：")
                            if type(direction[each.gps_id]) is not list:
                                direction[each.gps_id] = [direction[each.gps_id]]
                            direction[each.gps_id].append(each.timestamp)
                        else:
                            direction[each.gps_id]: str = each.timestamp
                    else:
                        direction = line[each.direction] = {}
                        direction[each.gps_id]: str = each.timestamp
                else:
                    line = line_collect[each.line_name] = {}
                    direction = line[each.direction] = {}
                    direction[each.gps_id]: str = each.timestamp

            return line_collect

        @staticmethod
        def data_union(font_dict, add_dict) -> dict:
            pass

    # 日间线路
    def main_operate_day(self):
        update_collect = []
        insert_collect = []

        tools = OperateData_Operate.OperateData_Operate_tools
        data_collect: dict = tools.data_collect(data_list=self.data_list)
        for line in data_collect:
            for direction in data_collect[line]:
                index = tools.index_md5(f"{datetime.now().strftime('%Y%m%d')}/{self.area}/{line}/{direction}")
                receive: list = OperateDate_operate(index).retrieve('Index')
                if len(receive) == 0:
                    # 新线路添加
                    insert_collect.append(
                        [index, 3201, line, direction, date.today(), json.dumps(data_collect[line][direction])])
                else:
                    his_date: dict = json.loads(receive[0]['History'])

                    for bus_id in data_collect[line][direction]:
                        try:
                            # 初始str类型改为list类型
                            if type(his_date[bus_id]) is not list:
                                his_date[bus_id] = [[his_date[bus_id]]]

                            # 记录间隔小于od_timestamp_interval设定，自动覆盖
                            interval = timedelta(minutes=parameter.od_timestamp_interval)
                            last_time = datetime.strptime(his_date[bus_id][-1][-1], '%H:%M')
                            current_time = datetime.strptime(data_collect[line][direction][bus_id], '%H:%M')
                            if last_time + interval > current_time:
                                if len(his_date[bus_id][-1]) >= 2:
                                    # 修改末位记录
                                    his_date[bus_id][-1][-1] = data_collect[line][direction][bus_id]
                                else:
                                    his_date[bus_id][-1].append(data_collect[line][direction][bus_id])
                            else:
                                # 插入数据夹
                                his_date[bus_id].append([data_collect[line][direction][bus_id]])
                        except KeyError:
                            # 新车辆添加
                            his_date[bus_id] = [[data_collect[line][direction][bus_id]]]

                    update_collect.append([json.dumps(his_date), index])

        OperateDate_operate(insert_collect).batch_insert()
        OperateDate_operate(update_collect).update('Index', 'History')

    # 夜间线路，跨日计入上一天
    def main_operate_night(self):
        update_collect = []
        insert_collect = []
        hour = int(datetime.now().hour)
        day = date.today()
        if 0 <= hour <= 12:
            day = datetime.now() - timedelta(days=1)

        tools = OperateData_Operate.OperateData_Operate_tools
        data_collect: dict = tools.data_collect(data_list=self.data_list)
        for line in data_collect:
            for direction in data_collect[line]:

                index = tools.index_md5(f"{day.strftime('%Y%m%d')}/{self.area}/{line}/{direction}")
                receive: list = OperateDate_operate(index).retrieve('Index')
                if len(receive) == 0:
                    # 新线路添加
                    insert_collect.append(
                        [index, 3201, line, direction, day.strftime('%Y-%m-%d'),
                         json.dumps(data_collect[line][direction])])
                else:
                    his_date: dict = json.loads(receive[0]['History'])

                    for bus_id in data_collect[line][direction]:
                        try:
                            # 初始str类型改为list类型
                            if type(his_date[bus_id]) is not list:
                                his_date[bus_id] = [[his_date[bus_id]]]

                            # 记录间隔小于od_timestamp_interval设定，自动覆盖
                            interval = timedelta(minutes=parameter.od_timestamp_interval)
                            last_time = datetime.strptime(his_date[bus_id][-1][-1], '%H:%M')
                            current_time = datetime.strptime(data_collect[line][direction][bus_id], '%H:%M')
                            if last_time + interval > current_time:
                                if len(his_date[bus_id][-1]) >= 2:
                                    # 修改末位记录
                                    his_date[bus_id][-1][-1] = data_collect[line][direction][bus_id]
                                else:
                                    his_date[bus_id][-1].append(data_collect[line][direction][bus_id])
                            else:
                                # 插入数据夹
                                his_date[bus_id].append([data_collect[line][direction][bus_id]])
                        except KeyError:
                            # 新车辆添加
                            his_date[bus_id] = [[data_collect[line][direction][bus_id]]]

                    update_collect.append([json.dumps(his_date), index])

        OperateDate_operate(insert_collect).batch_insert()
        OperateDate_operate(update_collect).update('Index', 'History')
