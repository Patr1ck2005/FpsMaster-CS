import os
from math import log10
import sys
from datetime import datetime
import hashlib
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QCheckBox, QPushButton, QVBoxLayout, QWidget, \
    QLineEdit, QFormLayout, QComboBox, QMessageBox, QHBoxLayout, QAction, QPlainTextEdit, QFrame, QTableWidget, \
    QTableWidgetItem

from cs_master.main_loop import MainLoop


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = None
        self.setWindowTitle("登录")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        label_username = QLabel("用户名:")
        self.lineEdit_username = QLineEdit()
        layout.addWidget(label_username)
        layout.addWidget(self.lineEdit_username)

        label_password = QLabel("密码:")
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_password)
        layout.addWidget(self.lineEdit_password)

        label_security_key = QLabel("访问密匙:")
        self.label_security_key = QLineEdit()
        self.label_security_key.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_security_key)
        layout.addWidget(self.label_security_key)

        button_login = QPushButton("登录")
        button_login.clicked.connect(self.login)
        layout.addWidget(button_login)

        self.setLayout(layout)

    def login(self):
        # 在这里编写登录逻辑
        # 获取用户名和密码输入框的内容，进行验证
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        security_key = self.label_security_key.text()
        # 假设正确的用户名和密码分别是 "admin" 和 "password"
        if (username == "admin" and password == "jake200555") or security_key == self.generate_daily_security_key() or security_key == self.generate_monthly_security_key():
            # 如果验证成功，切换到主界面
            self.switch_to_main_widget()
        else:
            # 如果验证失败，弹出错误提示框
            self.switch_to_main_widget()
            QMessageBox.warning(self, "登录失败", "访问密匙错误！请联系作者获取密匙")

    def switch_to_main_widget(self):
        # 切换到主界面
        self.close()
        self.main_window = MainWindow()
        self.main_window.show()

    @staticmethod
    def generate_daily_security_key():
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")  # 将日期转换为字符串形式，例如 "2024-03-11"
        date_string += 'daily'
        # 使用SHA-256哈希函数生成密钥
        sha256 = hashlib.sha256()
        sha256.update(date_string.encode('utf-8'))
        security_key = sha256.hexdigest()
        return security_key

    @staticmethod
    def generate_monthly_security_key():
        now = datetime.now()
        date_string = now.strftime("%Y-%m")  # 将日期转换为字符串形式，例如 "2024-03"
        date_string += 'monthly'
        # 使用SHA-256哈希函数生成密钥
        sha256 = hashlib.sha256()
        sha256.update(date_string.encode('utf-8'))
        security_key = sha256.hexdigest()
        return security_key


class ParamWidget(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        layout = QHBoxLayout()
        self.label = QLabel(name)
        self.line_edit = QLineEdit()
        self.line_edit.setFixedWidth(35)  # 设置固定的宽度为 30 像素
        self.line_edit.setFixedHeight(20)  # 设置固定的高度为 30 像素
        self.line_edit.setReadOnly(False)  # 允许编辑
        self.line_edit.returnPressed.connect(self.handle_return_pressed)  # 连接 returnPressed 信号到槽函数
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    def set_value(self, value):
        self.line_edit.setText(str(value))

    def handle_return_pressed(self):
        new_value = self.line_edit.text()
        # 在此处处理新值，例如将其转换为整数并执行其他操作
        print(f"New value: {new_value}")
        return new_value  # 返回新值

    def get_value(self):
        return float(self.line_edit.text())


class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(190)
        self.setColumnCount(3)  # 设置表格的列数为3
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["功能切换", "键", '当前'])  # 设置表格的列标签
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalHeader().setVisible(False)
        self.setColumnWidth(0, self.width() - 110)  # 设置第一列的宽度为100像素
        self.setColumnWidth(1, 40)  # 设置第二列的宽度为150像素
        self.setColumnWidth(2, 70)  # 设置第二列的宽度为150像素
        self.add_row(["武器模式", "h", "RIFLE"])
        self.add_row(["点射/扫射", "j", "One-tap"])
        self.add_row(["辅助瞄准Y/N", "l", "N"])
        self.add_row(["辅助开火Y/N", "k", "N"])
        self.add_row(["辅助急停Y/N", "-", "N"])
        self.cellChanged.connect(self.cell_changed_handler)

    def add_row(self, data):
        row_count = self.rowCount()  # 获取表格的行数
        self.insertRow(row_count)  # 插入新行
        for column, item in enumerate(data):
            table_item = QTableWidgetItem(item)  # 创建一个表格项
            self.setItem(row_count, column, table_item)  # 将表格项添加到指定位置
            if column == 0:
                table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)  # 设置第一列为只读

    def cell_changed_handler(self, row, column):
        item = self.item(row, column)
        new_value = item.text()
        # 在这里根据需要执行不同的函数或逻辑
        print(f"单元格 ({row}, {column}) 内容发生变化，新值为: {new_value}")


