import random
import time
from datetime import datetime
from multiprocessing.dummy import Process
from queue import Queue

import winsound
from pynput import keyboard, mouse

from cs_master.settings import WINDOW_SIZE
import mss
import mss.tools

shot_size = (640, 640)
save_path = "D:\DELL\Documents\ComputerVision\cs_master\data\images\\"
left, top = (WINDOW_SIZE[0] - shot_size[0]) // 2, (WINDOW_SIZE[1] - shot_size[1]) // 2
monitor = {"top": top, "left": left, "width": shot_size[0], "height": shot_size[1]}


def on_click(x, y, button, pressed):
    if pressed and run:
        # queue.put(mss.mss().grab(monitor))
        print('shot')


def on_key_press(key):
    global run
    try:
        if key.char == 'm':
            if run:
                winsound.Beep(400, 600)
            else:
                winsound.Beep(800, 600)
            run = not run
            print(run)
        if key.char == 'e':
            if run:
                queue.put(mss.mss().grab(monitor))
                print('shot')
    except AttributeError:
        pass

# def grab(queue: Queue) -> None:
#     monitor = {"top": top, "left": left, "width": shot_size[0], "height": shot_size[1]}
#
#     # with mss.mss() as sct:
#     #     for _ in range(100):
#     #         queue.put(sct.grab(monitor))
#     # for _ in range(100):
#     #     s1 = mss.mss().grab(rect)
#     #     s2 = pyautogui.screenshot()
#     #     queue.put(s2)
#
#     # Tell the other worker to stop
#     queue.put(None)

def save(queue: Queue) -> None:
    to_png = mss.tools.to_png

    while "there are screenshots":
        img = queue.get()
        if img is None:
            break
        timestamp = time.time()
        current_time = datetime.fromtimestamp(timestamp)
        formatted_time = current_time.strftime("%Y-%m-%d-%H-%M-%S-%f")
        name = str(formatted_time) + ".png"
        output = save_path + name
        to_png(img.rgb, img.size, output=output)
        print('saved')
        # img.save(output.format(number))


# python train.py --img 640 --data yolov5-fps-master/data.yaml --weights yolov5-fps-master/yolov5n.pt --epoch 300 --batch-size 16
if __name__ == "__main__":
    print('start')
    run = False
    keyboard.Listener(on_press=on_key_press).start()
    mouse.Listener(on_click=on_click).start()
    # The screenshots queue
    queue: Queue = Queue()
    # 2 processes: one for grabing and one for saving PNG files
    # Process(target=grab, args=(queue,)).start()
    Process(target=save, args=(queue,)).start()
