import numpy as np
# import viztracer
import winsound
import importlib
from time import time, perf_counter, sleep
from cs_master.detector import Detector
from cs_master.assistant import Assistant
from cs_master.controller import BaseController
from cs_master.mouse_simulator import MouseSimulator
import threading
import dxshot
# import mss
from cs_master.settings import region, monitor

lock = threading.Lock()


class MainLoop:
    def __init__(self, gui):
        self.gui = gui
        self.assist_min_interval = 1 / 240
        self.sim_frequency = 1000
        self.prediction_array = [None, None, 0, 0, time()]
        self.assistant = Assistant()
        self.detector = Detector()
        self.mouse_simulator = MouseSimulator(self.sim_frequency)
        self.base_controller = BaseController(self.assistant, self.detector, gui)
        self.detect_count = 0
        self.detect_thread = threading.Thread(target=self.detect_loop, args=())
        self.assist_thread = threading.Thread(target=self.assist_loop, args=())
        self.mouse_simulator_thread = threading.Thread(target=self.mouse_sim_loop, args=())
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.camera = None
        # self.mss =

        self.run = False

    # decorator
    def time_limit(time_limit):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time()
                result = func(*args, **kwargs)
                elapsed_time = time() - start_time
                if elapsed_time > time_limit:
                    print(f"Function '{func.__name__}' cost {elapsed_time} seconds")
                return result
            return wrapper
        return decorator

    def detect_loop(self):
        print('-----DETECT THREAD START-----'.center(100))
        self.gui.add_line_in_console('-----DETECT THREAD START-----', '')
        # with mss.mss() as sct:
        while self.run:
            self.pause_event.wait()
            # detect step
            # detect_start_time = perf_counter()
            t_shot = time()
            self.detector.get_assist_info(self.assistant.target_r_pos, self.assistant.mouse_rebuild,
                                          self.assistant.pred_rebuild_pixel_pos)

            screenshot = self.take_frame()
            # screenshot = self.take_frame(sct)

            t_detect = time()
            pred = self.detector.detect(screenshot)
            pred = [item.cpu().detach().numpy() for item in pred]
            self.detector.find_target(pred)
            target_pos, target_size = self.detector.get_target_pos_size()
            self.prediction_array[0] = target_pos[0]
            self.prediction_array[1] = target_pos[1]
            self.prediction_array[2] = target_size[0]
            self.prediction_array[3] = target_size[1]
            self.prediction_array[4] = t_shot
            self.detect_count += 1
            # test: no message delay time
            t2 = time()
            if t2 - t_detect > 1 / 24 and self.detect_count > 10:
                self.prediction_array = [None, None, 0, 0, time()]
                text = f'-----DETECT THREAD CODING DOWN ({round(1 / (t2 - t_detect))}fps)-----'
                print()
                print(text.center(100, '#'))
                self.gui.add_line_in_console(text, '')
                print()
                winsound.Beep(600, 600)
                # sleep(5)
                # winsound.PlaySound("SystemDefault", winsound.SND_ASYNC)
            if self.detect_count % 240 == 1:
                t_start = perf_counter()
            elif self.detect_count % 240 == 0:
                t_end = perf_counter()
                t_loop = (t_end - t_start)
                text = f"MAIN LOOP {round(240 / t_loop, 1)} FPS"
                print(text.center(100))
                self.gui.add_line_in_console(text, '')
        print('-----DETECT THREAD OVER-----'.center(100))

    def assist_loop(self):
        print('-----ASSIST THREAD START-----'.center(100))
        self.gui.add_line_in_console('-----ASSIST THREAD START-----', '')
        while self.run:
            if self.pause_event.is_set():
                self.pause_event.wait()
            # assist step
            assist_start_time = perf_counter()
            self.assistant.get_info(tuple(self.prediction_array))
            t = perf_counter()
            self.mouse_simulator.receive_mouse_v(self.assistant.take_action())
            # print(perf_counter()-t)
            assist_end_time = perf_counter()
            # test: assist step is very fast
            if (elapsed_time := assist_end_time - assist_start_time) < self.assist_min_interval:
                sleep(self.assist_min_interval - elapsed_time)
            else:
                print(f'WARNING: assist step is {elapsed_time}'.center(100, '#'))
        print('-----ASSIST THREAD OVER-----'.center(100))

    def mouse_sim_loop(self):
        # tracer = viztracer.VizTracer()
        # tracer.start()
        while self.run:
            lock.acquire()
            try:
                sim_start_time = perf_counter()
                self.mouse_simulator.send_input()
                sim_end_time = perf_counter()
                if (elapsed_time := sim_end_time - sim_start_time) < 1 / self.sim_frequency:
                    sleep(1 / self.sim_frequency - elapsed_time)
                else:
                    # tracer.stop()
                    # tracer.save("result.json")
                    # tracer.clear()
                    # print(f'warning: mouse step is {elapsed_time}'.center(100, '#'))
                    pass
            finally:
                lock.release()

    def start(self):
        self.run = True
        self.base_controller.start_listener()
        self.assist_thread.start()
        self.detect_thread.start()
        self.mouse_simulator_thread.start()

    def pause(self):
        self.pause_event.clear()
        self.base_controller.end_listener()
        print('-----PAUSE-----'.center(100))
        self.gui.add_line_in_console('PAUSE', '')

    def unpause(self):
        self.pause_event.set()
        self.base_controller.start_listener()
        print('-----UNPAUSE-----'.center(100))
        self.gui.add_line_in_console('UNPAUSE', '')

    def end(self):
        self.run = False
        self.base_controller.end_listener()
        self.assist_thread.join()
        self.detect_thread.join()
        self.mouse_simulator_thread.join()

    def reset_model(self, path):
        self.pause()
        self.detector.reset_model(path)
        print('-----RESET MODEL-----'.center(100))
        self.gui.add_line_in_console('RESET MODEL', '')
        self.unpause()

    # @time_limit(1 / 120)
    def take_frame(self):
        if self.camera is None:
            self.camera = dxshot.create(0, 0, region=region)
        try:
            frame = self.camera.grab()
            # print(frame)
            while frame is None:
                frame = self.camera.grab()
                # print(frame)
        except:
            print('Screen Capture Error'.center(100, '*'))
            importlib.reload(dxshot)
            sleep(3)
            self.camera = dxshot.create(0, 0, region=region)
            frame = self.camera.grab()
            # print(frame)
            while frame is None:
                frame = self.camera.grab()
        return frame

    # @time_limit(1 / 60)
    # @staticmethod
    # def take_frame(sct):
    #     png = sct.grab(monitor)
    #     frame = np.array(png)[:, :, [2, 1, 0]]
    #     return frame


if __name__ == '__main__':
    # assistant = Assistant()
    # controller = BaseController(assistant)
    # controller.start_listener()
    # print('INITIALISING'.center(100, '#'))
    # detector = Detector()
    # assistant = Assistant()
    # controller = BaseController()
    # print('INITIALISED'.center(100, '#'))
    # min_interval = 1 / 240
    #
    # window_title = "Counter-Strike 2"
    #
    # shared_pred_array = [None, None, 0, 0, time()]
    #
    # threading.Thread(target=assist_loop, args=(shared_pred_array,)).start()
    # detect_loop(shared_pred_array)

    main = MainLoop()
    main.start()

    # time.sleep(3)
    # main.pause()
    # time.sleep(3)
    # main.unpause()