class CustomParamSlider(QHBoxLayout):
    def __init__(self, name, slider_domain=(0, 100), interval=100, length=25, scale=False, parent=None, linear_scale:float=1):
        super().__init__(parent)
        self.linear_scale = linear_scale
        self.scale = scale
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)  # 设置滑动条为水平方向
        self.slider.setTickPosition(QSlider.TicksAbove)  # 将刻度线显示在滑动条的上方
        self.slider.setTickInterval(interval)  # 设置刻度线的间隔为 100
        self.slider.setMinimum(slider_domain[0])  # 设置滑动条的最小值为 0
        self.slider.setMaximum(slider_domain[-1])  # 设置滑动条的最大值为 100
        self.slider.valueChanged.connect(self.update_slider)
        self.param = ParamWidget(name)
        self.param.line_edit.setFixedWidth(length)
        self.param.line_edit.returnPressed.connect(self.update_param)
        self.update_slider()
        self.addWidget(self.param, 1)
        self.addWidget(self.slider, 3)

    def update_slider(self):
        value = self.slider.value()
        if self.scale:
            self.param.set_value(round(1.965 - log10(10 + (100 - value)) / 1.04, 2))
        else:
            self.param.set_value(round(value*self.linear_scale, 2))
        self.slider.setValue(value)

    def update_param(self):
        value = float(self.param.handle_return_pressed())
        self.param.set_value(round(value, 2))
        if self.scale:
            self.slider.setValue(int(110 - pow(10, 1.965 * 1.04 - 1.04 * value)))
        else:
            self.slider.setValue(int(value/self.linear_scale))

    def set_value(self, value):
        self.param.set_value(round(value, 2))
        if self.scale:
            self.slider.setValue(int(110 - pow(10, 1.965 * 1.04 - 1.04 * value)))
        else:
            self.slider.setValue(int(value/self.linear_scale))


class DebugSettingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setParent(parent)
        self.setWindowTitle("调试界面")
        self.setGeometry(100, 100, 800, 400)
        self.parent.add_line_in_console('Debug parameters', '调试参数')

        # 创建顶层部分
        top_layout = QFormLayout(self)
        top_label = QLabel("全局")
        top_layout.addRow(top_label)

        self.cps_11 = CustomParamSlider('TARGET_CONTINUITY_SCALE', slider_domain=(1, 20), interval=2)
        self.cps_12 = CustomParamSlider('OPERATION_DELAY(ms)', slider_domain=(0, 100), interval=10)
        self.cps_13 = CustomParamSlider('M_THRESHOLD', slider_domain=(1, 1000), interval=100, linear_scale=0.1, length=35)
        self.cps_14 = CustomParamSlider("M_SLOW_DOWN", slider_domain=(1, 50), interval=10, linear_scale=0.1)
        self.cps_15 = CustomParamSlider("M_ACCELERATION", slider_domain=(0, 50), interval=5, linear_scale=0.1)
        self.cps_16 = CustomParamSlider('CONF_THRESHOLD', slider_domain=(1, 10), interval=1, linear_scale=0.1)
        self.cps_11.set_value(self.parent.main_loop.assistant.TARGET_CONTINUITY_SCALE)
        self.cps_12.set_value(self.parent.main_loop.assistant.OPERATION_DELAY*1000)
        self.cps_13.set_value(self.parent.main_loop.assistant.M_THRESHOLD)
        self.cps_14.set_value(self.parent.main_loop.assistant.M_SLOW_DOWN)
        self.cps_15.set_value(self.parent.main_loop.assistant.M_ACCELERATION)
        self.cps_16.set_value(self.parent.main_loop.detector.HEAD_CONF_THRES)
        self.cps_11.slider.valueChanged.connect(self.update_assistant)
        self.cps_12.slider.valueChanged.connect(self.update_assistant)
        self.cps_13.slider.valueChanged.connect(self.update_assistant)
        self.cps_14.slider.valueChanged.connect(self.update_assistant)
        self.cps_15.slider.valueChanged.connect(self.update_assistant)
        self.cps_16.slider.valueChanged.connect(self.update_assistant)
        top_layout.addRow(self.cps_16)
        top_layout.addRow(self.cps_11)
        top_layout.addRow(self.cps_12)
        top_layout.addRow(self.cps_13)
        top_layout.addRow(self.cps_14)
        top_layout.addRow(self.cps_15)

        # 创建左右部分
        middle_layout = QHBoxLayout(self)
        middle_right_layout = QFormLayout(self)
        middle_left_layout = QFormLayout(self)
        middle_left_layout.addRow(QLabel("扫射模式"))
        middle_right_layout.addRow(QLabel("点射模式"))

        self.cps_1 = CustomParamSlider('WEAK_STOP_TOLERANCE', slider_domain=(0, 49), interval=10)
        self.cps_2 = CustomParamSlider('SPRAY_AIM_TOLERANCE', slider_domain=(0, 30), interval=10, linear_scale=0.1)
        self.cps_3 = CustomParamSlider('RIFLE_X_COLD_DOWN', slider_domain=(0, 200), interval=10)
        self.cps_4 = CustomParamSlider("RIFLE_Y_COLD_DOWN", slider_domain=(0, 200), interval=10)
        self.cps_5 = CustomParamSlider("RIFLE_SHOOT_INTERVAL", slider_domain=(0, 200), interval=10)
        self.cps_1.set_value(self.parent.main_loop.assistant.WEAK_STOP_TOLERANCE)
        self.cps_2.set_value(self.parent.main_loop.assistant.SPRAY_AIM_TOLERANCE)
        self.cps_3.set_value(self.parent.main_loop.assistant.RIFLE_X_COLD_DOWN)
        self.cps_4.set_value(self.parent.main_loop.assistant.RIFLE_Y_COLD_DOWN)
        self.cps_5.set_value(self.parent.main_loop.assistant.RIFLE_SHOOT_INTERVAL)
        self.cps_1.slider.valueChanged.connect(self.update_assistant)
        self.cps_2.slider.valueChanged.connect(self.update_assistant)
        self.cps_3.slider.valueChanged.connect(self.update_assistant)
        self.cps_4.slider.valueChanged.connect(self.update_assistant)
        self.cps_5.slider.valueChanged.connect(self.update_assistant)
        middle_left_layout.addRow(self.cps_1)
        middle_left_layout.addRow(self.cps_2)
        middle_left_layout.addRow(self.cps_3)
        middle_left_layout.addRow(self.cps_4)
        middle_left_layout.addRow(self.cps_5)

        self.cps_6 = CustomParamSlider('STRONG_STOP_TOLERANCE', slider_domain=(0, 49), interval=10)
        self.cps_7 = CustomParamSlider('BURST_AIM_TOLERANCE', slider_domain=(0, 30), interval=10, linear_scale=0.1)
        self.cps_8 = CustomParamSlider('PISTOL_X_COLD_DOWN', slider_domain=(0, 200), interval=10)
        self.cps_9 = CustomParamSlider("PISTOL_Y_COLD_DOWN", slider_domain=(0, 200), interval=10)
        self.cps_10 = CustomParamSlider("PISTOL_SHOOT_INTERVAL", slider_domain=(0, 200), interval=10)
        self.cps_6.set_value(self.parent.main_loop.assistant.STRONG_STOP_TOLERANCE)
        self.cps_7.set_value(self.parent.main_loop.assistant.BURST_AIM_TOLERANCE)
        self.cps_8.set_value(self.parent.main_loop.assistant.PISTOL_X_COLD_DOWN)
        self.cps_9.set_value(self.parent.main_loop.assistant.PISTOL_Y_COLD_DOWN)
        self.cps_10.set_value(self.parent.main_loop.assistant.PISTOL_SHOOT_INTERVAL)
        self.cps_6.slider.valueChanged.connect(self.update_assistant)
        self.cps_7.slider.valueChanged.connect(self.update_assistant)
        self.cps_8.slider.valueChanged.connect(self.update_assistant)
        self.cps_9.slider.valueChanged.connect(self.update_assistant)
        self.cps_10.slider.valueChanged.connect(self.update_assistant)
        middle_right_layout.addRow(self.cps_6)
        middle_right_layout.addRow(self.cps_7)
        middle_right_layout.addRow(self.cps_8)
        middle_right_layout.addRow(self.cps_9)
        middle_right_layout.addRow(self.cps_10)

        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)  # 设置分割线为水平方向
        h_line.setFrameShadow(QFrame.Sunken)  # 设置分割线样式

        v_line = QFrame()
        v_line.setFrameShape(QFrame.VLine)  # 设置分割线为竖直方向
        v_line.setFrameShadow(QFrame.Sunken)  # 设置分割线样式

        middle_layout.addLayout(middle_left_layout)
        middle_layout.addWidget(v_line)
        middle_layout.addLayout(middle_right_layout)

        # 设置布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(h_line)
        main_layout.addLayout(middle_layout)

        widget = QWidget(self)
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def update_assistant(self):
        self.parent.main_loop.detector.HEAD_CONF_THRES = float(self.cps_16.param.get_value())
        self.parent.main_loop.assistant.WEAK_STOP_TOLERANCE = int(self.cps_1.param.get_value())
        self.parent.main_loop.assistant.SPRAY_AIM_TOLERANCE = float(self.cps_2.param.get_value())
        self.parent.main_loop.assistant.RIFLE_X_COLD_DOWN = int(self.cps_3.param.get_value())
        self.parent.main_loop.assistant.RIFLE_Y_COLD_DOWN = int(self.cps_4.param.get_value())
        self.parent.main_loop.assistant.RIFLE_SHOOT_INTERVAL = int(self.cps_5.param.get_value())

        self.parent.main_loop.assistant.STRONG_STOP_TOLERANCE = int(self.cps_6.param.get_value())
        self.parent.main_loop.assistant.BURST_AIM_TOLERANCE = float(self.cps_7.param.get_value())
        self.parent.main_loop.assistant.PISTOL_X_COLD_DOWN = int(self.cps_8.param.get_value())
        self.parent.main_loop.assistant.PISTOL_Y_COLD_DOWN = int(self.cps_9.param.get_value())
        self.parent.main_loop.assistant.PISTOL_SHOOT_INTERVAL = int(self.cps_10.param.get_value())

        self.parent.main_loop.assistant.TARGET_CONTINUITY_SCALE = int(self.cps_11.param.get_value())
        self.parent.main_loop.assistant.reset_reaction()
        self.parent.main_loop.assistant.OPERATION_DELAY = int(self.cps_12.param.get_value())*1e-3
        self.parent.main_loop.assistant.M_THRESHOLD = float(self.cps_13.param.get_value())
        self.parent.main_loop.assistant.M_SLOW_DOWN = float(self.cps_14.param.get_value())
        self.parent.main_loop.assistant.M_ACCELERATION = float(self.cps_15.param.get_value())
        self.parent.add_line_in_console('Parameters updated', '已更新参数')


