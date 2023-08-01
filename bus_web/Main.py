import multiprocessing

from bus_web.Message import line_message
from bus_web.Request.amap import amap_loop, amap_reset
from qq_connect import Bot_Nakurut

# line_message._init()
# amap_loop()
# amap_reset(amap_loop())

if __name__ == '__main__':

    print("multiprocessing设定")
    bot = multiprocessing.Process(target=Bot_Nakurut.Bot_run)  # 机器人
    event = multiprocessing.Event()
    amap = multiprocessing.Process(target=amap_loop, args=(event,))
    amap_stop = multiprocessing.Process(target=amap_reset, args=(event,))

    print("multiprocessing启动")
    bot.start()
    amap.start()
    amap_stop.start()