import asyncio
import json
import os
from datetime import datetime

from bus_web.Defin.sqlite_define import IDInfo_operate, IDHistory_operate, IDSupport_operate

cur_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
proj_path = cur_path[:cur_path.find('qq_connect')]


class QA:
    def __init__(self, Struct, Sentence, Method):
        """
        :param Struct: {1:{11:{111:x,112:x}, 2:x, 3:{B1,B2,B3}},4:41}
        :param Sentence: {}
        """
        self.Struct: dict = Struct
        self.Sentence: dict = Sentence
        self.Method: dict = Method

    def yield_Object(self, **kwargs):
        Arg_List = []  # 额外参数
        while True:
            OP = '【加*项目需填写参数】'
            for Index in list(self.Struct):
                OP = OP + f'\n{Index}|' + self.Sentence[Index]

            if kwargs['arg_list'] is not None and len(self.Struct) == 1:
                # 只有单索引
                Input_Index = list(self.Struct)[0]
                Input_args = kwargs['arg_list'][0]
                if len(kwargs['arg_list']) > 1:
                    del kwargs['arg_list'][0]
                else:
                    kwargs['arg_list'] = None
            else:
                Input_Index, Input_args = yield OP  # 返回当前问题

            Arg_List.append(Input_args)
            if Input_Index not in list(self.Struct):
                return '索引错误，结束查询'
            else:
                if self.Sentence[Input_Index].find('*') > 0 and Input_args is None:
                    return '未填入需求参数，查询失败'
                self.Struct = self.Struct[Input_Index]
                if type(self.Struct) is str:
                    return eval(f"Run_Method.{self.Method[self.Struct]}({Arg_List})")  # 返回目标函数结构


class Run_Method:
    @staticmethod
    def FT(timestamp, HM=True):
        if HM:
            return datetime.fromtimestamp(int(timestamp) / 1000).strftime("%Y-%m-%d %H:%M")
        else:
            return datetime.fromtimestamp(int(timestamp) / 1000).strftime("%Y-%m-%d")

    @staticmethod
    def LAST_RUN_TIME(Arg_List):
        # res = IDInfo_operate(data=int(Arg_List[0])).retrieve(target_row="ID")
        return Arg_List

    @staticmethod
    def BUS_STATE(Arg_List):
        Str = ''
        Result = IDInfo_operate(data=int(Arg_List[0])).retrieve(target_row="ID")
        for bus in Result:
            Str = Str + (f'{bus["ID"]}:{bus["State"]},车牌{bus["Card"]}，归属于{bus["BLine"]}，最后记录于{bus["Line"]}，'
                         f'时间{Run_Method.FT(bus["LRTime"])}\n')
        return Str if Str is not None else '无相关数据'

    @staticmethod
    def BUS_OPERATE_HIS(Arg_List):
        Str = ''
        Result = IDHistory_operate(data=int(Arg_List[0])).retrieve(target_row="ID")
        for bus in Result:
            LineHis = json.loads(bus["LineHis"])
            LineHis_S = json.loads(bus["LineHis_S"])
            Str = Str + f'{bus["ID"]}：'
            Str = Str + f'[商务车]' if LineHis["business"] is True else Str
            Str = Str + f'[夜班车]' if LineHis["night"] is True else Str
            Str = Str + f'[支援车]' if LineHis["support"] is True else Str
            Str = Str + '历史运营线路：'
            Lines = ''
            for Line in LineHis_S:
                Lines = Lines + '、' + Line if len(Lines) > 0 else Line
            Str = Str + Lines + f'，最后运营于{LineHis["data"]["latest"]}，记录于{Run_Method.FT(LineHis["timestamp"])}\n'
        return Str if Str is not None else '无相关数据'

    @staticmethod
    def BUS_BELONG_HIS(Arg_List):
        Str = ''
        Result = IDHistory_operate(data=int(Arg_List[0])).retrieve(target_row="ID")
        for bus in Result:
            BelongHis = json.loads(bus["BelongHis"])
            Str = Str + f'{bus["ID"]}：归属于{BelongHis["BelLine"]}，'
            Str = Str + '车辆配属历史：'
            Lines = ''
            for HIS in BelongHis["BelHis"]:
                S = f'[{HIS[0]}]:'
                del HIS[0]
                for H in HIS:
                    S = S + H + '~' if (HIS.index(H)-1) % 2 == 1 else S + H
                if len(HIS) % 2 == 1:
                    S = S + '今'
                Lines = Lines + S + ';'
            Str = Str + Lines + f'\n'
        return Str if Str is not None else '无相关数据'

    @staticmethod
    def BUS_SUPPORT_HIS(Arg_List):
        Str = ''
        Result = IDSupport_operate(data=int(Arg_List[0])).retrieve(target_row="ID")
        for bus in Result:
            Time = json.loads(bus["Time"])
            for L in Time:
                Str = Str + f'[{L}]:'
                if len(Time[L]) >= 3:
                    Str = Str + f'{Time[L][-3]}、{Time[L][-2]}、{Time[L][-1]};\n'
                elif len(Time[L]) >= 2:
                    Str = Str + f'{Time[L][-2]}、{Time[L][-1]};\n'
                elif len(Time[L]) >= 1:
                    Str = Str + f'{Time[L][-1]};\n'
            Str = Str + '(只展示最近三次记录)'

        return Str if Str is not None else '无相关数据'

    # async def _run(self):
    #     loop = asyncio.get_event_loop()
    #     self.queue = asyncio.Queue(loop=loop)
    #     loop.create_task(self.ws_event())
    #     loop.create_task(self.event_runner())
    #
    # def run(self):
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(self._run())
    #     loop.run_forever()
