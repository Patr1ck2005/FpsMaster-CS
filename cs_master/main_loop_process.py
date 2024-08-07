import multiprocessing
from multiprocessing.managers import BaseManager

import numpy as np
# import viztracer
import winsound
from time import time, perf_counter, sleep
from cs_master.detector import Detector
from cs_master.assistant import Assistant
from cs_master.controller import BaseController
import threading
# import cs_master.dxshot as dxshot
import mss
from cs_master.settings import region, monitor
from cs_master.mouse_simulator import MouseSimulator


lock = threading.Lock()


class AssistLoop:
    def __init__(self, prediction_array, detector_obj, gui):
        self.mouse_v = [0.1, 0.1]
        self.assist_min_interval = 1 / 240
        self.sim_frequency = 1000
        # self.prediction_array = multiprocessing.Array('d', [10000, 10000, 0, 0, time()])
        self.prediction_array = prediction_array
        self.assistant = Assistant()
        self.detector = detector_obj
        self.mouse_simulator = MouseSimulator(self.sim_frequency)
        self.base_controller = BaseController(self.assistant, self.detector, gui)
        # self.assist_thread = threading.Thread(target=self.assist_loop, args=())
        self.assist_thread = self.assist_loop
        self.mouse_simulator_thread = threading.Thread(target=self.mouse_sim_loop, args=())
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.assist_step = 0
        # self.camera = None
        # self.mss =
        self.run = False

    def assist_loop(self):
        winsound.Beep(800, 500)
        print('-----ASSIST THREAD START-----'.center(100))
        while self.run:
            if self.pause_event.is_set():
                self.pause_event.wait()
            # assist step
            assist_start_time = perf_counter()
            self.assistant.get_info(self.i0000_to_none(list(self.prediction_array)))
            # self.mouse_v = self.assistant.take_action()
            self.assistant.take_action()
            t = perf_counter()
            # print(perf_counter()-t)
            assist_end_time = perf_counter()
            # test: assist step is very fast
            self.assist_step += 1
            if (elapsed_time := assist_end_time - assist_start_time) < self.assist_min_interval:
                sleep(self.assist_min_interval - elapsed_time)
            else:
                print(f'warning: assist step-{self.assist_step} is {elapsed_time}'.center(100, '#'))
        print('-----ASSIST THREAD OVER-----'.center(100))

    def mouse_sim_loop(self):
        # tracer = viztracer.VizTracer()
        # tracer.start()
        while self.run:
            sim_start_time = perf_counter()
            self.mouse_simulator.receive_mouse_v(self.mouse_v)
            self.mouse_simulator.send_input()
            sim_end_time = perf_counter()
            if (elapsed_time := sim_end_time - sim_start_time) < 1 / self.sim_frequency:
                sleep(1 / self.sim_frequency - elapsed_time)
            else:
                # tracer.stop()
                # tracer.save("result.json")
                # tracer.clear()
                print(f'warning: mouse step is {elapsed_time}'.center(100, '#'))

    def start(self):
        self.run = True
        self.base_controller.start_listener()
        # self.assist_thread.start()
        self.mouse_simulator_thread.start()
        # self.assist_thread()

    def pause(self):
        self.pause_event.clear()
        self.base_controller.end_listener()
        print('-----PAUSE-----'.center(100))

    def unpause(self):
        self.pause_event.set()
        self.base_controller.start_listener()
        print('-----UNPAUSE-----'.center(100))

    def end(self):
        self.run = False
        self.base_controller.end_listener()
        self.assist_thread.join()
        self.mouse_simulator_thread.join()

    # def take_frame(self):
    #     if self.camera is None:
    #         self.camera = dxshot.create(0, 0, region=region)
    #     frame = self.camera.grab()
    #     while frame is None:
    #         frame = self.camera.grab()
    #     return frame

    @staticmethod
    def i0000_to_none(array):
        for i, n in enumerate(array):
            if n == 10000:
                array[i] = None
            else:
                pass
        return tuple(array)


