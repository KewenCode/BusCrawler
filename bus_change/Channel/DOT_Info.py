import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta

import requests
from fake_useragent import UserAgent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from bus_change.Http_SendMsg import http

cur_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件的目录
proj_path = cur_path[:cur_path.find('bus_change')]


class input_date:
    @staticmethod
    def web_date():
        url = "http://jtj.nanjing.gov.cn/igs/front/search/publish/data/list.html?"
        data = {
            'index': 'wzqsearch-v20190124',
            'type': 'infomation',
            'siteId': 71,
            'pageSize': 20,
            'orderProperty': 'DOCRELTIME',
            'pageIndex': 1,
            'orderDirection': 'desc',
            'filter[SITEID]': 71,
            'filter[CHANNELID]': 28135,
            'filter[GROUPCAT]': 2063,
            'pageNumber': 1
        }
        headers = {
            # 'User-Agent': UserAgent().random #常见浏览器的请求头伪装（如：火狐,谷歌）
            'User-Agent': UserAgent().Chrome  # 谷歌浏览器
        }
        # proxies = {
        #     'http': 'http://101.43.93.67:7890',
        #     'https': 'http://101.43.93.67:7890'
        # }
        receive_date = {}
        insert_date = {}
        res_code = 0
        sleep_time = 5 * 60

        while res_code != 200:
            try:
                response = requests.get(url=url, params=data, timeout=1, headers=headers)
                response.close()
                if response.status_code == 200:
                    res_code = 200
                    receive_date = json.loads(response.text)
                    print('\033[31m可用\033[0m')
                else:
                    print('网站暂时不可用')
                    res_code = 200
                    sleep_time = 10 * 60
            except:
                print('交通局数据端口请求异常')
                time.sleep(30)
                sleep_time = 1 * 30

        if receive_date != {}:
            for each in receive_date['rows']:
                utc_data1 = each['DOCFIRSTPUBTIME']
                utc_date2 = datetime.strptime(utc_data1, "%Y-%m-%dT%H:%M:%S.%fZ")
                local_date = utc_date2 + timedelta(hours=8)
                local_date = datetime.strftime(local_date, "%Y-%m")

                try:
                    len(insert_date[local_date])
                except KeyError:
                    insert_date[local_date] = []

                table_num = 0
                for month in insert_date:
                    table_num += len(Web_date_operate(month).fetch_date(f'where "INDEXNO" is "{each["INDEXNO"]}"'))

                if table_num > 0:
                    pass
                else:
                    temp_str_list: list = each['DOCCONTENT'].replace(u'\u3000', '').split()
                    # 判断列表中是否有空值，并删除原数据
                    while len(each['DOCCONTENT']) != 0:
                        try:
                            temp_str_list.remove('')
                        except:
                            each['DOCCONTENT'] = ''
                    # 组成新字符串
                    for lines in temp_str_list:
                        if len(each['DOCCONTENT']) == 0:
                            each['DOCCONTENT'] = lines
                        else:
                            each['DOCCONTENT'] = each['DOCCONTENT'] + '\n' + lines

                    insert_date[local_date].append([each['INDEXNO'],
                                                    each['DOCFIRSTPUBTIME'],
                                                    each['DOCTITLE'],
                                                    each['DOCCONTENT'],
                                                    each['DOCPUBURL']])
                    print(f"{each['DOCTITLE']}{each['DOCCONTENT']}")
                    # 长消息分片，最长支持1750~1800
                    cq_receive = []
                    if len(each['DOCCONTENT']) > 1700:
                        split_char = ['一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、', '九、', '十、']
                        send_msg = ''

                        # 发送标题
                        receive = http(end_str='/send_msg', Group=826224229, msg=f"{each['DOCTITLE']}\n"
                                                                                 f"{each['DOCPUBURL']}").http_get()
                        cq_receive.append(receive)

                        # 分段发送内容
                        for line in temp_str_list:
                            cite = -1  # 标记分段点
                            for char in split_char:
                                cite = line.find(char)
                                if cite > -1:
                                    break

                            if cite == -1:
                                # 强制断点
                                if len(send_msg) > 1500:
                                    receive = http(end_str='/send_msg', Group=826224229, msg=f"{send_msg}").http_get()
                                    cq_receive.append(receive)
                                    send_msg = line
                                # 初始赋值
                                elif len(send_msg) == 0:
                                    send_msg = line
                                # 判断非空
                                elif line != '':
                                    send_msg = send_msg + '\n' + line
                            else:
                                # 存在分段，发送上一部分
                                receive = http(end_str='/send_msg', Group=826224229, msg=f"{send_msg}").http_get()
                                cq_receive.append(receive)
                                send_msg = line

                        # 未发送字符发送
                        if len(send_msg) > 0:
                            receive = http(end_str='/send_msg', Group=826224229, msg=f"{send_msg}").http_get()
                            cq_receive.append(receive)

                    else:
                        receive = http(end_str='/send_msg', Group=826224229, msg=f"{each['DOCTITLE']}\n"
                                                                                 f"{each['DOCPUBURL']}").http_get()
                        cq_receive.append(receive)
                        receive = http(end_str='/send_msg', Group=826224229, msg=f"{each['DOCCONTENT']}").http_get()
                        cq_receive.append(receive)
                    print(cq_receive)

            print(insert_date)
            for key in insert_date:
                Web_date_operate(table=key, data=insert_date[key]).batch_insert()

        return sleep_time


class Web_date_operate:

    @staticmethod
    def dict_factory(cursor, row):
        # 将游标获取的数据处理成字典返回
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __init__(self, table=datetime.strftime(datetime.now(), "%Y-%m"), data=None):
        """
        WebDate数据文件读取使用
        :param table:目标表单名称
        :param data:使用数据
        """
        if data is None:
            data = []
        self.target_db = proj_path + "bus_change/DateFile/ChangeInformation.db"  # 目标数据库
        self.table = table  # 目标表单
        self.date_list = data  # 数据文件

    def batch_insert(self) -> int:
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        batch_count = 0
        try:
            current.execute(f'CREATE TABLE IF NOT EXISTS "{self.table}" ( '
                            f'"INDEXNO"	TEXT NOT NULL UNIQUE,'
                            f'"DOCFIRSTPUBTIME"	TEXT,'
                            f'"DOCTITLE"	TEXT,'
                            f'"DOCCONTENT"	TEXT,'
                            f'"DOCPUBURL"	TEXT,'
                            f'PRIMARY KEY("INDEXNO"))')
            sql = f'insert into "{self.table}" values (?,?,?,?,?)'  # 其中问号为占位符
            batchInsert = current.executemany(sql, self.date_list)
            batch_count = batchInsert.rowcount
            print(f"{self.target_db}/{self.table}批量插入了{batchInsert.rowcount}条数据")
        except sqlite3.IntegrityError as reason:
            print(f"{self.target_db}/{self.table}批量插入数据重复，错误信息为{reason}")

        current.close()
        db.commit()
        db.close()
        return batch_count

    def fetch_date(self, sql="") -> list:
        db = sqlite3.connect(self.target_db)
        db.row_factory = Web_date_operate.dict_factory
        current = db.cursor()
        # print("数据库开启")
        all_data = []

        sql = f'SELECT * FROM "{self.table}"' + sql
        # print(sql)

        try:
            current.execute(sql)
            all_data = current.fetchall()
            # print(f"{self.target_db}/{self.table}记录{len(all_data)}条数据")
            # for item in all_data:
            #     print(item)
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}查询错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return all_data


def info_loop():
    while True:
        times = input_date.web_date()
        time.sleep(times)


if __name__ == '__main__':
    info_loop()
