import re

import requests  # 导入模块
from lxml import etree
from fake_useragent import UserAgent


# 简单的反爬，设置一个请求头来伪装成浏览器
def request_header():
    headers = {
        # 'User-Agent': UserAgent().random #常见浏览器的请求头伪装（如：火狐,谷歌）
        'User-Agent': UserAgent().Chrome  # 谷歌浏览器
    }
    return headers


'''
创建两个列表用来存放代理ip
'''
all_ip_list = []  # 用于存放从网站上抓取到的ip
usable_ip_list = []  # 用于存放通过检测ip后是否可以使用


# 发送请求，获得响应
def send_request():
    # 爬取7页，可自行修改
    # for i in range(1, 8):
    #     print(f'正在抓取第{i}页……')
    #     response = requests.get(url=f'http://www.ip3366.net/free/?stype=2&page={i}', headers=request_header())
    #     text = response.text.encode('ISO-8859-1')
    #     # print(text.decode('gbk'))
    #     # 使用xpath解析，提取出数据ip，端口
    #     html = etree.HTML(text)
    #     tr_list = html.xpath('/html/body/div[2]/div/div[2]/table/tbody/tr')
    #     for td in tr_list:
    #         ip_ = td.xpath('./td[1]/text()')[0]  # ip
    #         port_ = td.xpath('./td[2]/text()')[0]  # 端口
    #         proxy = ip_ + ':' + port_  # 115.218.5.5:9000
    #         all_ip_list.append(proxy)
    #         test_ip(proxy)  # 开始检测获取到的ip是否可以使用
    #
    # print('抓取完成！')
    # print(f'抓取到的ip个数为：{len(all_ip_list)}')
    # print(f'可以使用的ip个数为：{len(usable_ip_list)}')


    while len(usable_ip_list) < 10:
        response = requests.get(url=f'http://www.66ip.cn/mo.php?sxb=&tqsl=200&port=&export=&ktip=&sxa=&submit=&textarea=', headers=request_header())
        # response = requests.get(url=f'http://www.66ip.cn/nmtq.php?getnum=&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=2&api=66ip', headers=request_header())
        text = response.text.encode('ISO-8859-1')
        # response = requests.get(url=f'http://api.89ip.cn/tqdl.html?api=1&num=100&port=&address=&isp=',
        #                         headers=request_header())
        # text = response.text.encode('UTF-8')
        # print(text.decode('gbk'))
        # 使用xpath解析，提取出数据ip，端口
        html = etree.HTML(text)
        tr_list = html.xpath(f'normalize-space(/html/body)')
        patten = re.compile(r'((\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5]):(6[0-5]{2}[0-3][0-5]|[1-5]\d{4}|[1-9]\d{1,3}|[0-9]))')
        tr_list = patten.findall(tr_list)
        # print(tr_list)
        for proxy in tr_list:
            all_ip_list.append(proxy[0])
            test_ip(proxy[0])  # 开始检测获取到的ip是否可以使用

        print('抓取完成！')
        print(f'抓取到的ip个数为：{len(all_ip_list)}')
        print(f'可以使用的ip个数为：{len(usable_ip_list)}')

    print('可用ip为：\n', usable_ip_list)

    return usable_ip_list


# 检测ip是否可以使用
def test_ip(proxy):
    # 构建代理ip
    proxies = {
        "http": "http://" + proxy,
        "https": "http://" + proxy,
        # "http": proxy,
        # "https": proxy,
    }
    try:
        # response = requests.get(url='https://web.chelaile.net.cn/', headers=request_header(), proxies=proxies,
        #                         timeout=1)  # 设置timeout，使响应等待1s
        response = requests.get(url='https://www.amap.com/', headers=request_header(), proxies=proxies,
                                timeout=1)  # 设置timeout，使响应等待1s
        response.close()
        if response.status_code == 200:
            usable_ip_list.append(proxy)
            print(proxy, '\033[31m可用\033[0m')
        else:
            print(proxy, '不可用')
    except:
        print(proxy, '请求异常')


if __name__ == '__main__':
    send_request()
