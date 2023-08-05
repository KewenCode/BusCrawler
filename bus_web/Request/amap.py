import copy
import json
import os
import time

cur_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
proj_path = cur_path[:cur_path.find('bus_web')]

from bus_web.Message import line_message
from bus_web.Operate.data_operate import BusIdData_Operate, OperateData_Operate
from bus_web.Operate.request_operate import Request_Filter
from bus_web.Operate.support_operate import Support_Operate

line_message._init()


def amap_main():
    """web数据库连接"""
    gps_day = copy.deepcopy(Request_Filter("amap").web_day_normal())
    gps_night = copy.deepcopy(Request_Filter("amap").web_night_normal())
    bus_data_collect = gps_day + gps_night
    """数据初筛，返回最新值"""
    data_list1 = BusIdData_Operate(bus_data_collect).main_operate()
    support_list = BusIdData_Operate(data_list1).history_operate()
    Support_Operate(support_list).data_update()

    # append = {'class': 100, 'his': '2023-07-23', 'support': '1路',
    #           'id': '57001', 'line': '2路', 'direction': 1}
    # msg = {'type': 'LINE_LOG', 'code': 'LINE_SUPPORT', 'time': 1690084947000,
    #        'append': append}
    # line_message.MSG_IN(msg)
    # line_message.Tools.Print_Msg()

    if len(gps_day) > 0:
        OperateData_Operate(data_list=gps_day).main_operate_day()
    if len(gps_night) > 0:
        OperateData_Operate(data_list=gps_night).main_operate_night()


def amap_loop(event=None):
    stop_mark_json = {'amap_loop': True}
    while stop_mark_json['amap_loop']:
        amap_main()

        line_message.Tools.Send_Msg()  # 发送消息
        line_message.Tools.Clear_Msg()
        line_message.Tools.File_Write()

        dt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        dx = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time() + 60 * 5)))
        print(f"当前时间：{dt}\n下一次运行时间：{dx}")
        time.sleep(60 * 5)
        stop_mark_file = open(proj_path + 'bus_web/DateFile/Temp/Temp_Mark.txt', mode='r')
        stop_mark_json = json.loads(stop_mark_file.read())
        stop_mark_file.close()

    if event:
        event.set()  # reset开始标记
        event.clear()
        event.wait()  # 等待reset结束

    print("amap运行结束")


def amap_reset(event=None):
    if event:
        event.wait()  # 等待loop结束

    file = open(proj_path + 'bus_web/DateFile/Temp/Temp_Mark.txt', mode='r+')
    stop_mark = json.loads(file.read())
    file.close()
    file = open(proj_path + 'bus_web/DateFile/Temp/Temp_Mark.txt', mode='w+')
    stop_mark['amap_loop'] = True
    file.write(json.dumps(stop_mark))
    file.close()
    print('mark success reset')

    if event:
        event.set()  # loop开始标记


def amap_stop():
    file = open(proj_path + 'bus_web/DateFile/Temp/Temp_Mark.txt', mode='r+')
    stop_mark = json.loads(file.read())
    file.close()
    file = open(proj_path + 'bus_web/DateFile/Temp/Temp_Mark.txt', mode='w+')
    stop_mark['amap_loop'] = False
    file.write(json.dumps(stop_mark))
    file.close()
    print('mark success set end')


if __name__ == '__main__':
    # amap_main()
    amap_loop()

# print("++++")
# temp_id_collect = [(359471, "运营", "53路"), (628041, '运营', '206路')]
# test = IDInfo_operate("IDInfor",temp_id_collect)
# print(f"待批量插入{len(temp_id_collect)}条数据")
# print(f"批量插入{test.batch_insert()}条数据")

# test = IDInfo_operate(first="ID", data=9471)
# all_data = test.retrieve()
# for item in all_data:
#     print(item)

# print("++++")
# for each in bus_data_collect:
#     print(each)
