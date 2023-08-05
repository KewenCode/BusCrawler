import calendar
import os
import sqlite3
from datetime import datetime

cur_path = os.path.abspath(os.path.dirname(__file__))   # 获取当前文件的目录
proj_path = cur_path[:cur_path.find('bus_web')]

def dict_factory(cursor, row):
    # 将游标获取的数据处理成字典返回
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Sqlite_operate:
    def batch_insert(self) -> int:
        """写入数据"""
        pass

    def fetchall(self) -> list:
        """所有数据"""
        pass

    def retrieve(self, target_row) -> list:
        """精准数据"""
        pass

    # def update(self, query_row, target_row1, target_row2, target_row3, target_row4, target_row5):
    #     """替换数据"""
    #     pass


class WebDate_operate(Sqlite_operate):

    def __init__(self, table, data=None):
        """
        WebDate数据文件读取使用
        :param table:目标表单名称
        :param data:使用数据
        """
        if data is None:
            data = []
        self.table = table  # 目标表单
        self.target_db = proj_path + "bus_web/DateFile/Database/WebDate.db"  # 目标数据库，默认为WebDate.db
        self.date_list = data  # 数据文件

    def fetchall(self, sql="") -> list:
        db = sqlite3.connect(self.target_db)
        db.row_factory = dict_factory
        current = db.cursor()
        # print("数据库开启")
        all_data = []

        sql = f"SELECT * FROM {self.table}" + sql
        # print(sql)

        try:
            current.execute(sql)
            all_data = current.fetchall()
            print(f"{self.target_db}/{self.table}记录{len(all_data)}条数据")
            # for item in all_data:
            #     print(item)
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}查询错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return all_data

    def update(self, target_row1, query_row, target_row2):
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print("数据库开启")
        data = []
        try:
            sql = f"UPDATE {self.table} SET {target_row1} = ? , {target_row2} = ? WHERE {query_row} = ?"
            # print(sql, self.date_list)
            batchUpdate = current.executemany(sql, self.date_list)
            print(f"{self.target_db}/{self.table}批量更新{batchUpdate.rowcount}条数据")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}批量更新错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data


class IDInfo_operate(Sqlite_operate):

    def __init__(self, data=None):
        """
        IDInfo数据表单使用
        :param data: 数据文件
        """
        if data is None:
            data = []
        self.table = "IDInfo"  # 目标表单
        self.target_db = proj_path + "bus_web/DateFile/Database/BusIdData.db"  # 目标数据库，默认为BusIdData.db
        self.date_list = data  # 数据文件

    def batch_insert(self) -> int:
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print(f"{self.target_db}开启，模式：批量插入")
        batch_count = 0
        # print(f"待批量插入{len(self.date_list)}条数据")
        try:
            current.execute(f'CREATE TABLE IF NOT EXISTS {self.table} ( '
                            f'"ID" INTEGER NOT NULL,'
                            f' "State" INTEGER,'
                            f' "BLine" TEXT,'
                            f' "Line" TEXT,'
                            f' "Card" TEXT,'
                            f' "LRTime" INTEGER,'
                            f' PRIMARY KEY("ID"))')
            sql = f"insert into {self.table} values (?,?,?,?,?,?)"  # 其中问号为占位符
            batchInsert = current.executemany(sql, self.date_list)
            batch_count = batchInsert.rowcount
            print(f"{self.target_db}/{self.table}批量插入了{batchInsert.rowcount}条数据")
        except sqlite3.IntegrityError as reason:
            print(f"{self.target_db}/{self.table}批量插入数据重复，错误信息为{reason}")

        current.close()
        db.commit()
        db.close()
        # print(f"{self.target_db}关闭")
        return batch_count

    def fetchall(self) -> list:
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print("数据库开启")
        all_data = []
        try:
            current.execute(f"SELECT * FROM {self.table}")
            all_data = current.fetchall()
            print(f"{self.target_db}/{self.table}记录{len(all_data)}条数据")
            # for item in all_data:
            #     print(item)
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}查询错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return all_data

    def retrieve(self, target_row) -> list:
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print("数据库开启")
        data = []
        try:
            current.execute(f"select *  from {self.table} where {target_row} like '%{self.date_list}'")
            data = current.fetchall()
            # print(f"{self.target_db}/{self.table} {self.date_list}查询结果{len(data)}个")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}取回错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data

    def update(self, target_row1, query_row, target_row2):
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print("数据库开启")
        data = []
        try:
            sql = f"UPDATE {self.table} SET {target_row1} = ? , {target_row2} = ? WHERE {query_row} = ?"
            # print(sql, self.date_list)
            batchUpdate = current.executemany(sql, self.date_list)
            print(f"{self.target_db}/{self.table}批量更新{batchUpdate.rowcount}条数据")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}批量更新错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data


