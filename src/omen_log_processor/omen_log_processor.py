#from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QFormLayout, QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QColor
import sys
import json
import pika
import os
import re

from omen_log_processor.gui.gui import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
