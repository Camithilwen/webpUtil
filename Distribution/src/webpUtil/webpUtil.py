from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QWidget
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtGui import QGuiApplication, QMovie
from PyQt5.QtCore import Qt
from WEBPconvert import *
import sys
import os
import platform
import subprocess

# Interface
interface = WEBPconvert()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window configuration
        self.setWindowTitle("WEBP to PNG Converter")
        self.setGeometry(100, 100, 800, 500)  # Taller window
        self.setMinimumSize(800, 500)

        # High-DPI scaling
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.mainLayout = QVBoxLayout(central_widget)

        # Filepath display with "Open in Folder" button
        self.filepathLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.filepathLayout)

        self.fileDisplay = QLineEdit(self)
        self.fileDisplay.setPlaceholderText("Output file path")
        self.fileDisplay.setReadOnly(True)
        self.fileDisplay.setFixedHeight(30)
        self.filepathLayout.addWidget(self.fileDisplay)

        self.openFolderButton = QPushButton("Open in Folder", self)
        self.openFolderButton.setFixedSize(150, 30)
        self.openFolderButton.setEnabled(False)  # Initially disabled
        self.openFolderButton.clicked.connect(self.openInFolderCommand)
        self.filepathLayout.addWidget(self.openFolderButton)

        # Images layout (side by side)
        self.imageLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.imageLayout)

        self.beforeImageLabel = QLabel("Before Image", self)
        self.beforeImageLabel.setFixedSize(350, 350)
        self.beforeImageLabel.setStyleSheet("border: 1px solid black;")
        self.beforeImageLabel.setAlignment(Qt.AlignCenter)
        self.imageLayout.addWidget(self.beforeImageLabel)

        self.afterImageLabel = QLabel("After Image", self)
        self.afterImageLabel.setFixedSize(350, 350)
        self.afterImageLabel.setStyleSheet("border: 1px solid black;")
        self.afterImageLabel.setAlignment(Qt.AlignCenter)
        self.imageLayout.addWidget(self.afterImageLabel)

        # Buttons layout (side by side)
        self.buttonLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.buttonLayout)

        self.openButton = QPushButton("Open", self)
        self.openButton.clicked.connect(self.openCommand)
        self.buttonLayout.addWidget(self.openButton)

        self.convertButton = QPushButton("Convert", self)
        self.convertButton.clicked.connect(self.convertCommand)
        self.buttonLayout.addWidget(self.convertButton)

        self.closeButton = QPushButton("Close", self)
        self.closeButton.clicked.connect(self.close)
        self.buttonLayout.addWidget(self.closeButton)

        # Ensure buttons are evenly sized
        for button in [self.openButton, self.convertButton, self.closeButton]:
            button.setFixedSize(150, 40)

    def openCommand(self):
        """Generates a file dialog and passes selection to the conversion module."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "WEBP files (*.webp);;All Files (*)", options=options)
        if file_path:
            self.filepath = file_path
            status = interface.fileOpen(file_path)
            if status == "OK":
                self.displayImage(file_path, self.beforeImageLabel)
            else:
                QMessageBox.information(self, "Error", status)

    def convertCommand(self):
        """Calls the conversion method and generates a save dialog on completion.
        Upon conversion, the converted image is displayed and the new file path made available for the user to open."""
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*)", options=options)
        if save_path:
            returnedPath = interface.fileConvert(save_path)
            self.displayImage(returnedPath, self.afterImageLabel)
            self.savedPath = returnedPath  # Store the saved file path
            self.fileDisplay.setText(returnedPath)  # Updates the filepath display
            self.openFolderButton.setEnabled(True)  # Enable "Open in Folder" button

    def displayImage(self, path, labelWidget):
        """Loads and displays images or animations in their respective label widgets."""
        if path.lower().endswith((".webp", ".gif")):  # Check for animated formats
            movie = QMovie(path)
            movie.setScaledSize(labelWidget.size())  # Scale animation to fit label
            labelWidget.setMovie(movie)
            movie.start()
        else:
            pixmap = QPixmap(path)
            pixmap = pixmap.scaled(labelWidget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            labelWidget.setPixmap(pixmap)

    def openInFolderCommand(self):
        """Opens the saved image location in the system file browser."""
        if hasattr(self, 'savedPath') and os.path.exists(self.savedPath):
            folder_path = os.path.dirname(self.savedPath)
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", folder_path])
            else:  # Linux and other Unix-like systems
                subprocess.call(["xdg-open", folder_path])

    def get_scaled_font_size(self, base_size):
        """Returns a scaled font size based on the device pixel ratio."""
        screen = QGuiApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()  # Get the logical DPI of the screen
        scale_factor = dpi / 96.0  # Assume standard DPI is 96
        return int(base_size * scale_factor)  # Scale the base font size


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # Set a global font with dynamic scaling
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    scale_factor = dpi / 96.0
    font = QFont("Arial", int(12 * scale_factor))  # Adjust base font size dynamically
    app.setFont(font)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
