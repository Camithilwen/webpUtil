from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QSplashScreen
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtGui import QGuiApplication, QMovie, QCursor
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

        # Apply sunflower yellow theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFDA03;  /* Sunflower yellow background */
            }
            QPushButton {
                background-color: #FFC107;  /* Yellow button color */
                border: 2px solid #FF9800;  /* Slightly darker border */
                border-radius: 5px;
                font-size: 14px;
                color: black;
            }
            QPushButton:hover {
                background-color: #FFB300;  /* Darker yellow on hover */
            }
            QLineEdit, QLabel {
                background-color: white;
                border: 2px solid #FF9800;  /* Slightly darker border for fields */
                border-radius: 5px;
                padding: 5px;
            }
        """)

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
        self.beforeImageLabel.setStyleSheet("border: 2px solid #FF9800;")
        self.beforeImageLabel.setAlignment(Qt.AlignCenter)
        self.imageLayout.addWidget(self.beforeImageLabel)

        self.afterImageLabel = QLabel("After Image", self)
        self.afterImageLabel.setFixedSize(350, 350)
        self.afterImageLabel.setStyleSheet("border: 2px solid #FF9800;")
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

        # Add the secret button
        self.secretButton = QPushButton("what's this?", self)
        self.secretButton.setFixedSize(120, 30)
        self.secretButton.setStyleSheet("background-color: transparent; border: none; color: transparent;")
        self.secretButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.secretButton.setToolTip("")
        self.secretButton.move(self.width() // 2 - 75, self.height() // 2 - 20)
        self.secretButton.clicked.connect(self.showSecretMessage)
        self.secretButton.installEventFilter(self)

    def eventFilter(self, source, event):
        """Make the secret button visible on hover."""
        if source == self.secretButton and event.type() == event.Enter:
            self.secretButton.setStyleSheet("background-color: #FFC107; color: black;")
        elif source == self.secretButton and event.type() == event.Leave:
            self.secretButton.setStyleSheet("background-color: transparent; border: none; color: transparent;")
        return super().eventFilter(source, event)

    def showSecretMessage(self):
        """Show a playful message when the secret button is clicked."""
        QMessageBox.information(self, "easter egg", "made you look ;3 hi court!")

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
        try:
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*)", options=options)
            if save_path:
                print(f"Save path: {save_path}")  # Debug log
                returnedPath = interface.fileConvert(save_path)
                print(f"Converted file path: {returnedPath}")  # Debug log
                # Verify output file exists
                if os.path.exists(returnedPath):
                    self.displayImage(returnedPath, self.afterImageLabel)
                    self.savedPath = returnedPath# Store actual file path
                    self.fileDisplay.setText(returnedPath)  # Update display
                    self.openFolderButton.setEnabled(True)
                else:
                    print(f"Output file not found at {returnedPath}")
                    QMessageBox.warning(self, "Error", "File conversion failed.")
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Conversion failed: {ex}")
            print(f"Error during conversion: {ex}")

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

     # Dynamically locate the splash image
    base_path = getattr(sys, '_MEIPASS', os.getcwd())  # Use sys._MEIPASS for bundled executable
    splash_image_path = os.path.join(base_path, "608ddf37f31bc3671f018ca37f1e8e5a-3479531950.jpg")

    # Set up and display a splash screen
    splash_pix = QPixmap(splash_image_path)
    splash = QSplashScreen(splash_pix)
    splash.show()
    app.processEvents()  # Allow the splash screen to show while loading

    # Set a global font with dynamic scaling
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    scale_factor = dpi / 96.0
    font = QFont("Arial", int(12 * scale_factor))  # Adjust base font size dynamically
    app.setFont(font)

    main_window = MainWindow()
    main_window.show()

     # Close the splash screen
    splash.finish(main_window)

    sys.exit(app.exec_())
