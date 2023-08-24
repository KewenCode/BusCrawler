"""
和网络数据获取相关的类定义
"""
import json
import random
import re
import string
import time

import requests
from fake_useragent import UserAgent

from bus_web.Defin.data_define import Gps_data


class WebData:  # 数据抽象类
    def data_receive(self, Proxies=None) -> (list[Gps_data], int):
        """网络数据接收"""
        pass

    def data_form(self):
        """数据处理"""
        pass

    def date_dic(self):
        """输出字典"""
        pass


class Amap_webdata(WebData):

    def __init__(self, line_name, direction, ent, pathin, csid):
        self.line_name = line_name  # 线路名称
        self.direction = direction  # 方向
        # get参数
        self.ent = ent
        self.pathin = pathin
        self.csid = csid

    # 实现抽象方法
    def data_receive(self, Proxies=None) -> (list[Gps_data], int):
        code = 200
        bus_data = []
        url = "https://m5.amap.com/ws/mapapi/realtimebus/linestation/"
        data = {
            'ent': self.ent,
            'in': self.pathin,
            'csid': self.csid
        }
        # 175.8.132.228:7890
        # *111.178.11.20:8088
        # 123.60.27.166:7890
        # 47.100.69.29:8888
        # 101.43.93.67:7890
        # ￥114.116.106.90:7890
        # *47.110.163.29:7890
        # *42.193.100.8:7890
        # 47.106.144.184:7890

        # *47.97.97.119:3128
        proxies = {
            'http': f'http://{Proxies}',
            'https': f'http://{Proxies}'
        }
        try:
            response = requests.get(url=url, params=data, timeout=5, proxies=proxies)
            if response.status_code == 200:
                json_data = json.loads(response.text)

                if json_data["result"] is False:
                    print("元数据错误")
                    code = 250
                elif not json_data["buses"][0]['trip']:
                    """ 当gps数据不存在，跳过 """
                    print("无数据")
                    code = 201
                else:
                    for contain in json_data["buses"][0]['trip']:
                        # print(contain['gps_id'])
                        temp_data = Gps_data(self.line_name,
                                             self.direction,
                                             # json_data['buses'][0]['line'],
                                             contain['gps_id'],
                                             json_data['timestamp']
                                             )
                        bus_data.append(temp_data)
                        print(temp_data)  # 信息概览输出
            else:
                code = response.status_code
        except:
            print('请求异常')
            code = 203

        return bus_data, code


class Chelaile_webdata(WebData):

    @staticmethod
    def create_string_number(n):
        """生成一串指定位数的字符+数组混合的字符串"""
        m = random.randint(1, n)
        a = "".join([str(random.randint(0, 9)) for _ in range(m)])
        b = "".join([random.choice(string.ascii_letters) for _ in range(n - m)])
        return ''.join(random.sample(list(a + b), n))

    def __init__(self, LineName, Direction, QueryID, stationId):
        self.LineName = LineName
        self.Direction = Direction
        self.QueryID = QueryID
        self.stationId = stationId

    def data_receive(self, Proxies=None) -> (list[Gps_data], int):
        code = 200
        bus_data = []
        UserId = Chelaile_webdata.create_string_number(28)
        lat = '%.14f' % random.uniform(31.9, 32.1)
        lng = '%.14f' % random.uniform(118.74, 118.82)

        headers = {
            'Host': 'web.chelaile.net.cn',
            'Connection': 'keep-alive',
            'referer': 'https://servicewechat.com/wx71d589ea01ce3321/630/page-frame.html',
            'xweb_xhr': '1',
            'User-Agent': UserAgent().random,
            'Content-Type': 'text',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh'
        }
        data = {
            's': 'h5',
            'wxs': 'wx_app',
            'sign': 1,
            'h5RealData': 1,
            'v': '3.9.187',
            'src': 'weixinapp_cx',
            'ctm_mp': 'mp_wx',
            'vc': 1,
            'cityId': '018',
            'favoriteGray': 1,
            'userId': UserId,
            'h5Id': UserId,
            'lat': lat,
            'lng': lng,
            'geo_lat': lat,
            'geo_lng': lng,
            'gpstype': 'wgs',
            'geo_type': 'wgs',
            'scene': 1001,
            # 'lineId': '0025114984337',
            # 'stationId': '025-1312',
            'lineId': self.QueryID,
            'stationId': self.stationId,
            'targetOrder': 1,
            'specialTargetOrder': 1,
            'specail': 0,
            'specialType': 'undefined',
            'cshow': 'busDetail'
        }
        # *101.43.93.67:7890
        # 183.56.253.129:8118
        # 47.100.69.29:8888
        # *75.114.77.38:8080
        # 39.98.204.54:7890
        # 47.108.239.99:7890
        # 123.249.124.39:3128
        # 47.97.97.119:3128
        proxies = {
            'http': 'http://183.56.253.129:8118',
            'https': 'http://183.56.253.129:8118'
        }

        try:
            response = requests.get('https://web.chelaile.net.cn/api/bus/line!busesDetail.action', headers=headers,
                                    timeout=10, params=data, proxies=proxies)
            if response.status_code == 200:
                timestamp = int(time.time() * 1000)
                patten = re.compile('{.*}')
                tr_list = patten.findall(response.content.decode("utf-8"))
                json_data = json.loads(tr_list[0])
                print(tr_list[0])  # 输出json

                if json_data['jsonr']["success"] is False:
                    print("元数据错误")
                    code = 250
                elif not json_data['jsonr']['data']['buses']:
                    """ 当gps数据不存在，跳过 """
                    print("无数据")
                    code = 201
                else:
                    for contain in json_data['jsonr']['data']['buses']:
                        # print(contain)
                        temp_data = Gps_data(self.LineName,
                                             self.Direction,
                                             contain['busId'],
                                             timestamp
                                             )
                        bus_data.append(temp_data)
                        print(temp_data)  # 信息概览输出
            else:
                code = response.status_code
        except:
            print('请求异常')
            code = 203

        return bus_data, code


