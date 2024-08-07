# import win32api
# import win32con
import interception
from numpy.random import randn


class KeyboardMouseClass:
    @staticmethod
    def mouse_click():
        interception.left_click(interval=0.05+0.01*randn())
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        # Logitech.mouse.click(1)

    @staticmethod
    def mouse_press():
        interception.mouse_down('left')
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        # Logitech.mouse.press(1)

    @staticmethod
    def mouse_release():
        interception.mouse_up('left')
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        # Logitech.mouse.release(1)

    @staticmethod
    def mouse_move(dx, dy):
        interception.move_relative(int(dx), int(dy))
        # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(dy))
        # Logitech.mouse.move(int(dx), int(dy))

    @staticmethod
    def press_key(key):
        dic = {
            'w': 87,
            'a': 65,
            's': 83,
            'd': 68
        }
        # win32api.keybd_event(dic[key], 0, 0, 0)
        # interception.press(key)
        pass

    @staticmethod
    def release_key(key):
        dic = {
            'w': 87,
            'a': 65,
            's': 83,
            'd': 68,
        }
        pass
        # win32api.keybd_event(dic[key], 0, win32con.KEYEVENTF_KEYUP, 0)

    @staticmethod
    def release():
        pass


if __name__ == '__main__':
    import time
    km = KeyboardMouseClass()
    i = 0
    t = time.time()
    while i<10:
        t1 = time.time()
        km.mouse_move(10,3)
        print(time.time()-t1)
        i+=1
    print(time.time()-t)