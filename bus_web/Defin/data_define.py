class parameter:
    od_timestamp_interval = 15  # OperateData_Operate中History车辆记录消除间隔
    lq_get_num = 5     # request threading 每次运行提取线路数量
    lq_thread_num = 5   # request threading 并发数


class Gps_data:  # 定义数据基本信息

    def __init__(self, line_name, direction, gps_id, timestamp):
        self.line_name = line_name  # 线路名称
        self.direction = direction  # 方向
        # self.amap_lid = amap_lid  # amamp线路id
        self.gps_id = gps_id  # 车辆id
        self.timestamp = timestamp  # 时间

    def __str__(self):
        return f"{self.line_name}，方向{self.direction}，自编{self.gps_id}，时间{self.timestamp}"


class Amap_web:     # 定义amap存储格式

    def __init__(self, line_name, direction, ent, pathin, csid):
        self.line_name = line_name  # 线路名称
        self.direction = direction  # 方向
        # get参数
        self.ent = ent
        self.pathin = pathin
        self.csid = csid

    def __str__(self):
        return f"{self.line_name}，方向{self.direction},{self.ent}/{self.pathin}/{self.csid}"


class Sqlite_data:  # 定义sqlite传入格式

    def __init__(self, date, target="BusIdData.db"):
        self.target_db = target     # 目标数据库
        self.date_list = date       # 数据文件

    def __str__(self):
        return f"目标数据库{self.target_db}，数据文件{self.date_list}"