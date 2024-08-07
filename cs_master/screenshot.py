import time
# import dxcam
# import cs_master.dxshot as dxshot
import mss
import numpy as np
from cs_master.settings import region, monitor

# camera = dxshot.create(0, 0, region=region)
M = mss.mss()


# def take_frame():
#     frame = camera.grab()
#     return frame


def take_frame():
    png = M.grab(monitor)
    frame = np.array(png)[:, :, :3]
    return frame


# def take_png():
#     png = M.grab(monitor)
#     return png

if __name__ == '__main__':
    # camera = dxshot.create(0, 0, region=region)
    # # time.sleep(5)
    # camera.grab()
    # print('grab')
    # # time.sleep(10)
    # print('1')
    import dxshot

    while True:
        try:
            # 尝试执行截屏操作
            screenshot = dxshot.create(0, 0, region=region).grab()
            # 在这里处理截屏结果
            # ...
            print(screenshot)
            time.sleep(1)
            # 如果成功执行截屏操作，则跳出循环
        except Exception as e:
            print("截屏操作出现错误:", str(e))
            # 在这里重新加载库模块

            # 重新导入dxshot模块
            import importlib

            importlib.reload(dxshot)
