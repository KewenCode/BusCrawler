import json
import os



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
