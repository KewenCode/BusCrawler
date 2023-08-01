import json

from bus_web.Defin.sqlite_define import IDSupport_operate


class Support_Operate:

    def __init__(self, data: list = None):
        self.data = data

    def data_update(self):
        up_collect = []
        insert_collect = []
        for each in self.data:
            """
            each["ID"]: ID
            each["Line"]: 线路
            each["Day"]: 时间
            each["Type"]: 1 support 2 night
            """
            # try:
            support_result = IDSupport_operate(each["ID"]).retrieve("ID")
            print("+++")
            print("查询信息如下：")
            print(support_result)
            print("+++")

            if len(support_result) == 0:
                json_support = [each["ID"],
                                json.dumps([each["Line"]]),
                                json.dumps({
                                    each["Line"]: [each["Day"]]
                                }),
                                each["Type"]]
                insert_collect.append(json_support)
            else:
                # 默认匹配第一条数据
                line = support_result[0]
                line_json = json.loads(line['Line'])
                try:
                    line_json.index(each["Line"])
                    his_json = json.loads(line['Time'])
                    if each["Day"] not in his_json[each["Line"]]:
                        his_json[each["Line"]].append(each["Day"])
                        line['Time'] = json.dumps(his_json)
                except (IndexError, ValueError):
                    # 列表添加
                    line_json.append(each["Line"])
                    # 时间表添加
                    his_json = json.loads(line['Time'])
                    his_json[each["Line"]] = [each["Day"]]
                    line['Line'] = json.dumps(line_json)
                    line['Time'] = json.dumps(his_json)

                up_collect.append([line['Line'], line['Time'], line['Type'], line['ID']])
        if len(insert_collect) > 0:
            IDSupport_operate(insert_collect).batch_insert()
        if len(up_collect) > 0:
            IDSupport_operate(up_collect).update('ID', 'line', 'Time', 'Type')

    def data_fresh(self):
        """
        support数据再整合，默认不传参全域刷新，传入列表参指定刷新
        :return:
        """
        if self.data is not None:
            # 指定ID刷新
            for each in self.data:
                print(each)
        else:
            # 全域刷新
            print(f"1")

