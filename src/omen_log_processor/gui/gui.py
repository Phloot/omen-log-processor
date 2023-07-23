from PyQt5.QtWidgets import QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QFormLayout, QSizePolicy, QGridLayout
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QIcon

from omen_log_processor.gui.worker import Worker


import json
import pika
import os
import re

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set the window title and icon
        self.setWindowTitle('Omen Bot WvW Log Processor')
        current_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(current_dir, '..', 'assets', 'icon.png')
        self.setWindowIcon(QIcon(icon_path))

        # Set the initial window size and disable resizing
        self.setGeometry(100, 100, 800, 400)
        self.setFixedSize(800, 400)

        # Console
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)

        # Connection details
        self.credentials_group = QGroupBox("MQ Credentials")

        # Arrange the host and port fields
        self.host_field = QLineEdit()
        self.port_field = QLineEdit()

        # Set the sizes for host and port fields
        self.host_field.setMinimumWidth(90)  # Adjust this value as necessary
        self.port_field.setMaximumWidth(45)  # Adjust this value as necessary

        self.host_layout = QHBoxLayout()
        self.host_layout.addWidget(QLabel("Host"))
        self.host_layout.addWidget(self.host_field, 2) # Give host field double space of port field
        self.host_layout.addWidget(QLabel("Port"))
        self.host_layout.addWidget(self.port_field, 1)

        self.username_label = QLabel("Username:")
        self.username_entry = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.verify_connection)

        # Arrange the MQ fields vertically
        self.credentials_layout = QVBoxLayout()
        self.credentials_layout.addWidget(self.username_label)
        self.credentials_layout.addWidget(self.username_entry)
        self.credentials_layout.addWidget(self.password_label)
        self.credentials_layout.addWidget(self.password_entry)
        self.credentials_layout.addLayout(self.host_layout)
        self.credentials_layout.addWidget(self.connect_button)
        self.credentials_group.setLayout(self.credentials_layout)

        # Connection status
        self.connections_group = QGroupBox("Connections")
        self.connection_status_label = QLabel("MQ Connection: <span style='color:black'>Not Connected</span>")
        self.connections_layout = QVBoxLayout()
        self.connections_layout.addWidget(self.connection_status_label)
        self.connections_group.setLayout(self.connections_layout)

        # Stats
        self.stats_group = QGroupBox("File Stats")

        # Create a label for each counter and the counter itself
        self.files_uploaded_label = QLabel("Files Uploaded: ")
        self.files_uploaded_counter = QLabel("0")
        self.files_processed_label = QLabel("Files Processed: ")
        self.files_processed_counter = QLabel("0")
        self.files_failed_label = QLabel("Files Failed: ")
        self.files_failed_counter = QLabel("0")

        # Arrange the labels and counters in a grid layout
        self.stats_layout = QGridLayout()
        self.stats_layout.addWidget(self.files_uploaded_label, 0, 0)
        self.stats_layout.addWidget(self.files_uploaded_counter, 0, 1)
        self.stats_layout.addWidget(self.files_processed_label, 1, 0)
        self.stats_layout.addWidget(self.files_processed_counter, 1, 1)
        self.stats_layout.addWidget(self.files_failed_label, 2, 0)
        self.stats_layout.addWidget(self.files_failed_counter, 2, 1)
        self.stats_group.setLayout(self.stats_layout)

        # Clear and Exit buttons
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        # Arrange buttons horizontally
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.clear_button)
        self.buttons_layout.addWidget(self.exit_button)

        # Arrange the MQ fields, connections, stats, and buttons vertically
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.credentials_group)
        self.right_layout.addWidget(self.connections_group)
        self.right_layout.addWidget(self.stats_group)
        self.right_layout.addLayout(self.buttons_layout)

        # Arrange the console and the right layout horizontally
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.console, 3)  # 75% of the space
        self.layout.addLayout(self.right_layout, 1)  # 25% of the space
        self.setLayout(self.layout)

        # Drag and Drop files
        self.setAcceptDrops(True)

        # Initialize file counters
        self.files_uploaded = 0
        self.files_processed = 0
        self.files_failed = 0

        # Thread collector
        self.threads = []

    def clear(self):
        self.console.clear()
        self.files_uploaded = 0
        self.files_processed = 0
        self.files_failed = 0
        self.files_uploaded_label.setText("Files Uploaded: ")
        self.files_processed_label.setText("Files Processed: ")
        self.files_failed_label.setText("Files Failed: ")
        self.files_uploaded_counter.setText(str(self.files_uploaded))
        self.files_processed_counter.setText(str(self.files_processed))
        self.files_failed_counter.setText(str(self.files_failed))
        self.connection_status_label.setText("MQ Connection: <span style='color:black'>Not Connected</span>")

    def verify_connection(self):
        host = self.host_field.text()
        port = self.port_field.text()

        if not self.validate_ip_port(host, port):
            self.add_to_console("Invalid IP address or port. Please try again.")
            return

        try:
            # Connection code will go here
            pass
        except Exception as e:
            self.add_to_console(f"Failed to connect: {str(e)}")
            self.connection_status_label.setText("MQ Connection: <font color='red'>Failed</font>")
        else:
            self.connection_status_label.setText("MQ Connection: <font color='green'>Connected</font>")

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            file_path = url.toLocalFile()
            self.files_uploaded += 1
            self.files_uploaded_counter.setText(str(self.files_uploaded))

            worker = Worker(file_path)
            worker.loaded.connect(self.on_file_loaded)
            worker.failed.connect(self.on_file_failed)
            worker.finished.connect(self.thread_finished)
            self.threads.append(worker)
            worker.start()

    def on_file_loaded(self, file_name):
        self.add_to_console(f"Loaded file {file_name}")
        self.files_processed += 1
        self.files_processed_counter.setText(str(self.files_processed))

    def on_file_failed(self, file_name, e):
        self.add_to_console(f"Failed to load file {file_name}: {str(e)}")
        self.files_failed += 1
        self.files_failed_counter.setText(str(self.files_failed))

    def thread_finished(self):
        for thread in self.threads:
            if not thread.isRunning():
                self.threads.remove(thread)

    def load_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.add_to_console(f"Loaded file {os.path.basename(file_path)}")
                self.files_processed += 1
                self.files_processed_label.setText(f"Files Processed: {self.files_processed}")
        except Exception as e:
            self.add_to_console(f"Failed to load file {os.path.basename(file_path)}: {e}")
            self.files_failed += 1
            self.files_failed_label.setText(f"Files Failed: {self.files_failed}")

    def validate_ip_port(self, ip, port):
        # Checking if IP is in valid format
        ip_pattern = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}$")
        if not ip_pattern.fullmatch(ip):
            return False

        # Check each segment of the IP address to make sure it's between 0 and 255
        ip_segments = ip.split('.')
        for segment in ip_segments:
            if not 0 <= int(segment) <= 255:
                return False

        # Checking if Port is in valid range
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                return False
        except ValueError:
            return False

        return True

    def add_to_console(self, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.console.append(f"[{timestamp}] {message}")