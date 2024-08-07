import threading
from time import time
import tkinter as tk
import winrawin
from pynput import keyboard, mouse
from cs_master.kmclass import KeyboardMouseClass as km


# interception.auto_capture_devices(keyboard=True, mouse=True)
# from matplotlib import pyplot as plt
# human_curve_dx = []
# human_curve_x = []
# human_curve_t = []
# count = 0


class BaseController:
    def __init__(self, assistant_class, detector_class, gui):
        super().__init__()
        self.gui = gui
        self.assistant = assistant_class
        self.detector = detector_class
        self.window = None
        self.run = False
        self.keyboard_listener = None
        self.mouse_listener = None
        self.m_listener_thread = threading.Thread(target=self.raw_mouse_listener)
        self.m_listener_thread.start()
        self.awp_scale = 1
        self.temp_shooting_mode = self.assistant.weapon_mode

    def keyboard_on_press(self, key):
        if key == keyboard.Key.alt_l:
            pass
            # self.assistant.print_setting()
            # self.assistant.fix_aim_assist = True
            # self.assistant.fix_auto_shoot = True
            # self.assistant.print_setting()
            # km().mouse_release()
        if key == keyboard.Key.shift_l:
            self.assistant.walk = True
        if key == keyboard.Key.ctrl_l:
            self.assistant.crouch = True
        try:
            if key.char == 'w' and 'w' not in self.assistant.pressed_keys:
                self.assistant.pressed_keys.append('w')
            if key.char == 'a' and 'a' not in self.assistant.pressed_keys:
                self.assistant.pressed_keys.append('a')
            if key.char == 's' and 's' not in self.assistant.pressed_keys:
                self.assistant.pressed_keys.append('s')
            if key.char == 'd' and 'd' not in self.assistant.pressed_keys:
                self.assistant.pressed_keys.append('d')
        except AttributeError:
            pass

    def keyboard_on_release(self, key):
        if key == keyboard.Key.alt_l:
            self.assistant.BURST_AIM_TOLERANCE = .6
            self.awp_scale = 1
            self.assistant.LOCK_RANGE = (150, 300)
            self.assistant.fix_aim_assist = False
            self.assistant.fix_auto_shoot = False
            self.assistant.weapon_mode = 'RIFLE'
            self.assistant.shooting_mode = 'One-tap'
            self.assistant.reset_reaction()
            self.assistant.shoot_interval = self.assistant.RIFLE_SHOOT_INTERVAL
            self.assistant.x_cold_down_mode = self.assistant.RIFLE_X_COLD_DOWN
            self.assistant.y_cold_down_mode = self.assistant.RIFLE_Y_COLD_DOWN
            self.detector.head_track = True
            self.detector.body_track = False
            self.assistant.print_setting()
            self.gui.update_setting_tabel()
            km().mouse_release()
        if key == keyboard.Key.shift_l:
            self.assistant.walk = False
        if key == keyboard.Key.ctrl_l:
            self.assistant.crouch = False
        if key == keyboard.Key.space:
            self.assistant.x_cold_down = -230
            self.assistant.y_cold_down = -230
            self.assistant.shoot_wait = -230
        try:
            if key.char == '1':
                self.assistant.shooting_mode = self.temp_shooting_mode
                self.assistant.knife = False
                self.assistant.print_setting()
                self.gui.update_setting_tabel()
            if key.char == '2':
                self.temp_shooting_mode = self.assistant.shooting_mode
                self.assistant.shooting_mode = 'One-tap'
                self.assistant.knife = False
                self.assistant.print_setting()
                self.gui.update_setting_tabel()
            if key.char == '3' or key.char == '4' or key.char == '5':
                self.temp_shooting_mode = self.assistant.shooting_mode
                self.assistant.knife = True
            if key.char == 'w' and 'w' in self.assistant.pressed_keys:
                self.assistant.pressed_keys.remove('w')
            if key.char == 'a' and 'a' in self.assistant.pressed_keys:
                self.assistant.pressed_keys.remove('a')
            if key.char == 's' and 's' in self.assistant.pressed_keys:
                self.assistant.pressed_keys.remove('s')
            if key.char == 'd' and 'd' in self.assistant.pressed_keys:
                self.assistant.pressed_keys.remove('d')
            if key.char == 'k':
                self.assistant.fix_auto_shoot = not self.assistant.fix_auto_shoot
                km().mouse_release()
                self.assistant.print_setting()
                self.gui.update_setting_tabel()
            if key.char == 'l':
                self.assistant.fix_aim_assist = not self.assistant.fix_aim_assist
                self.assistant.print_setting()
                self.gui.update_setting_tabel()
            if key.char == 'j':
                self.assistant.weapon_mode \
                    = self.assistant.weapon_modes[
                    (self.assistant.weapon_modes.index(self.assistant.weapon_mode) + 1) % 4]
                if self.assistant.weapon_mode == 'RIFLE':
                    self.detector.head_track = True
                    self.detector.body_track = False
                    self.assistant.shooting_mode = 'Spray'
                    self.assistant.reset_reaction()
                    self.assistant.shoot_interval = self.assistant.RIFLE_SHOOT_INTERVAL
                    self.assistant.x_cold_down_mode = self.assistant.RIFLE_X_COLD_DOWN
                    self.assistant.y_cold_down_mode = self.assistant.RIFLE_Y_COLD_DOWN
                    self.assistant.k = self.assistant.WEAK_STOP_TOLERANCE
                elif self.assistant.weapon_mode == 'PISTOL':
                    self.detector.head_track = True
                    self.detector.body_track = False
                    self.assistant.shooting_mode = 'One-tap'
                    self.assistant.reset_reaction()
                    self.assistant.shoot_interval = self.assistant.PISTOL_SHOOT_INTERVAL
                    self.assistant.x_cold_down_mode = self.assistant.PISTOL_X_COLD_DOWN
                    self.assistant.y_cold_down_mode = self.assistant.PISTOL_Y_COLD_DOWN
                    self.assistant.k = self.assistant.STRONG_STOP_TOLERANCE
                elif self.assistant.weapon_mode == 'AWP':
                    self.detector.head_track = False
                    self.detector.body_track = True
                    self.awp_scale = 2.75 / 1.7
                    self.assistant.BURST_AIM_TOLERANCE = .9
                    self.assistant.shooting_mode = 'One-tap'
                    self.assistant.LOCK_RANGE = (300, 300)
                    self.assistant.reset_reaction()
                    self.assistant.shoot_interval = self.assistant.PISTOL_SHOOT_INTERVAL
                    self.assistant.x_cold_down_mode = self.assistant.PISTOL_X_COLD_DOWN
                    self.assistant.y_cold_down_mode = self.assistant.PISTOL_Y_COLD_DOWN
                    self.assistant.k = self.assistant.STRONG_STOP_TOLERANCE
                elif self.assistant.weapon_mode == 'SMG':
                    self.detector.head_track = True
                    self.detector.body_track = False
                    self.assistant.shooting_mode = 'Spray'
                    self.assistant.reset_reaction()
                    self.assistant.shoot_interval = self.assistant.RIFLE_SHOOT_INTERVAL
                    self.assistant.x_cold_down_mode = self.assistant.RIFLE_X_COLD_DOWN
                    self.assistant.y_cold_down_mode = self.assistant.RIFLE_Y_COLD_DOWN
                    self.awp_scale = 1
                    self.assistant.BURST_AIM_TOLERANCE = .6
                    self.assistant.LOCK_RANGE = (150, 300)
                self.gui.update_setting_tabel()
                self.assistant.print_setting()
            if key.char == 'h':
                if self.assistant.weapon_mode in {'PISTOL', 'AWP'}:
                    print('Invalid, PISTOL/AWP Mode Can Only One-tap'.center(100, '*'))
                else:
                    self.assistant.shooting_mode \
                        = self.assistant.shooting_modes[
                        (self.assistant.shooting_modes.index(self.assistant.shooting_mode) + 1) % 2]
                    self.assistant.reset_reaction()
                    self.assistant.auto_pressing = False
                    self.assistant.shooting = False
                    self.assistant._start_shooting_time = None
                    self.assistant._end_shooting_time = time()
                    self.assistant.last_spray_last = self.assistant.recoil_time
                    if self.assistant.shooting_mode == 'Spray':
                        self.assistant.k = self.assistant.WEAK_STOP_TOLERANCE
                    elif self.assistant.shooting_mode == 'One-tap':
                        self.assistant.k = self.assistant.STRONG_STOP_TOLERANCE
                    self.assistant.print_setting()
                    km().mouse_release()  # safety ensure
                    self.gui.update_setting_tabel()
            if key.char == 'o':
                self.detector.body_track = not self.detector.body_track
                self.detector.head_track = not self.detector.head_track
                self.gui.update_setting_tabel()
        except AttributeError:
            pass

    def on_mouse_click(self, x, y, button, pressed):
        if button == mouse.Button.right:
            if pressed:
                if self.assistant.weapon_mode == 'AWP':
                    self.assistant.shoot_wait = -30 * self.assistant.f_scale
                    self.assistant.awp_auto_shoot = True
                    self.assistant.awp_aim_assist = True
                else:
                    pass
                    # self.assistant.alt_aim_assist = not self.assistant.alt_aim_assist
                    # self.assistant.auto_shoot = not self.assistant.auto_shoot
                self.assistant.print_setting()
            else:
                if self.assistant.weapon_mode == 'AWP':
                    self.assistant.awp_auto_shoot = False
                    self.assistant.awp_aim_assist = False
                else:
                    # self.assistant.alt_aim_assist = False
                    # self.assistant.auto_shoot = False
                    # km().mouse_release()
                    pass

    def raw_mouse_listener(self):
        self.window = tk.Tk()
        self.window.withdraw()
        # hwnd = win32gui.GetForegroundWindow()
        # hwnd = win32gui.FindWindow(None, "Steam")
        winrawin.hook_raw_input_for_window(self.window.winfo_id(), self.handle_event)
        self.window.mainloop()

    def handle_event(self, e: winrawin.RawInputEvent):
        if e.event_type == 'move':
            self.assistant.current_mouse_v = (
                    dx := (e.delta_x * self.awp_scale) / (2.7 * self.assistant.pixel_scale * 2),
                    dy := (e.delta_y * self.awp_scale) / (2.00 * self.assistant.pixel_scale * 2))
            self.assistant.mouse_rebuild[0] += dx
            self.assistant.mouse_rebuild[1] += dy
            self.assistant.mouse_history_value_memory[0].append(self.assistant.mouse_rebuild[0])
            self.assistant.mouse_history_value_memory[1].append(self.assistant.mouse_rebuild[1])
            self.assistant.mouse_history_time_memory.append(time())
            # if count < 4000:
            #     print(1)
            # elif 4000 < count < 5000:
            # human_curve_dx.append(e.delta_x)
            # human_curve_x.append(self.assistant.mouse_rebuild[0]/1.5)
            # human_curve_t.append(time())
            # elif count == 5000:
            #     plt.figure(figsize=(50, 50), dpi=100)
            #     plt.plot(human_curve_t, human_curve_dx, label='dx', linewidth=1)
            #     plt.plot(human_curve_t, human_curve_x, label='x')
            #     plt.legend()
            #     plt.savefig('mouse_curve')
            # count += 1
        if e.name == 'left':
            if e.event_type == 'down':
                self.assistant.shooting = True
                self.assistant.x_cold_down = -self.assistant.RIFLE_X_COLD_DOWN
                self.assistant.y_cold_down = -self.assistant.RIFLE_Y_COLD_DOWN
                self.assistant._start_shooting_time = time()
            elif e.event_type == 'up':
                self.assistant.shooting = False
                self.assistant._start_shooting_time = None
                self.assistant._end_shooting_time = time()
                self.assistant.last_spray_last = self.assistant.recoil_time
        # elif e.name == 'right':
        #     if e.event_type == 'down':
        #         if self.assistant.weapon_mode == 'AWP':
        #             self.assistant.shoot_wait = -30 * self.assistant.f_scale
        #             self.assistant.awp_auto_shoot = True
        #             self.assistant.awp_aim_assist = True
        #         else:
        #             self.assistant.alt_aim_assist = True
        #             self.assistant.auto_shoot = True
        #     if e.event_type == 'up':
        #         if self.assistant.weapon_mode == 'AWP':
        #             self.assistant.awp_auto_shoot = False
        #             self.assistant.awp_aim_assist = False
        #         else:
        #             self.assistant.alt_aim_assist = False
        #             self.assistant.auto_shoot = False
        #             km().mouse_release()
                # self.assistant.fix_aim_assist = not self.assistant.fix_aim_assist
                # self.assistant.fix_auto_shoot = not self.assistant.fix_auto_shoot
                # km().mouse_release()
                # self.assistant.print_setting()

    def get_a_started_listener(self):
        self.run = True
        keyboard_listener = keyboard.Listener(on_press=self.keyboard_on_press, on_release=self.keyboard_on_release)
        keyboard_listener.start()
        mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        mouse_listener.start()
        return keyboard_listener, mouse_listener

    def start_listener(self):
        self.run = True
        self.keyboard_listener, self.mouse_listener = self.get_a_started_listener()

    def end_listener(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        print('-----Keyboard Listener Stopped-----'.center(100))
        self.run = False
        # self.window.destroy()
        # self.m_listener_thread.join()


if __name__ == '__main__':
    from cs_master.assistant import Assistant
    from matplotlib import pyplot as plt
    from time import sleep

    assistant = Assistant()
    controller = BaseController(assistant)
    controller.start_listener()
    sleep(10)
    plt.figure(figsize=(50, 50), dpi=100)
    plt.plot(human_curve_t, human_curve_dx, label='human-dx')
    plt.plot(human_curve_t, human_curve_x, label='human-x')
    plt.legend()
    plt.savefig('human_mouse_curve.png')
    plt.show()
    # winsound.Beep(600, 600)
    # # win32api.keybd_event(17, 0, 0, 0)  # ctrl键位码是17
    # # win32api.keybd_event(0x11, 0, 0, 0)
    # # win32api.keybd_event(0x41, 0, 0, 0)
    # # win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
    # # win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    # print(controller.assist_class.mouse_rebuild)
    # # test()
    # controller.press_key('d')
    # print(1)
    # time.sleep(10)
    # # for _ in range(100):
    # #     controller.mouse_move(5, 5)
    # #     # interception.move_relative(5, 5)
    # #     time.sleep(0.1)
    # controller.release_key('d')
    # print(controller.assist_class.mouse_rebuild)
