#!/usr/bin/env python3

import sys
from PySide6 import QtCore, QtWidgets, QtGui

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exam Shuffler")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.resize(400, 100)
    window.show()
    sys.exit(app.exec())
