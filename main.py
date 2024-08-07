import sys
from PyQt5.QtWidgets import QApplication
from cs_master.gui import LoginWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