class ChangelogWindow(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("更新日志")
        self.setReadOnly(True)
        self.setGeometry(100, 100, 300, 200)
        self.setPlainText(
            """
            版本 0.0 (2024/3/4):
            - Hello! FpsMaster！这是来自Patrick的FpsMaster for CS2
            
            版本 1.0 (2024/3/5):
            - 修复了切屏导致截图出错的问题，现在程序运行基本稳定。
            
            版本 1.1 (2024/3/6):
            - 完善gui，现在可以在游戏外进行可视化调参
            
            版本 2.0 (2024/3/8):
            - 首次加入敌友识别。
            
            版本 3.0 (2024/3/13):
            - 加入静步检测、狙击模式，监督检测窗口，同时优化UI、用户交互体验，优化目标检测。修改了一些默认参数。敌友识别更加精确。
            """
        )


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.debug_settings_window = None
        self.main_loop = MainLoop(self)

        self.is_predicting = False  # 预测状态标志变量

        self.setWindowTitle("CsMaster")
        self.setGeometry(100, 100, 600, 700)
        self.line_by_line_text_edit = QPlainTextEdit()
        self.line_by_line_text_edit.setReadOnly(True)  # 设置为只读模式，禁止用户编辑文本
        self.add_line_in_console("""WELCOME, CS-MASTER!
    版本 0.0 (2024/3/4):
    - Hello! FpsMaster！这是来自Patrick的FpsMaster for CS2
    
    版本 1.0 (2024/3/5):
    - 修复了切屏导致截图出错的问题，现在程序运行基本稳定。
    
    版本 1.1 (2024/3/6):
    - 完善gui，现在可以在游戏外进行可视化调参
    
    版本 2.0 (2024/3/8):
    - 首次加入敌友识别。
    
    版本 3.0 (2024/3/13):
    - 加入静步检测、狙击模式，监督检测窗口，同时优化UI、用户交互体验，优化目标检测。修改了一些默认参数。敌友识别更加精确。
            """, '欢迎使用 CsMaster!')

        menu_bar = self.menuBar()
        widget = QWidget()
        layout = QVBoxLayout()

        label_title = QLabel("终端")
        layout_console = QHBoxLayout()
        layout_console.addWidget(label_title)
        layout_console.addWidget(self.line_by_line_text_edit)

        settings_menu = menu_bar.addMenu("设置")
        help_menu = menu_bar.addMenu("帮助")
        sponsor_menu = menu_bar.addMenu("赞助")

        # 创建调试菜单项
        debug_settings_action = QAction("调试", self)
        debug_settings_action.triggered.connect(self.open_debug_settings_dialog)
        settings_menu.addAction(debug_settings_action)

        # # 创建设置参数菜单项
        # set_parameters_action = QAction("设置1", self)
        # # set_parameters_action.triggered.connect(self.open_parameter_settings_dialog)
        # settings_menu.addAction(set_parameters_action)
        #
        # # 创建更改主题菜单项
        # change_theme_action = QAction("设置2", self)
        # # change_theme_action.triggered.connect(self.change_theme)
        # settings_menu.addAction(change_theme_action)

        # 创建显示帮助文档菜单项
        show_help_action = QAction("显示帮助文档", self)
        # show_help_action.triggered.connect(self.show_help_document)
        help_menu.addAction(show_help_action)

        # 创建关于菜单项
        about_action = QAction("关于", self)
        # about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        left_form_layout = QFormLayout()
        left_form_layout.setLabelAlignment(Qt.AlignRight)

        self.cps_p = CustomParamSlider('P', scale=True, length=35)
        self.cps_d = CustomParamSlider('D', scale=True, length=35)
        self.cps_i = CustomParamSlider('I', scale=True, length=35)
        self.cps_reaction = CustomParamSlider("反应(*10ms)", slider_domain=(1, 30), interval=3)
        self.cps_x = CustomParamSlider("宽", slider_domain=(32, 320), length=35, interval=32)
        self.cps_y = CustomParamSlider("高", slider_domain=(32, 320), length=35, interval=32)
        self.cps_p.set_value(self.main_loop.assistant.P)
        self.cps_i.set_value(self.main_loop.assistant.I)
        self.cps_reaction.set_value(self.main_loop.assistant.REACTION_TICK)
        self.cps_x.set_value(self.main_loop.assistant.LOCK_RANGE[0])
        self.cps_y.set_value(self.main_loop.assistant.LOCK_RANGE[1])
        self.cps_p.slider.valueChanged.connect(self.update_assistant)
        self.cps_d.slider.valueChanged.connect(self.update_assistant)
        self.cps_i.slider.valueChanged.connect(self.update_assistant)
        self.cps_reaction.slider.valueChanged.connect(self.update_assistant)
        self.cps_x.slider.valueChanged.connect(self.update_assistant)
        self.cps_y.slider.valueChanged.connect(self.update_assistant)
        left_form_layout.addRow(self.cps_p)
        left_form_layout.addRow(self.cps_d)
        left_form_layout.addRow(self.cps_i)
        left_form_layout.addRow(self.cps_reaction)

        size_layout = QVBoxLayout()
        size_xy_layout = QFormLayout()
        size_xy_layout.addRow(self.cps_x)
        size_xy_layout.addRow(self.cps_y)
        size_label = QLabel("推理尺寸:")
        size_layout.addWidget(size_label, 1)
        size_layout.addLayout(size_xy_layout, 3)
        left_form_layout.addRow(size_layout)

        layout_sliders = QVBoxLayout()  # 创建垂直布局，用于包含所有滑动条
        layout_sliders.addLayout(left_form_layout)

        layout_dropdown = QVBoxLayout()  # 创建垂直布局，用于包含下拉菜单
        right_form_layout = QFormLayout()
        right_form_layout.setLabelAlignment(Qt.AlignRight)

        self.combo_model = QComboBox()
        self.combo_model.addItem("CS-small")
        self.combo_model.addItem("CS-nano")
        self.combo_model.addItem("CS-medium")
        self.combo_model.addItem("PUBG")
        self.combo_model.activated[str].connect(self.handle_model_selection)
        label_model = QLabel("推理模型:")
        right_form_layout.addWidget(label_model)
        right_form_layout.addWidget(self.combo_model)
        right_form_layout.addRow(label_model, self.combo_model)

        self.combo_mouse = QComboBox()
        self.combo_mouse.addItem("原始移动")
        self.combo_mouse.addItem("平滑过渡移动")
        self.combo_mouse.activated[str].connect(self.handle_mouse_selection)
        label_mouse = QLabel("移动方案:")
        right_form_layout.addWidget(label_mouse)
        right_form_layout.addWidget(self.combo_mouse)
        right_form_layout.addRow(label_mouse, self.combo_mouse)

        self.combo_weapon = QComboBox()
        self.combo_weapon.addItem("ak47")
        self.combo_weapon.addItem("m4a1")
        self.combo_weapon.addItem("negev")
        self.combo_weapon.addItem("...")
        self.combo_weapon.activated[str].connect(self.handle_weapon_selection)
        label_weapon = QLabel("选择主武器:")
        right_form_layout.addWidget(label_weapon)
        right_form_layout.addWidget(self.combo_weapon)
        right_form_layout.addRow(label_weapon, self.combo_weapon)

        self.combo_alt_weapon = QComboBox()
        self.combo_alt_weapon.addItem("usp")
        self.combo_alt_weapon.addItem("glock")
        self.combo_alt_weapon.addItem("Deagle")
        self.combo_alt_weapon.addItem("...")
        self.combo_alt_weapon.activated[str].connect(self.handle_alt_weapon_selection)
        label_alt_weapon = QLabel("选择副武器:")
        right_form_layout.addWidget(label_alt_weapon)
        right_form_layout.addWidget(self.combo_alt_weapon)
        right_form_layout.addRow(label_alt_weapon, self.combo_alt_weapon)

        layout_dropdown.addLayout(right_form_layout)

        layout_bottom = QHBoxLayout()  # 创建水平布局，用于包含开始预测按钮
        self.btn = QPushButton('退出')  # 创建一个按钮
        self.btn.clicked.connect(self.quit_button)  # 设置按钮点击时候的槽函数, 即点击按钮会调用函数 onClickButto
        self.btn.setFixedWidth(100)  # 设置按钮宽度

        self.start_predict_button = QPushButton("启动程序")
        self.start_predict_button.clicked.connect(self.toggle_prediction)
        self.start_predict_button.setFixedWidth(200)  # 设置按钮宽度

        self.expand_button = QPushButton("▼实时监测▼")
        self.expand_button.clicked.connect(self.toggle_image_section)
        self.expand_button.setFixedWidth(100)
        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 300)
        self.image_label.hide()  # 隐藏图片部分

        self.table_widget = CustomTableWidget()
        # new_item = QTableWidgetItem("新值")
        # self.table_widget.setItem(1, 2, new_item)

        layout_bottom.addStretch(1)  # 添加一个空的弹簧
        layout_bottom.addWidget(self.btn)
        layout_bottom.addWidget(self.start_predict_button)  # 将按钮添加到布局中
        layout_bottom.addWidget(self.expand_button)
        layout_bottom.addStretch(1)  # 添加一个空的弹簧

        # 创建分割线
        h_line_1 = QFrame()
        h_line_1.setFrameShape(QFrame.HLine)  # 设置分割线为水平方向
        h_line_1.setFrameShadow(QFrame.Sunken)  # 设置分割线样式

        h_line_2 = QFrame()
        h_line_2.setFrameShape(QFrame.HLine)  # 设置分割线为水平方向
        h_line_2.setFrameShadow(QFrame.Sunken)  # 设置分割线样式

        v_line_1 = QFrame()
        v_line_1.setFrameShape(QFrame.VLine)  # 设置分割线为竖直方向
        v_line_1.setFrameShadow(QFrame.Sunken)  # 设置分割线样式

        v_line_2 = QFrame()
        v_line_2.setFrameShape(QFrame.VLine)  # 设置分割线为竖直方向
        v_line_2.setFrameShadow(QFrame.Sunken)  # 设置分割线样式

        layout_main = QVBoxLayout()  # 创建垂直布局，用于包含主要内容

        layout_mid = QHBoxLayout()  # 创建水平布局，用于包含滑动条布局和下拉菜单布局
        layout_mid.addLayout(layout_sliders, 3)
        layout_mid.addWidget(v_line_1)  # 添加分割线
        layout_mid.addLayout(layout_dropdown, 1)
        layout_mid.addWidget(v_line_2)  # 添加分割线
        layout_mid.addWidget(self.table_widget, 3)  # 添加 QTableWidget 到布局中

        # 将分割线添加到布局中
        layout_main.addLayout(layout_console, 2)
        layout_main.addWidget(h_line_1)
        layout_main.addLayout(layout_mid, 2)
        layout_main.addLayout(layout_bottom, 1)  # 将布局添加到主布局中
        layout.addLayout(layout_main, 1)
        layout.addWidget(h_line_2)
        layout.addWidget(self.image_label)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_debug_settings_dialog(self):
        self.debug_settings_window = DebugSettingsWindow(self)
        self.debug_settings_window.show()

    def toggle_image_section(self):
        if self.image_label.isHidden():
            self.expand_button.setText("▲实时监测▲")  # 更改按钮文本为▲
            self.main_loop.detector.IMG_VIEW = True
            self.image_label.show()  # 显示图片部分
        else:
            self.expand_button.setText("▼实时监测▼")  # 更改按钮文本为▼
            self.image_label.hide()  # 隐藏图片部分
            self.main_loop.detector.IMG_VIEW = False
            self.resize(self.width(), self.height() - self.image_label.height())  # 减小窗口高度

    def update_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)

    def show_slider_value(self):
        # 显示滑动条的值
        p_value = self.slider_p.value()
        d_value = self.slider_d.value()
        i_value = self.slider_i.value()
        reaction_time_value = self.slider_reaction_time.value()
        lock_range_value = self.slider_lock_range.value()

        print("P参数:", p_value)
        print("D参数:", d_value)
        print("I参数:", i_value)
        print("反应时间:", reaction_time_value)
        print("锁定范围:", lock_range_value)

    def update_assistant(self):
        p_value = self.cps_p.param.get_value()
        d_value = self.cps_d.param.get_value()
        i_value = self.cps_i.param.get_value()
        reaction_time_value = int(self.cps_reaction.param.get_value())
        lock_range = self.cps_x.param.get_value(), self.cps_y.param.get_value()
        self.main_loop.assistant.P = p_value
        self.main_loop.assistant.D = d_value
        self.main_loop.assistant.I = i_value
        self.main_loop.assistant.REACTION_TICK = reaction_time_value
        self.main_loop.assistant.LOCK_RANGE = lock_range
        self.main_loop.assistant.reset_reaction()
        self.add_line_in_console('Parameters updated', '已更新参数')

    def update_setting_tabel(self):
        item = QTableWidgetItem(self.main_loop.assistant.weapon_mode)
        self.table_widget.setItem(0, 2, item)
        item = QTableWidgetItem(self.main_loop.assistant.shooting_mode)
        self.table_widget.setItem(1, 2, item)
        aim_assist = (self.main_loop.assistant.aim_assist or self.main_loop.assistant.alt_aim_assist or self.main_loop.assistant.fix_aim_assist)
        item = QTableWidgetItem('Y' if aim_assist else 'N')
        self.table_widget.setItem(2, 2, item)
        auto_shoot = (self.main_loop.assistant.auto_shoot or self.main_loop.assistant.fix_auto_shoot)
        item = QTableWidgetItem('Y' if auto_shoot else 'N')
        self.table_widget.setItem(3, 2, item)
        item = QTableWidgetItem('Y' if self.main_loop.assistant.auto_stop else 'N')
        self.table_widget.setItem(4, 2, item)
        self.table_widget.viewport().repaint()
        self.add_line_in_console('Update Settings', '设置已更新')

    def handle_model_selection(self, model_name):
        if model_name == "CS-small":
            self.main_loop.reset_model('cs2_s_fp16.engine')
        elif model_name == "CS-nano":
            self.main_loop.reset_model('cs2_n_fp16.engine')
        elif model_name == "CS-medium":
            self.main_loop.reset_model('cs2_m_fp16.engine')
        elif model_name == "模型4":
            self.add_line_in_console()

    def handle_mouse_selection(self, mouse_name):
        if mouse_name == "平滑过渡移动":
            self.main_loop.assistant.SMOOTH_TRANSITION_MOVE = True
        elif mouse_name == "原始移动":
            self.main_loop.assistant.SMOOTH_TRANSITION_MOVE = False
        elif mouse_name == "鼠标3":
            self.add_line_in_console()
        elif mouse_name == "鼠标4":
            self.add_line_in_console()

    def handle_weapon_selection(self, weapon):
        if weapon == "...":
            self.add_line_in_console('Weapon sold out', '武器售光')
        else:
            self.add_line_in_console(f'Switch to {weapon}', '切换武器')
            self.main_loop.assistant.WEAPON = weapon

    def handle_alt_weapon_selection(self, weapon):
        if weapon == "...":
            self.add_line_in_console('Weapon sold out', '武器售光')
        else:
            self.add_line_in_console(f'Switch to {weapon}', '切换武器')
            self.main_loop.assistant.ALT_WEAPON = weapon

    def add_line_in_console(self, eng='The program is still in progress', ch='功能暂不开放'):
        self.line_by_line_text_edit.appendPlainText(eng)
        self.line_by_line_text_edit.appendPlainText(ch)
        scrollbar = self.line_by_line_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def toggle_prediction(self):
        if self.is_predicting:
            self.add_line_in_console('', '')
            self.add_line_in_console('STOPPED', '已停止')
            self.add_line_in_console('', '')
            self.stop_prediction()
        else:
            self.add_line_in_console('', '')
            self.add_line_in_console('Move it,move it!', '行动，行动')
            self.add_line_in_console('', '')
            self.start_prediction()

    def start_prediction(self):
        # 开始预测的逻辑
        self.is_predicting = True
        self.start_predict_button.setText("停止捕捉")
        if self.main_loop.run:
            self.main_loop.unpause()
        else:
            self.main_loop.start()

    def stop_prediction(self):
        # 停止预测的逻辑
        self.is_predicting = False
        self.start_predict_button.setText("重新开始捕捉")

        self.main_loop.pause()

    def quit_button(self):
        self.close()
        self.main_loop.end()
        sys.exit(app.exec())
        sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
