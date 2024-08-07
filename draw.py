import ctypes
import math
import random

# 导入所需的Windows GDI函数声明
gdi32 = ctypes.WinDLL('gdi32')
# 获取屏幕设备上下文
hdc = ctypes.windll.user32.GetDC(None)
# 设置绘图颜色
color = 0xFF0000  # 红色
while True:
    # 设置文本颜色和字体
    color = 0x000000  # 黑色
    gdi32.SetTextColor(hdc, color)
    gdi32.SetBkMode(hdc, 1)  # 设置背景模式为透明

    # 设置字体
    font = gdi32.CreateFontW(20, 0, 0, 0, 700, 0, 0, 0, 0, 0, 0, 0, 0, 'Arial')
    gdi32.SelectObject(hdc, font)

    # 绘制文本
    x = 100
    y = 100
    text = "Hello, World!"
    gdi32.TextOutW(hdc, x, y, text, -1)

    x = 400
    y = 300
    radius = 10
    gdi32.SetROP2(hdc, 0x0002)  # 设置绘图模式为R2_COPYPEN
    gdi32.SetDCBrushColor(hdc, color)
    gdi32.Ellipse(hdc, x - radius, y - radius, x + radius, y + radius)

    # 设置画笔颜色
    penColor = 0x000000  # 黑色
    gdi32.SetDCPenColor(hdc, penColor)

    # 设置抗锯齿模式
    gdi32.SetROP2(hdc, 0x0008)  # R2_XORPEN

    radius = 50+random.random()*10
    centerX = 100
    centerY = 100

    for angle in range(0, 360):
        x = int(centerX + radius * math.cos(math.pi * angle / 180))
        y = int(centerY + radius * math.sin(math.pi * angle / 180))
        gdi32.SetPixel(hdc, x, y, penColor)

# 释放设备上下文
ctypes.windll.user32.ReleaseDC(None, hdc)
