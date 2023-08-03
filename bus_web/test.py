import ast
import calendar
import json
import os
import random
import time
# import re
# import string
# import time
from datetime import date, datetime, timedelta

# import requests
# from fake_useragent import UserAgent
#
# from bus_web.Defin.data_define import parameter
# from bus_web.Defin.web_define import Chelaile_webdata
# from bus_web.Operate.request_operate import limit_request
# from bus_web.Operate.support_operate import Support_Operate
# from bus_web.Request.amap import amap_loop
# from bus_web.Request.proxy_ip import request_header
# from qq_connect.bot_sendmsg import http

# http(end_str='/send_msg', Group=826224229, msg=f"{'ceshi'}").http_get()

# Chelaile_webdata('Y1路', 1, '0025114984337', '025-1312').data_receive()

# cutime = datetime.now()
# print(cutime.strftime('%Y%m%d'))
# stime = datetime.strptime("23:00", "%H:%M")
# s = datetime(year=cutime.year, month=cutime.month, day=cutime.day+1, hour=stime.hour, minute=stime.minute)
# print(s)
# plus = timedelta(hours=12, seconds=60, microseconds=500)
# print(cutime)
# a= {'s': 1687789200.0}
# print(len(a))
# print(a['d'])
# print(cutime.timestamp())
# print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M'))
# print(a['s'] < cutime.timestamp())
# print((datetime.now() + timedelta(minutes=20)).timestamp()*1000)

# limit_request("amap").web_day_normal()

# Support_Operate(test).data_fresh()
# test = time.localtime(1688635617966/1000)
# print(datetime.strptime("17:30", '%H:%M'))
# a = datetime.fromtimestamp(1690379045999/1000).strftime('%Y-%m-%d %H:%M')
# print(a)
# print(datetime.strptime(a, '%H:%M'))
# print(timedelta(minutes=30))

# now = datetime.now()
# last_day = calendar.monthrange(now.year, now.month)[1]
# print(last_day)

# print(date.today())
# print(datetime.strftime(datetime.now(), "%Y-%m"))
# print((datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d'))
# print((datetime.now()).strftime('%Y%m%d'))

# b = []
a = [11, 2, 2, 3, 4, 5]
# for L in list(a):
#     print(L)
#     if L not in b:
#         b.append(L)
#     else:
#         a.remove(L)
print(random.choice(a))
# print(a[1:3])
# del a[1:3]
# print(a)
# print(b)

# a = {'a':1, 'b':2}
# b = {'c':1, 'd':2}
# a.update(b)
# print(a)

# for i in range(10):
#     print(i)


# a = {123: {'L': 2, 'D': 1}}
# if 123 in list(a) and a[123]['L'] == 1 and a[123]['D'] == 2:
#     print(1)
# else:
#     print(2)

# def stop():
#     file = open('DateFile/Temp/Temp_Mark.txt', mode='r+')
#     stop_mark = json.loads(file.read())
#     file.close()
#     file = open('DateFile/Temp/Temp_Mark.txt', mode='w+')
#     stop_mark['amap_loop'] = False
#     file.write(json.dumps(stop_mark))
#     file.close()
#     print('成功结束')
#
#
# stop()


# cur_path = os.path.abspath(os.path.dirname(__file__))   # 获取当前文件的目录
# proj_path = cur_path[:cur_path.find('bus_web')]
# print(proj_path)