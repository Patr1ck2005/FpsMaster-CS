from pynput import keyboard

# 初始化状态
a_pressed = False
d_pressed = False
program_triggered = False

# 键盘控制器
controller = keyboard.Controller()

def on_press(key):
    global a_pressed, d_pressed, program_triggered

    try:
        if key.char == 'a' and not a_pressed:
            print("手动或程序按下了 'a'")
            a_pressed = True
            if not program_triggered:
                # 程序按下 'a'
                controller.press('a')
                print("程序按下 'a'")
                program_triggered = True
            if d_pressed:
                # 程序松开 'd'
                print("程序松开 'd'")
                controller.release('d')
                d_pressed = False

        elif key.char == 'd' and not d_pressed:
            print("手动或程序按下了 'd'")
            d_pressed = True
            if not program_triggered:
                # 程序按下 'd'
                controller.press('d')
                print("程序按下 'd'")
                program_triggered = True
            if a_pressed:
                # 程序松开 'a'
                print("程序松开 'a'")
                controller.release('a')
                a_pressed = False

    except AttributeError:
        pass

def on_release(key):
    global a_pressed, d_pressed, program_triggered

    try:
        if key.char == 'a':
            print("on_release: 手动松开了 'a'")
            if program_triggered:
                controller.release('a')
            a_pressed = False
            program_triggered = False

        elif key.char == 'd':
            print("on_release: 手动松开了 'd'")
            if program_triggered:
                controller.release('d')
            d_pressed = False
            program_triggered = False

    except AttributeError:
        pass

# 监听键盘输入
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
