import asyncio
import os

from bus_web.Defin.sqlite_define import IDInfo_operate

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

    def yield_Object(self):
        Arg_List = []   # 额外参数
        while True:
            OP = '【加*项目需填写参数】'
            for Index in list(self.Struct):
                OP = OP + f'\n{Index}|' + self.Sentence[Index]

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
    def LAST_RUN_TIME(Arg_List):
        # res = IDInfo_operate(data=int(Arg_List[0])).retrieve(target_row="ID")
        return Arg_List



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