class IDHistory_operate(Sqlite_operate):

    def __init__(self, data=None):
        """
        IDInfo数据表单使用
        :param data: 数据文件
        """
        if data is None:
            data = []
        self.table = "IDHistory"  # 目标表单
        self.target_db = proj_path + "bus_web/DateFile/Database/BusIdData.db"  # 目标数据库，默认为BusIdData.db
        self.date = data  # 数据文件

    def batch_insert(self) -> int:
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print(f"{self.target_db}开启，模式：批量插入")
        batch_count = 0
        # print(f"待批量插入{len(self.date_list)}条数据")
        try:
            current.execute(f'CREATE TABLE  IF NOT EXISTS "IDHistory" ('
                            f'"ID"	INTEGER NOT NULL,'
                            f'"UpTime"	INTEGER NOT NULL,'
                            f'"StateHis"	TEXT,'
                            f'"LineHis_S"	TEXT,'
                            f'"LineHis"	TEXT,'
                            f'"BelongHis_S"	TEXT,'
                            f'"BelongHis"	TEXT,'
                            f'PRIMARY KEY("ID"))')
            sql = f"insert into {self.table} values (?,?,?,?,?,?,?)"  # 其中问号为占位符
            batchInsert = current.executemany(sql, self.date)
            batch_count = batchInsert.rowcount
            print(f"{self.target_db}/{self.table}批量插入了{batchInsert.rowcount}条数据")
        except sqlite3.IntegrityError as reason:
            print(f"{self.target_db}/{self.table}批量插入数据重复，错误信息为{reason}")

        current.close()
        db.commit()
        db.close()
        # print(f"{self.target_db}关闭")
        return batch_count

    def retrieve(self, target_row) -> list:

        db = sqlite3.connect(self.target_db)
        db.row_factory = dict_factory
        current = db.cursor()
        # print("数据库开启")
        data_list = []
        try:
            current.execute(f"select *  from {self.table} where {target_row} like '%{self.date}'")
            data_list = current.fetchall()
            # print(f"{self.target_db}/{self.table} {self.date}查询结果{len(data_list)}个")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}查询错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data_list

    def update(self, query_row, target_row1, target_row2, target_row3, target_row4, target_row5):
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print("数据库开启")
        data = []
        try:
            sql = f"UPDATE {self.table} " \
                  f"SET {target_row1} = ?, {target_row2} = ?, {target_row3} = ?, {target_row4} = ?, {target_row5} = ?" \
                  f"WHERE {query_row} = ?"
            # print(sql, self.date)
            batchUpdate = current.executemany(sql, self.date)
            print(f"{self.target_db}/{self.table}批量更新{batchUpdate.rowcount}条数据")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}批量更新错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data


