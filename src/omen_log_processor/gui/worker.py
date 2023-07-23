from PyQt5.QtCore import QThread, pyqtSignal

import json
import os

class Worker(QThread):
    loaded = pyqtSignal(str)
    failed = pyqtSignal(str, Exception)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.loaded.emit(os.path.basename(self.file_path))
        except Exception as e:
            self.failed.emit(os.path.basename(self.file_path), e)