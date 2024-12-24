import os
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal

class ExportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, input_folder, output_folder):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder

    def run(self):
        subfolders = [d for d in os.listdir(self.input_folder) if os.path.isdir(os.path.join(self.input_folder, d))]
        total = len(subfolders)

        for i, subfolder in enumerate(subfolders):
            song_folder = os.path.join(self.input_folder, subfolder)
            output_file = os.path.join(self.output_folder, f"{subfolder}.osz")
            self.create_osz(song_folder, output_file)
            self.progress.emit(int((i + 1) / total * 100))

        self.finished.emit()

    def create_osz(self, folder_path, output_path):
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as osz_file:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    osz_file.write(file_path, arcname)


class OszExporterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QIcon("extractor.ico"))

        self.setWindowTitle("osu! .osz Extractor")
        self.setGeometry(300, 200, 600, 230)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        input_layout = QHBoxLayout()
        self.input_label = QLabel("Songs Folder:")
        self.input_path = QLineEdit()
        self.browse_input_button = QPushButton("Browse")
        self.browse_input_button.clicked.connect(self.browse_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.browse_input_button)

        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output Folder:")
        self.output_path = QLineEdit()
        self.browse_output_button = QPushButton("Browse")
        self.browse_output_button.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.browse_output_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.export_button = QPushButton("Export All Songs to .osz")
        self.export_button.clicked.connect(self.export_all_to_osz)
        self.export_button.setStyleSheet("padding: 10px; font-size: 16px;")

        copyright_label = QLabel("© 2024 ledinhchinh (Yukiookii). All rights reserved.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 12px; color: #666666; margin-top: 10px;")
        
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.export_button)

        layout.addWidget(copyright_label)

        self.setLayout(layout)
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                border: 1px solid #ccc;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                text-align: center;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)

    def browse_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Songs Folder")
        if folder:
            self.input_path.setText(folder)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path.setText(folder)

    def export_all_to_osz(self):
        input_folder = self.input_path.text()
        output_folder = self.output_path.text()

        if not input_folder or not output_folder:
            QMessageBox.warning(self, "Error", "Please specify both input and output paths.")
            return

        if not os.path.exists(input_folder):
            QMessageBox.warning(self, "Error", "The input folder does not exist.")
            return

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.worker = ExportWorker(input_folder, output_folder)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_export_finished)

        self.export_button.setEnabled(False)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_export_finished(self):
        QMessageBox.information(self, "Success", "All songs have been exported successfully!")
        self.progress_bar.setValue(0)
        self.export_button.setEnabled(True)


if __name__ == "__main__":
    from PyQt5.QtCore import Qt
    app = QApplication([])
    window = OszExporterApp()
    window.show()
    app.exec_()