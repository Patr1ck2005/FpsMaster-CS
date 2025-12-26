import ctypes
import time

# 定义一些常量
KEYEVENTF_KEYUP = 0x0002
VK_A = 0x41  # Virtual key code for 'A'
VK_D = 0x44  # Virtual key code for 'D'

# 模拟按下键
def key_down(vk):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)

# 模拟松开键
def key_up(vk):
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

time.sleep(5)
# 按下a键
print("Pressing 'a'")
# key_down(VK_A)
time.sleep(1)

# 强制松开a键
print("Releasing 'a'")
key_up(VK_A)

# 按下d键
time.sleep(1)
print("Pressing 'd'")
# key_down(VK_D)
time.sleep(1)

# 强制松开d键
print("Releasing 'd'")
key_up(VK_D)