class DetectLoop:
    def __init__(self, prediction_array):
        self.prediction_array = prediction_array
        manager = BaseManager()
        # 一定要在start前注册，不然就注册无效
        manager.register('Detector', Detector)  # 第一个参数为类型id，通常和第二个参数传入的类的类名相同，直观并且便于阅读
        manager.start()
        self.detector = manager.Detector()
        # self.detector = Detector()
        self.detect_count = 0
        self.detect_process = multiprocessing.Process(target=self.detect_loop, args=())
        # self.detect_process = self.detect_loop
        # self.prediction_array = [10000, 10000, 0, 0, time()]
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
        print('-----DETECT PROCESS START-----'.center(100))
        with mss.mss() as sct:
            while self.run:
                # self.pause_event.wait()
                # detect step
                # detect_start_time = perf_counter()
                t_shot = time()
                # self.detector.get_assist_info(self.assistant.target_r_pos, self.assistant.mouse_rebuild,
                #                               self.assistant.pred_rebuild_pixel_pos)

                # screenshot = self.take_frame()
                screenshot = self.take_frame(sct)

                t_detect = time()
                pred = self.detector.detect(screenshot)
                pred = [item.cpu().detach().numpy() for item in pred]
                self.detector.find_target(pred)
                target_pos, target_size = self.detector.get_target_pos_size()
                array = self.none_to_10000([*target_pos, *target_size, t_shot])
                self.prediction_array[0] = array[0]
                self.prediction_array[1] = array[1]
                self.prediction_array[2] = array[2]
                self.prediction_array[3] = array[3]
                self.prediction_array[4] = array[4]
                self.detect_count += 1
                # test: no message delay time
                t2 = time()
                if t2 - t_detect > 1 / 30:
                    print(f"detect {1 / (t2 - t_detect)}fps".center(100, '#'))
                if self.detect_count % 240 == 1:
                    t_start = perf_counter()
                elif self.detect_count % 240 == 0:
                    t_end = perf_counter()
                    t_loop = (t_end - t_start)
                    print(f"MAIN LOOP {round(240 / t_loop, 1)} FPS".center(100))
        print('-----DETECT THREAD OVER-----'.center(100))

    def start_process(self):
        self.run = True
        self.detect_process.start()

    def end(self):
        self.run = False

    @time_limit(1 / 60)
    def take_frame(self, sct):
        png = sct.grab(monitor)
        frame = np.array(png)[:, :, [2, 1, 0]]
        return frame

    @staticmethod
    def none_to_10000(lst):
        for i, n in enumerate(lst):
            if n is None:
                lst[i] = 10000
            else:
                pass
        return lst


class MainLoop:
    def __init__(self, gui=None):
        self.prediction_array = multiprocessing.RawArray('d', [10000, 10000, 0, 0, time()])
        self.detect_loop = DetectLoop(self.prediction_array)
        # self.assist_process = multiprocessing.Process(target=AssistLoop(self.prediction_array, self.detect_loop.detector, gui).start)
        self.assist_process = AssistLoop(self.prediction_array, self.detect_loop.detector, gui)

    def start(self):
        self.detect_loop.start_process()
        self.assist_process.start()


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
    # def mainloop(gui=None):
    #     prediction_array = multiprocessing.RawArray('d', [10000, 10000, 0, 0, time()])
    #     # prediction_array = [10000, 10000, 0, 0, time()]
    #     detect_loop = DetectLoop(prediction_array)
    #     # assist_process = multiprocessing.Process(target=AssistLoop(prediction_array, detect_loop.detector, gui).start)
    #     assist_process = AssistLoop(prediction_array, detect_loop.detector, gui)
    #     detect_loop.start_process()
    #     assist_process.start()
    #
    # mainloop()

    # time.sleep(3)
    # main.pause()
    # time.sleep(3)
    # main.unpause()
