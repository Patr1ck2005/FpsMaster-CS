import threading
from math import tanh, sin, cos
from time import time
from collections import deque
import numpy as np
from scipy.interpolate import interp1d
from collections import Counter

from cs_master.settings import *
from cs_master.kfilter import motion_kf, motion_translation_matrix
from cs_master.controller import BaseController  # strange
from cs_master.kmclass import KeyboardMouseClass as km
from cs_master.recoil_curves import RecoilCurve


class Assistant:
    def __init__(self):

        self.P = 0.6
        self.D = 0
        self.I = 0.6
        self.REACTION_TICK = 8
        self.LOCK_RANGE = (150, 300)
        self.WEAPON = 'ak47'
        self.ALT_WEAPON = 'usp'
        self.SMOOTH_TRANSITION_MOVE = False
        # debug value
        self.WEAK_STOP_TOLERANCE = 20
        self.STRONG_STOP_TOLERANCE = 10
        self.SPRAY_AIM_TOLERANCE = 1.2
        self.BURST_AIM_TOLERANCE = 0.8
        self.RIFLE_X_COLD_DOWN = 15
        self.RIFLE_Y_COLD_DOWN = 25
        self.PISTOL_X_COLD_DOWN = 30
        self.PISTOL_Y_COLD_DOWN = 100
        self.RIFLE_SHOOT_INTERVAL = 25
        self.PISTOL_SHOOT_INTERVAL = 70
        self.TARGET_CONTINUITY_SCALE = 4
        self.OPERATION_DELAY = 0.009
        self.AUTO_RECOIL_RECOVERY = 30

        self.M_THRESHOLD = 40
        self.M_SLOW_DOWN = 4
        self.M_ACCELERATION = 1

        # set default value
        self.shoot_interval = self.RIFLE_SHOOT_INTERVAL
        self.aim_tolerance = self.SPRAY_AIM_TOLERANCE
        self.x_cold_down_mode = self.RIFLE_X_COLD_DOWN
        self.y_cold_down_mode = self.RIFLE_Y_COLD_DOWN
        self._max_spray = 240
        self.k = self.STRONG_STOP_TOLERANCE
        self.auto_stop_mode = 240

        self.shoot_body = False
        self.DETECT_REGION_POS = (WINDOW_SIZE[0] / 2 - SHOT_SIZE[0] / 2, WINDOW_SIZE[1] / 2 - SHOT_SIZE[1] / 2)
        self.pixel_scale = 1280 / WINDOW_SIZE[0]
        self.f_scale = 2

        self.aim_assist = False
        self.alt_aim_assist = False
        self.fix_aim_assist = False
        self.awp_aim_assist = False
        self.auto_shoot = False
        self.awp_auto_shoot = False
        self.fix_auto_shoot = False
        self.hold_angle = False
        self.shooting_modes = ['One-tap', 'Spray']
        self.weapon_modes = ['RIFLE', 'PISTOL', 'AWP', 'SMG']
        # self.weapon_modes = ['RIFLE', 'PISTOL']
        self.weapons = ['ak47', 'm4a1', 'negev']
        self.auto_stop = False
        self.shooting_mode = 'One-tap'
        self.weapon_mode = 'RIFLE'

        self.shooting = False
        self.walk = False
        self.auto_aim = False
        self.auto_pressing = False
        self.dying = False
        self.crouch = False
        self.stand = True
        self.knife = True
        self.peek_stand = True
        self.peek = False
        self.lost_target = True
        self.recovery = False
        self.pressed_keys = []
        self._wait_time = 0
        self._update_time = None
        self.shoot_wait = 0
        self.recovery_tick = 0
        self._start_shooting_time = None
        self._end_shooting_time = time()
        self.auto_spray_tick = 0
        self.recoil_time = 0
        self.last_spray_last = 0
        self.auto_stop_tick = 0
        self.x_cold_down = 0
        self.y_cold_down = 0
        self.current_mouse_v = (0, 0)
        self.logitech_mouse_v = [0, 0]
        self.trigger = 0
        self.mouse_rebuild = [0, 0]
        self.detect_mouse_rebuild = [0, 0]
        self.mouse_init = [0, 0]
        self.accumulate_error = [0, 0]
        self.accumulate_errors = [deque(maxlen=10), deque(maxlen=10)]
        self.mouse_int_error = [0, 0]
        self.recoil_correct = [0, 0]
        self.raw_pos_info = None
        self.raw_size_info = None
        self.size_info = None
        self.target_r_pos = None
        self.sable_rebuild_y = None
        self.detect_time = None
        self.last_time = None
        self.mouse_derivative = None
        self.rebuild_pixel_pos = None
        self.pred_rebuild_pixel_pos = None
        self.rebuild_pixel_v = None
        self.pred_rebuild_pixel_v = None
        self.detect_delta_time = 0
        self.delay_time = 0
        self.pixel_pos_memory = [deque(maxlen=5), deque(maxlen=5)]
        self.raw_size_info_memory = [deque(maxlen=5), deque(maxlen=5)]
        self.raw_pos_info_memory = None
        self.detect_mouse_memory = [deque(maxlen=20), deque(maxlen=20)]
        self.mouse_history_value_memory = [deque(maxlen=100), deque(maxlen=100)]
        self.mouse_history_time_memory = deque(maxlen=100)
        self.motion_history = deque(maxlen=50)
        self.init_deque()
        self.maxlen = 0
        self.reset_reaction()
        self.kf = motion_kf

    @staticmethod
    def timeit(func):
        def wrapper(*args, **kwargs):
            start = time()
            func(*args, **kwargs)
            end = time()
            print(f'function {func.__name__} cost {end - start}s')

        return wrapper

    def reset_reaction(self):
        if self.shooting_mode == 'Spray':
            self.maxlen = self.REACTION_TICK * self.TARGET_CONTINUITY_SCALE
        else:
            if self.weapon_mode == 'AWP':
                self.maxlen = self.REACTION_TICK
            else:
                self.maxlen = self.REACTION_TICK * (self.TARGET_CONTINUITY_SCALE // 3)
        self.raw_pos_info_memory = [deque([None] * self.maxlen, maxlen=self.maxlen),
                                    deque([None] * self.maxlen, maxlen=self.maxlen)]

    def print_setting(self):
        pass
        # if True:
        #     dic = {
        #         'Weapon Mode': self.weapon_mode,
        #         'Shooting Mode': self.shooting_mode,
        #         'Aim Assist': self.aim_assist or self.alt_aim_assist or self.fix_aim_assist,
        #         'Auto Shoot': self.auto_shoot or self.fix_auto_shoot,
        #         'Auto Stop': self.auto_stop,
        #         'Reaction': f'  {self.REACTION_TICK}   ',
        #     }
        #     max_key_length = max(len(key) for key in dic.keys())
        #     print('---SETTINGS CHANGED---'.center(100, '*'))
        #     for key, value in dic.items():
        #         print('|', f'\t{key:{max_key_length}}\t||\t{value}\t'.center(90, '-'), '|')
        #     print(''.center(100, '-'))

    def init_deque(self):
        self.mouse_history_value_memory[0].append(0)
        self.mouse_history_value_memory[1].append(0)
        self.mouse_history_time_memory.append(time() - 5)

    def init_rebuild_target(self):
        self.init_filter(*self.raw_pos_info)
        self.mouse_init[0] = self.mouse_rebuild[0]
        self.mouse_init[1] = self.mouse_rebuild[1]
        for i in range(len(self.mouse_history_value_memory[0])):
            self.mouse_history_value_memory[0][i] -= self.mouse_init[0]
        for i in range(len(self.mouse_history_value_memory[1])):
            self.mouse_history_value_memory[1][i] -= self.mouse_init[1]
        self.mouse_rebuild = [0, 0]
        self.rebuild_pixel_pos = list(self.raw_pos_info)

        self.size_info = list(self.raw_size_info)
        self.pred_rebuild_pixel_pos = [0, 0]
        self.pred_rebuild_pixel_v = [0, 0]
        self.rebuild_pixel_v = [0, 0]
        self.rebuild_pixel_v = [0, 0]
        self.mouse_derivative = [0, 0]

    def get_info(self, info):
        # print(f'receive info {info}'.center(100, '*'))
        walk_scale = 2 if self.walk else 1
        if self.stand_check(self.k * walk_scale):
            self.stand = True
        else:
            self.stand = False
        if self.stand_check(30):
            if not self.peek_stand:
                self.peek = True
            self.peek_stand = True
        else:
            self.peek_stand = False
        self.save_motion()

        self.detect_time = info[4]
        self.delay_time = time() - self.detect_time
        if self.shooting:  # auto_pressing ignore
            self.recoil_time = ((time() - self._start_shooting_time)
                                + min(.8, max(0, (
                            self.last_spray_last - 3 * (self._start_shooting_time - self._end_shooting_time)))))
        else:
            self.recoil_time = max(0, min(.8, max(0, (
                    self.last_spray_last - 3 * (time() - self._end_shooting_time)))) - 3 * (
                                           time() - self._end_shooting_time))
        if info[0] is not None:
            self.raw_pos_info: tuple = self.trans_pos(info[:2])
        if info[0] is not None and not (
                abs(self.raw_pos_info[0]) > self.LOCK_RANGE[0] / 2 or self.raw_pos_info[1] > self.LOCK_RANGE[1] / 2):
            # print('TARGET OUT OF RANGE'.center(100))
            self.raw_size_info = info[2:4]
            if self.peek:
                # print('peek init')
                self.freeze_states()
                self.peek = False
            if self.lost_target:  # first get target before no target
                self._update_time = time()
                # print('First Spot Target'.center(100, '*'))
                self.last_time = self.detect_time
                self.raw_pos_info_memory[0].append(self.raw_pos_info[0])
                self.raw_pos_info_memory[1].append(self.raw_pos_info[1])
                self.raw_size_info_memory[0].append(self.raw_size_info[0])
                self.raw_size_info_memory[1].append(self.raw_size_info[1])
                self.pixel_pos_memory[0].append(self.raw_pos_info[0])
                self.pixel_pos_memory[1].append(self.raw_pos_info[1])
                if all(list(self.raw_pos_info_memory[0])[-self.REACTION_TICK:]):
                    print('Target Confirmed'.center(100, '-'))
                    self.lost_target = False
                    self.dying = False
                    # init rebuild
                    self.init_rebuild_target()

            elif self.last_time == self.detect_time:  # get same info special when after first get target:
                # print('note: get same info'.center(100, '*'))
                self._wait_time = time() - self._update_time
                self.process_former_mouse_pos()
                if all(list(self.raw_pos_info_memory[0])[-self.REACTION_TICK:]) or (
                        any(self.raw_pos_info_memory[0]) and self.target_r_pos is not None):
                    self.filter_predict(self.delay_time)
                    self.process_relative_pos()
            else:  # get target pos updated
                # print('get updated raw info'.center(100, '*'))
                self._update_time = time()
                self._wait_time = 0
                self.process_former_mouse_pos()
                self.detect_delta_time = self.detect_time - self.last_time
                self.last_time = self.detect_time
                self.rebuild_pixel_pos[0] = self.detect_mouse_rebuild[0] + self.raw_pos_info[0]
                self.rebuild_pixel_pos[1] = self.detect_mouse_rebuild[1] + self.raw_pos_info[1]
                self.rebuild_pixel_v[0] = (self.rebuild_pixel_pos[0] - self.kf.x[
                    1]) / self.detect_delta_time
                self.rebuild_pixel_v[1] = (self.rebuild_pixel_pos[1] - self.kf.x[
                    3]) / self.detect_delta_time
                self.raw_pos_info_memory[0].append(self.raw_pos_info[0])
                self.raw_pos_info_memory[1].append(self.raw_pos_info[1])
                self.raw_size_info_memory[0].append(self.raw_size_info[0])
                self.raw_size_info_memory[1].append(self.raw_size_info[1])
                self.pixel_pos_memory[0].append(self.rebuild_pixel_pos[0])
                self.pixel_pos_memory[1].append(self.rebuild_pixel_pos[1])
                if abs(self.rebuild_pixel_v[0]) > 5000 * (20 + self.size_info[0]) or abs(
                        self.rebuild_pixel_v[1] > 3000 * (20 + self.size_info[1])):
                    print(f'Force Init ({self.rebuild_pixel_v[0]}>{5000 * (20 + self.size_info[0])})'.center(100))
                    self.init_rebuild_target()
                else:
                    self.update_filter(self.detect_delta_time, *self.rebuild_pixel_pos)

                if all(list(self.raw_pos_info_memory[0])[-self.REACTION_TICK:]) or (
                        any(self.raw_pos_info_memory[0]) and self.target_r_pos is not None):
                    self.filter_predict(self.delay_time)
                    self.process_relative_pos()

                # print(f'delay time {self.delay_time}'.center(100, '-'))
                # print(f'key {self.pressed_keys}'.center(100))
        else:  # no target
            self.raw_pos_info = None
            self.raw_size_info = None
            self.raw_pos_info_memory[0].append(None)
            self.raw_pos_info_memory[1].append(None)
            self.pixel_pos_memory[0].append(None)
            self.pixel_pos_memory[1].append(None)
            if (not self.lost_target) and any(self.raw_pos_info_memory[0]) and self.fix_auto_shoot:
                # print('MISS TARGET'.center(100, '-'))
                self.filter_predict(self.delay_time)
                self.process_relative_pos()
            else:
                if not self.lost_target:
                    print('LOST TARGET'.center(100, '-'))
                    self.recovery = True
                self.lost_target = True
                self.shoot_wait = 0
                self.x_cold_down = 0
                self.y_cold_down = 0
                self.recovery_tick += 1
                if self.shooting_mode == 'Spray':
                    if self.shooting and self.target_r_pos is not None:
                        # self.filter_predict(self.delay_time)
                        # self.recovery = False
                        self.process_relative_pos()
                        self.shoot_body = True
                    elif self.recovery and self.target_r_pos is not None:
                        # self.filter_predict(self.delay_time)
                        self.pred_rebuild_pixel_pos[1] -= self.first_rebuild_pixel_y
                        self.process_relative_pos()
                        print('Recovery')
                    else:
                        self.clear_states()
                        # self.process_relative_pos()
                        self.shoot_body = False
                else:
                    self.clear_states()
                    self.shoot_body = False

    def take_action(self):
        self.auto_aim = False
        if not self.knife:
            if self.auto_stop:
                self.move_assist()
            if (self.target_r_pos is not None and not self.dying) and (
                    self.aim_assist or self.alt_aim_assist or self.fix_aim_assist):
                if (self.shooting_mode == 'One-tap' and (not self.shooting)
                        and (self.weapon_mode != 'AWP' or (self.weapon_mode == 'AWP' and self.awp_aim_assist))):
                    if self.y_cold_down > 0 and self.x_cold_down > 0:
                        self.aim_action(mode='xy')
                    elif self.y_cold_down < 0 < self.x_cold_down:
                        self.aim_action(mode='x')
                elif self.shooting_mode == 'Spray' or self.shoot_body:
                    self.recovery_check()
                    self.recoil_correct = [x / self.pixel_scale for x in
                                           getattr(RecoilCurve(), self.WEAPON)(self.recoil_time)]
                    if self.recovery:
                        self.aim_action(mode='y')
                        print('recovery')
                    else:
                        if self.y_cold_down > 0 and self.x_cold_down > 0 or True:
                            self.aim_action(mode='xy', recoil=self.recoil_correct)
                        elif self.y_cold_down < 0 < self.x_cold_down:
                            self.aim_action(mode='x', recoil=self.recoil_correct)
                    # if self.lost_target:
                    #     print('continuing', self.logitech_mouse_v)
                    # else:
                    #     print('normal', self.logitech_mouse_v)
            if self.weapon_mode == 'AWP':
                if self.awp_auto_shoot and self.fix_auto_shoot:
                    self.shoot_action()
            elif self.auto_shoot or self.fix_auto_shoot:
                self.shoot_action()
        if not self.auto_aim:
            self.logitech_mouse_v[0] = round(self.logitech_mouse_v[0] / 1.5, 1)
            self.logitech_mouse_v[1] = round(self.logitech_mouse_v[1] / 1.5, 1)
        self.shoot_wait += 1
        self.x_cold_down += 1
        self.y_cold_down += 1
        self.auto_stop_tick += 1
        return self.logitech_mouse_v

    def shoot_action(self):
        if (self.shooting_mode == 'One-tap' and self.shoot_wait >= 0 and not self.shooting
                and self.aim_check(c=self.BURST_AIM_TOLERANCE) and self.stand):
            threading.Thread(target=km().mouse_click).start()
            # km().mouse_click()
            print('Auto One-tap'.center(100))
            self.shoot_wait = -self.shoot_interval * self.f_scale
            self.x_cold_down = -self.x_cold_down_mode * self.f_scale
            self.y_cold_down = -self.y_cold_down_mode * self.f_scale
        if self.shooting_mode == 'Spray':
            if self.shooting:
                self.auto_spray_tick += 1
            if self.aim_check(c=self.SPRAY_AIM_TOLERANCE, recoil=self.recoil_correct) and (
                    not self.shooting) and (self.stand or self.weapon_mode == 'SMG') and self.shoot_wait >= 0:
                self.auto_spray_tick = -self._max_spray * self.f_scale
                if not self.auto_pressing:
                    self._start_shooting_time = time()
                    self.auto_pressing = True  # ensure
                    # self.shooting = True  # ensure
                self.alt_aim_assist = True  # auto aim while shooting
                threading.Thread(target=km().mouse_press).start()
                self.SPRAY_AIM_TOLERANCE *= 3
                self.shoot_wait = -self.shoot_interval * self.f_scale
                # km().mouse_press()
                self.recoil_time += 0.1
            if ((self.lost_target and self.auto_pressing)
                    or (not self.lost_target and self.auto_pressing and not self.stand)):
                threading.Thread(target=km().mouse_release).start()
                self.SPRAY_AIM_TOLERANCE /= 3
                # km().mouse_release()
                self.auto_pressing = False
                self.alt_aim_assist = False

    def aim_action(self, recoil=(0, 0), mode='xy'):
        _K_p = self.P / self.f_scale
        _K_d = self.D / self.f_scale
        _K_i = 1 * self.I / (1 * self.f_scale)
        # size_scale = (self.size_info[0] * self.size_info[1]) / (WINDOW_SIZE[0] * WINDOW_SIZE[1])
        dx = self.target_r_pos[0] - recoil[0]
        dy = self.target_r_pos[1] - recoil[1]
        if mode == 'xy':
            _K_x = 1
            _K_y = 1
        elif mode == 'x':
            _K_x = 1
            _K_y = 0
        else:
            _K_x = 0
            _K_y = 1
            print(dy)
        old_logitech_mouse_v = self.logitech_mouse_v.copy()
        if self.SMOOTH_TRANSITION_MOVE:
            ddx = self.accumulate_func(dx, 1.5)
            ddy = self.accumulate_func(dy, 1.5)
        else:
            ddx = dx
            ddy = dy
        self.logitech_mouse_v[0] = _K_x * (_K_p * self.motion_func(ddx)
                                           + _K_d * self.mouse_derivative[0]
                                           + _K_i * self.accumulate_error[0] * self.near_head_showdown(
                    self.accumulate_error[0] / 10, 1, power=2)
                                           + 3 * sin(dy / (40 / self.pixel_scale)) ** 2) * self.pixel_scale / 2
        # print('1', _K_p * self.motion_func(ddx))
        # print(self.accumulate_error[0]/20)
        # print('mu', self.near_head_showdown(self.accumulate_error[1]/20, 3, power=2))
        # print('2', _K_i * self.accumulate_error[0] * self.near_head_showdown(self.accumulate_error[0]/10, 1, power=2))
        self.logitech_mouse_v[1] = _K_y * 0.95 * (_K_p * self.motion_func(ddy)
                                                  + _K_d * self.mouse_derivative[1]
                                                  + _K_i * self.accumulate_error[1] * self.near_head_showdown(
                    self.accumulate_error[1] / 10, 1, power=2)
                                                  + 4 * sin(dx / (30 / self.pixel_scale)) ** 2) * self.pixel_scale / 2
        self.logitech_mouse_v[0] = max(old_logitech_mouse_v[0] * 0.95 - self.M_ACCELERATION,
                                       min(old_logitech_mouse_v[0] * 0.95 + self.M_ACCELERATION,
                                           self.logitech_mouse_v[0]))
        self.logitech_mouse_v[1] = max(old_logitech_mouse_v[1] * 0.95 - self.M_ACCELERATION,
                                       min(old_logitech_mouse_v[1] * 0.95 + self.M_ACCELERATION,
                                           self.logitech_mouse_v[1]))
        self.auto_aim = True

    def filter_predict(self, delay):
        # self.dying = True
        self.pred_rebuild_pixel_pos[0], self.pred_rebuild_pixel_v[0], self.pred_rebuild_pixel_pos[1], \
            self.pred_rebuild_pixel_v[1] \
            = motion_translation_matrix(delay + self.OPERATION_DELAY) @ self.kf.x
        # print(f'predict pos:{self.pred_rebuild_pixel_pos} v:{self.rebuild_pixel_v}'.center(100, '*'))
        # print(f'pred forward x {self.pred_rebuild_pixel_pos[0] - self.rebuild_pixel_pos[0]}')

    def init_filter(self, x, y):
        self.kf.x = np.array([x, 0, y, 0])

    def update_filter(self, dt, x, y):
        self.kf.predict(F=motion_translation_matrix(dt))
        self.kf.update(z=np.array([x, y]))

    def move_assist(self):
        if 'a' in self.pressed_keys and 'd' not in self.pressed_keys and self.auto_stop_tick > 0:
            if not self.stand and (not self.lost_target):
                km().release_key('a')
                km().press_key('d')
                # self.auto_stop_tick = -self.auto_stop_mode
                print('saw while moving')
        elif 'd' in self.pressed_keys and 'a' not in self.pressed_keys and self.auto_stop_tick > 0:
            if not self.stand and (not self.lost_target):
                km().release_key('d')
                km().press_key('a')
                print('saw while moving')
                # self.auto_stop_tick = -self.auto_stop_mode
        if self.stand and (not self.lost_target) and any(self.pressed_keys):
            km().release_key('w')
            km().release_key('a')
            km().release_key('s')
            km().release_key('d')

    def process_relative_pos(self):
        self.size_info[0] = np.mean(self.raw_size_info_memory[0])
        self.size_info[1] = np.mean(self.raw_size_info_memory[1])
        if self.target_r_pos is None:
            # need to init
            self.target_r_pos = [0, 0]
            self.mouse_derivative = [0, 0]
            self.target_r_pos[0] = self.pred_rebuild_pixel_pos[0] - self.mouse_rebuild[0]
            self.target_r_pos[1] = self.pred_rebuild_pixel_pos[1] - self.mouse_rebuild[1]
        else:
            _old_target_r_pos = self.target_r_pos.copy()
            self.target_r_pos[0] = self.pred_rebuild_pixel_pos[0] - self.mouse_rebuild[0]
            self.target_r_pos[1] = self.pred_rebuild_pixel_pos[1] - self.mouse_rebuild[1]
            self.mouse_derivative[0] = (self.target_r_pos[0] - _old_target_r_pos[0])
            self.mouse_derivative[1] = (self.target_r_pos[1] - _old_target_r_pos[1])
        x = max(-5 / self.pixel_scale, min(self.target_r_pos[0], 5 / self.pixel_scale))
        y = max(-5 / self.pixel_scale, min(self.target_r_pos[1], 5 / self.pixel_scale))
        # x = self.accumulate_func(self.target_r_pos[0])
        # y = self.accumulate_func(self.target_r_pos[1])
        self.accumulate_errors[0].append(x)
        self.accumulate_errors[1].append(y)
        self.accumulate_error[0] = sum(self.accumulate_errors[0])
        self.accumulate_error[1] = sum(self.accumulate_errors[1])

    def process_former_mouse_pos(self):
        # begin_time = self.mouse_history_time_memory[0]
        latest_time = self.mouse_history_time_memory[-1]  # in case history updated while following steps
        self.manual_save_mouse()
        self.detect_mouse_rebuild[0] = (interp1d(self.mouse_history_time_memory, self.mouse_history_value_memory[0])
            (max(
            min(latest_time, self._wait_time + self.detect_time - self.OPERATION_DELAY),
            self.mouse_history_time_memory[0])))
        if self._wait_time + self.detect_time - self.OPERATION_DELAY < self.mouse_history_time_memory[0]\
                or self._wait_time + self.detect_time - self.OPERATION_DELAY < self.mouse_history_time_memory[0] > latest_time:
            print('early')
        self.detect_mouse_rebuild[1] = (interp1d(self.mouse_history_time_memory, self.mouse_history_value_memory[1])
            (max(
            min(latest_time, self._wait_time + self.detect_time - self.OPERATION_DELAY),
            self.mouse_history_time_memory[0])))

    def trans_pos(self, pos):
        return self.DETECT_REGION_POS[0] + pos[0] - CENTER_POS[0], self.DETECT_REGION_POS[1] + pos[1] - CENTER_POS[
            1] - 30

    def aim_check(self, c, recoil=(0, 0)):
        if self.target_r_pos is None:
            return False
        else:
            if ((self.target_r_pos[0] - recoil[0]) / (1 + self.size_info[0] / 2)) ** 2 + (
                    (self.target_r_pos[1] - recoil[1]) / (1 + self.size_info[1] / 2.5)) ** 2 < c ** 2:
                return True
            else:
                return False

    def recovery_check(self):
        if self.recovery:
            if abs(self.target_r_pos[1]) < 2:
                print('recovery over')
                self.recovery = False

    def stand_check(self, k):
        elements = [element for tpl in self.motion_history for element in tpl]
        count_dict = Counter(elements)
        adad = count_dict['a'] - count_dict['d']
        wsws = count_dict['w'] - count_dict['s']
        if (abs(adad) < k and abs(wsws) < k) or self.crouch:
            return True
        else:
            return False

    def manual_save_mouse(self):
        self.mouse_history_value_memory[0].append(self.mouse_rebuild[0])
        self.mouse_history_value_memory[1].append(self.mouse_rebuild[1])
        self.mouse_history_time_memory.append(time())

    def clear_states(self):
        self.init_filter(0, 0)
        self.accumulate_error = [0, 0]
        self.logitech_mouse_v = [0, 0]
        self.target_r_pos = None
        self.mouse_derivative = None
        self.rebuild_pixel_v = None
        self.rebuild_pixel_pos = None
        self.pred_rebuild_pixel_pos = None
        self.pred_rebuild_pixel_v = None
        self.rebuild_pixel_v = None
        self.size_info = None
        self.raw_size_info_memory[0].clear()
        self.raw_size_info_memory[1].clear()

    def freeze_states(self):
        self.kf.x[1] = 0
        self.kf.x[3] = 0

    def motion_func(self, delta):
        def sgn(x):
            if x > 0:
                return 1
            else:
                return -1

        n = 3 / self.pixel_scale
        m = self.M_THRESHOLD
        # return n * sgn(delta) * (delta / n) ** 2 / math.sqrt((delta / n) ** 4 + m)
        # n = 80
        # return n * m * tanh(delta / m) * (delta ** 4 / (delta ** 4 + self.size_info[0]**4))
        return n * m * tanh(delta / m) * (delta ** 4 / (delta ** 4 + (1 + self.size_info[0] / self.M_SLOW_DOWN) ** 4))
        # return delta

    def near_head_showdown(self, delta, c, power=4):
        return delta ** power / (delta ** power + (1 + self.size_info[0] / c) ** power)

    def save_motion(self):
        self.motion_history.append(tuple(self.pressed_keys))

    def accumulate_func(self, x, power: float = 4):
        if abs(x) > self.size_info[0]:
            x /= (abs(x) / (self.size_info[0])) ** power
        else:
            pass
        return x

    @staticmethod
    def sgn(x):
        if x >= 0:
            return 1
        else:
            return -1

    @staticmethod
    def range_limit(domain, x):
        max_value = max(domain)
        min_value = min(domain)
        if x > max_value:
            return max_value
        elif x > min_value:
            return x
        else:
            return min_value


if __name__ == '__main__':
    pass