class IDSupport_operate(Sqlite_operate):

    def __init__(self, data=None):
        """
        IDSupport数据表单使用
        :param data: 数据文件
        """
        if data is None:
            data = []
        self.table = "IDSupport"  # 目标表单
        self.target_db = proj_path + "bus_web/DateFile/Database/BusIdData.db"  # 目标数据库，默认为BusIdData.db
        self.date = data  # 数据文件

    def batch_insert(self) -> int:
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print(f"{self.target_db}开启，模式：批量插入")
        batch_count = 0
        # print(f"待批量插入{len(self.date_list)}条数据")
        try:
            current.execute(f'CREATE TABLE IF NOT EXISTS "IDSupport" ('
                            f'"ID" INTEGER NOT NULL, '
                            f'"Line" TEXT NOT NULL, '
                            f'"Time" TEXT NOT NULL, '
                            f'"Support" INTEGER NOT NULL)')
            sql = f"insert into {self.table} values (?,?,?,?)"
            batchInsert = current.executemany(sql, self.date)
            batch_count = batchInsert.rowcount
            print(f"{self.target_db}/{self.table}批量插入了{batchInsert.rowcount}条数据")
        except sqlite3.IntegrityError as reason:
            print(f"{self.target_db}/{self.table}批量插入数据重复，错误信息为{reason}")

        current.close()
        db.commit()
        db.close()
        # print(f"{self.target_db}关闭")
        return batch_count

    def retrieve(self, target_row) -> list:

        db = sqlite3.connect(self.target_db)
        db.row_factory = dict_factory
        current = db.cursor()
        # print("数据库开启")
        data_list = []
        try:
            current.execute(f"select *  from {self.table} where {target_row} like '%{self.date}'")
            data_list = current.fetchall()
            # print(f"{self.target_db}/{self.table} {self.date}查询结果{len(data_list)}个")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}查询错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data_list

    def update(self, query_row, target_row1, target_row2, target_row3):
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print("数据库开启")
        data = []
        try:
            sql = f"UPDATE {self.table} " \
                  f"SET {target_row1} = ?, {target_row2} = ?, {target_row3} = ?" \
                  f"WHERE {query_row} = ?"
            # print(sql, self.date)
            batchUpdate = current.executemany(sql, self.date)
            print(f"{self.target_db}/{self.table}批量更新{batchUpdate.rowcount}条数据")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}批量更新错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data


class OperateDate_operate(Sqlite_operate):

    def __init__(self, data=None, line_type=1):
        """
        OperateDate数据库使用
        :param data: 数据文件
        :param line_type:  特殊线路类型
        """
        if data is None:
            data = []

        self.type = line_type   # 特殊线路专用
        month = datetime.now().month
        if self.type == 1:
            # 夜间线月初判断
            if datetime.now().day == 1:
                month = month - 1

        self.table = str(datetime.strftime(datetime.now(), "%Y-%m"))  # 目标表单
        self.target_db = proj_path + "bus_web/DateFile/Database/OperateDate.db"  # 目标数据库，默认为BusIdData.db
        self.date = data  # 数据文件

    def batch_insert(self) -> int:
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print(f"{self.target_db}开启，模式：批量插入")
        batch_count = 0
        # print(f"待批量插入{len(self.date_list)}条数据")
        try:
            current.execute(f'CREATE TABLE IF NOT EXISTS "{self.table}" ('
                            f'"Index"	TEXT NOT NULL, '
                            f'"Area"	INTEGER, '
                            f'"Line"	TEXT NOT NULL, '
                            f'"Direction"	INTEGER NOT NULL, '
                            f'"Day"	TEXT, '
                            f'"History"	TEXT, '
                            f'PRIMARY KEY("Index") )')
            sql = f'insert into "{self.table}" values (?,?,?,?,?,?)'
            batchInsert = current.executemany(sql, self.date)
            batch_count = batchInsert.rowcount
            print(f"{self.target_db}/{self.table}批量插入了{batchInsert.rowcount}条数据")
        except sqlite3.IntegrityError as reason:
            print(f"{self.target_db}/{self.table}批量插入数据重复，错误信息为{reason}")

        current.close()
        db.commit()
        db.close()
        # print(f"{self.target_db}关闭")
        return batch_count

    def retrieve(self, target_row) -> list:

        db = sqlite3.connect(self.target_db)
        db.row_factory = dict_factory
        current = db.cursor()
        # print("数据库开启")
        data_list = []
        try:
            current.execute(f'select *  from "{self.table}" where "{target_row}" like "{self.date}"')
            data_list = current.fetchall()
            # print(f"{self.target_db}/{self.table} {self.date}查询结果{len(data_list)}个")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}查询错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data_list

    def update(self, query_row, target_row1):
        db = sqlite3.connect(self.target_db)
        current = db.cursor()
        # print("数据库开启")
        data = []
        try:
            sql = f'UPDATE "{self.table}" ' \
                  f'SET "{target_row1}" = ?' \
                  f'WHERE "{query_row}" = ?'
            # print(sql, self.date)
            batchUpdate = current.executemany(sql, self.date)
            print(f"{self.target_db}/{self.table}批量更新{batchUpdate.rowcount}条数据")
        except sqlite3.OperationalError as reason:
            print(f"{self.target_db}/{self.table}批量更新错误，错误原因{reason}")

        current.close()
        db.commit()
        db.close()
        # print("数据库关闭")
        return data
