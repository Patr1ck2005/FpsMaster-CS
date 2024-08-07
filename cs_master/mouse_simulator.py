import time

from cs_master.kmclass import KeyboardMouseClass as km


# from matplotlib import pyplot as plt
# human_curve_dx = []
# human_curve_x = []
# human_curve_t = []
# count = 0
# x = 0


class MouseSimulator:
    def __init__(self, sim_frequency=1000):
        self.INPUT_FREQUENCY = 240
        self.OUTPUT_FREQUENCY = sim_frequency
        self.scale = self.OUTPUT_FREQUENCY / self.INPUT_FREQUENCY
        self.unhandled_mouse_v = [0, 0]
        self.last_unhandled_mouse_v = (0, 0)
        self.divide_mouse_v = [0, 0]
        self.mouse_int_error = [0, 0]
        self.divide_count = 0

    def receive_mouse_v(self, v):
        self.divide_count = 0
        self.last_unhandled_mouse_v = tuple(self.unhandled_mouse_v)
        self.unhandled_mouse_v = v.copy()

    def send_input(self):
        # global count, x
        # t = time.time()
        self.divide_count += 1
        self.divide_mouse_v[0] = 2*self.unhandled_mouse_v[0]/self.scale
        self.divide_mouse_v[1] = 2*self.unhandled_mouse_v[1]/self.scale
        move_error_x, self.divide_mouse_v[0] = self.custom_modf(self.divide_mouse_v[0])
        move_error_y, self.divide_mouse_v[1] = self.custom_modf(self.divide_mouse_v[1])
        self.mouse_int_error[0] += move_error_x
        self.mouse_int_error[1] += move_error_y
        if self.mouse_int_error[0] >= 1:
            self.divide_mouse_v[0] += 1
            self.mouse_int_error[0] -= 1
        elif self.mouse_int_error[0] <= -1:
            self.divide_mouse_v[0] -= 1
            self.mouse_int_error[0] += 1
        elif self.mouse_int_error[1] >= 1:
            self.divide_mouse_v[1] += 1
            self.mouse_int_error[1] -= 1
        elif self.mouse_int_error[1] <= -1:
            self.divide_mouse_v[1] -= 1
            self.mouse_int_error[1] += 1
        # if time.time()>t+0.0001:
            # print(time.time()-t)
            # print('too slow')
        if self.divide_mouse_v[0] == 0 and self.divide_mouse_v[1] == 0:
            # human_curve_dx.append(self.divide_mouse_v[0])
            # x += self.divide_mouse_v[0]
            # human_curve_x.append(x / 10)
            # human_curve_t.append(time.time())
            pass
        else:
            km.mouse_move(*self.divide_mouse_v)
            # if count < 2000:
            #     human_curve_dx.append(self.divide_mouse_v[0])
            #     x += self.divide_mouse_v[0]
            #     human_curve_x.append(x/10)
            #     human_curve_t.append(time.time())
            # elif count == 2000:
            #     plt.figure(figsize=(50, 50), dpi=100)
            #     plt.plot(human_curve_t, human_curve_dx, label='dx', linewidth=1)
            #     plt.plot(human_curve_t, human_curve_x, label='x')
            #     plt.legend()
            #     plt.savefig('aim_mouse_curve')
            # count += 1

    @staticmethod
    def custom_modf(value):
        int_value = int(value)
        float_value = value - int_value
        return float_value, int_value