if __name__ == '__main__':
    text = Amap_webdata("206路", "1", "2",
                        "ZRmRCRvwd8oR7TESnx5s/PMKguMS4mfZu1CSa/5AqHxwKSSKuk2E4C9f3K6B3defQxkvXklv0K0aWxt7P7S/ZKfWNjefsyw2+kcvTXQ87B/SqA9sXdcv1lqhpruL27CmRwVH6cxrCCk1PZyglc+oc+2QA4HGhqZIJSZOllC03T+jZBKJjavFZBjB1/cDyFG1ZurzDUL8WnGEi9XD+B9yGt9zUmH2DRrH/zbwHhn9bZCedjzpMALnj7cyt0AF/W/hHGbiJgFAAD8K7NqDHjRTrMCGQkwYb3/pj3U7Kwsck9RpWAruQSD3kmCVMzEVmiCfg4RiCji2vwj2MpzjgCaeBmabaoevb0Fj3RfeU6OlwruWhKiPKGvxtIG2eMUJ0akwn06bSb9hg2D7KKwHgx2Cl71nWIaV+P74LV9SgSbSshsuOpn7y6E8LnD4/RMFCbjBEIdggSA2+74ut0S0cpJueTpvsTPu4SLJ6pC0sggXxZC3Oo4WSPFOMaFFDkc++FNw+ApybWQovxp+gVoE2O+7lQJgILdp1RS2H2+eo2Ym0yMPBiWmlJJtf9BHpDI5VxcJnuynGgCXp33/monkRah9K5Luj6Op2ICsuUuUqotHbtQtncPsrWsvW9Ob7QDwnC99StJbXvIhOGakh6XS6zZbEmmZbJJpyJR3Y1u1b8ln0p/Hs/BjVNWP13f7L2uVh/8bDRcQY1n947qFwEGmKVS0VVRhVCYd6Aj6cYDRVwU59bR16mOgCgLqGBtxac4wlKBWgb7GWTZG7/l/R0w/56quP92qUtiJ7bkL0NFsZCHQt0VPLLMOJl6Sr4v7UMbvXaetzt5NPUji4bVK7ofMVGE2jsnGju2OZgmAFQwlAy4tYd9yAgLWhTJ5mKI6iOPBdBHFZv8ia13/uSsz9s/GtTbOxCJ3H2Jqa8lTkxIOQNe0mv96+eoNTa9pvswqF4jTyWdJuUZEoNJEXBTU1PPqtegZZvfdLgk27TIYpoN4eR8INhe385LsyhDvE1EsSsgeV9gwu0h8xuOHYkGJgDfx+hUb9KIdeBLjOKNoUaU3MoxRuD8D58xSXLlzyPBhpbr1pMrKpAiMAm8jsCIVWS86TrTtv7pSapSo68WXaaoq8sLOnUHABpXlNKusE7z/DG5tVz0xPONX11Kgfxlu6to5whE6MIrxLG0tTsLAE9DbXA3xFWXY7XxovBfKAx3T+27V/c50DsP8P3WZhYLljzi2783hFxZxx3fkWmPfircIVgP8xaTSk+gotxrgxFYscbiVrmaItSpN7YTQtQrzdUQ6SuHQXut7/dNLMB9nr/giUlYYrd/kSuScYFLYLdxJAshL6olTf3baXuUvRhcIIMnz5/bbTRiwka8f2YZuoNVQ9I/ZcUNkw2ufDny+gWvHa4oKU4uGkGm2YE00nTa25RTfIxAJkxxXCusp9YL1zzk+bgxqYxq5bd2TCIZvMC8Qr9ZMCDehqh4lUngW8dZFlMJmo+aeQb7asP+TDHOmB37D4bOtOouHxfkbaFP68YEWadk=",
                        "")
    # text = Amap_webdata("53路", "1", "2",
    #                     "VreVL5AjjlTXoQDjLBYd2vJEH/LkoS/AGVLH/M7YrwUgk9BtjBZwUoQ8p1Po/tq3axns5LZ96/xCq3Nyjk8iZ47/w4spnuQ/1Ts56tB5p9Toj2NwGLk4CrQTK+rLuHzIOIuCBid9Pm1bcllhvinHygyPEzGK51o0e2J3ViNjExb39H5SaWnSLI5FzKqbq266qcuF2r4v8vEC8erhBVHcgEnqazp9QDcjGgb/2ePolAPzmNYa8Oj5VVwt+rmXPAZHNe1eNvFwQ3+ao4jWvPfrzc5c5WvEPqy1LeOJ16YCc84GYwhpw4FEocDHX9B7mtkQFZgjpkM/Q+ZOL545U0sgkdHcg3wPB1AI7NHSFqFDi4D1cpicw6WUomnGl0pRAjT+cyR/UQvtVO0F6ZREDtNN70zAlhVd0tfP1WOwpTcECKFWv2mtpof6Zuz3AaeSKyyXKYVxgVL5R9R++BHPg+s86I/YU8vpnDxRmbfPFgGrPfpsHwFsARSftxiXMKE1HOBilJeoocZgYSDPfj8zklqLqqzgftSseg8G7jASgQuOoz1fwZ6tTYYtbTMgjnuiaYGlK5Dg7TXRsa4tepWPUoBYRK5m74gkQpwXGRjeu/LSjtPmybvdENjOzofMzc+u35YX2jaP0eNSUjipMRJB45Pxl5ZdevExctiw/1skscdFfw8BXLhBcK44NwXncJRoYVRydofncIM/Aw71T7R2p30iFT6s5Joe/J4HCroHiV+IqBUJLonYvaFdyjjUfk2/fTAo+8kx2CL7i7EsmRXa50jW1r3xd5ljKkrw5GsM4rl7eWidNdGVMHtTP2BQyxRn/sN1njrD0orHcl8fW160mxrdxLPMCdNpU3zTUHGXb+lBnBwR6A1w3C8Wg6faMWBZbi+0z+5OveggF3BHf9WiIYqp2jz+jTf0Iv+hn9c6pItU7bkvC0a9bOM906B/slBIJ7QZPlkmc4+XcA98R/G2Ge9OXXCDmSJfUNSX9Gezq7ULcDQhQroLpBSCQLCg7Pgxm/tQC6zS8Fr3TrZd1l4njE3cLaYUVvqVFT6DiCgckQLHqHLrhiDBbpIzOdschbwjD4IKeFlMFoOzjBQCh0o1GNmblHFNtlzqlkFc9W0vD9twcxyz01poRDLjA2o3lQs9jHkPHcfVT/WczV4MphHrnzCMopW5qFMMjzm/luy50WW7emwidaKYGvnU7uQk2y0N4RKCGnFi00D5NJUWc2E1zTDxP54P5nI8wx7PN0mxNiyB5e2ivJurtGacDi6ZVOeaf6p/wD4ARX+7+Q7uZJz1PIZ0WEq3Rc2++m0tanf5H2YMGRGO1kbnhTdJ3hkkx1nd/moMAfzNKgHeRIrX7TqqdhQSXRy1Im1FfEm2cXJcGg71ZlqtynhP/mv2Uwq5gl2WtvNeUMwQg/3mKuq+5MQjOSu43msfBWpnqaVq82T6emwm3deAXYi9DNMcDxuo8nH1NkWw4zNURQ==",
    #                     "")
    # text = Amap_webdata("Y16路", "2", "2",
    #                     "FX+tXJpMOC3fuPROvbS6AVTuTqiVPtZVANxbSFHnOChp1c/tFXjErMhEVhDdfpnQCjYnOzGKImc7TpnTKhkOoJTas455DzQFf1iIl0w+ULN41xRMad8mAoSABhJe6H1Mgxo2ybuNfcEJfsrfaVrDhb7GCVQmsNr30qXYVPHt5OkNYM4SW10ZI+apOmUKBglJ253F9vs74BGtydiWJbiEMSk4EU5BGU94dhSlxeKFCNxsyA0IPeH07LZmkUVh+ht4zgnZw8LqYXHUbDckchfQsmhJF/fJbubr+gSlnjT3+/D/lgGVB/qAkY2r/YsZOVqqBn+89WBouQwI/EUVXjLjlv+Fdqo0CIC3s750KMBUJA2GllCNsCmqtCwL6dWKHGkouVM7bsHbsdr5t1mwxg75ZJJFHCUmKCh0xt8sLiQmcKq2+hMb8dadXNqKyjEDel6VmQd+Zk0T5lyMBoPMcwYOQIKlr1nt08ixU1sllsJ0SZRddYcr6RcoKjQHWi4z2qBzf0MxpZDtyQujZUTAQgFsvvNAyLFOUG8ypO/ElqDE+SI5AFsYv2aAnMJdGBjsNE6M9j41xeieI2UKlKxPmr3NkTNIQnWppKzRsMLYqQ/4k1D2f4kO8cdzgCHxo5kXEpA2Jhmo7aJ61BstpyxcTGkwV52AT1s8RERsxfDOKdZnULI2ghv7HMK/8a8zGsT/SSsYlak5hJ/CD7wtwuw0L0kIbuDp2+zmF1HCbRs99Mkwx0fegJy3duFDrVySFSiXEXhVvd283mEwBhItGjTuEfVaNnbtTSnlkpBLpfxbLD1+Cn7gHzUA8XsPNY8YAiFkRmmm4oD1B21LHu+Z1mj0+jxOX8l7Qcxak/GCYLgn/GGMe2Dtuc6yVZDmOY8HkC/mSgjuR6RhLPtBfClqMR6FazLH5OLoRsCNhCF6F7m95o/5FSJN13vRqPnsKEMqyhOjBr9FxxlV1VvGwlFhxZUAP6e6MkwRBEeSn1RZP5cx65UC85+93biMs8hKlpqG3Lgih+dC8IRN6YtTLKEWazX7llIMK8YpyPJy22J11vqApvAMGC47v8lNIKUpz+m/q8oJsJojiadCcQht2bjvMZLKUP3OBwkM21MvODcJeC0bhowM6fc9yhMnxkiQ+IH6sCzmi261ThiQzZi5i20J4hBPj2FQup8AFGRIjNWalnUhxzOrhsCFY+FwU+jeeT9aNWcx8GhZcVrj/0xC8bZ/pPLKlOafGvL64TCwdMZWsJYlID0x8tmhPn8TtAhXEkYfGkwywQbqymJMNm/7WU+9K8YTZwTM00QE7FL1SMni6qcK0172IuIAoduQYrpMs/uukFKLG9nubP45sIr7sWN7dNWAMsDNm0bXuf/0XsnKnbn9r1j0AbNWcYxaQFDN6c5Ofmj8ea6oGfy6owG4kuS9QM6PEVec/inXDDsj+SddiN4MuwvzRAVef+loEw2VeufD+O/wxfXNg+beb9RcWL/kTSdp3XY99uQhuemlMe7o",
    #                     "4b08ba70-4f36-40cf-a935-c2a45c006854")
    text.data_receive('124.222.181.107:7890')
    # 20.44.206.138:80
    # 223.215.176.36:8089

    # 114.116.252.222:443
    # 47.97.97.119:3128
    # 5.78.72.71:10080
