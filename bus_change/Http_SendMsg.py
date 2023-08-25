import requests


class http:
    def __init__(self, end_str, msg, QQ=None, Group=None):
        self.end_str = end_str
        self.Group = Group
        self.QQ = QQ
        self.msg = msg

    def http_get(self):
        host = ['localhost', '192.168.1.215']
        data = {
            'group_id': self.Group,
            'user_id': self.QQ,
            'message': self.msg
        }
        for each in host:
            try:
                url = f"http://{each}:15202{self.end_str}"
                response = requests.get(url=url, params=data)
            except:
                continue
                # return 'QQ未登录'
            if response == 404:
                return 'API不存在，请核实终结点！'
            else:
                return response.text
        return 'QQ Bot未启动！'

