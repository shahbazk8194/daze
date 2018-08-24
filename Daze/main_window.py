import sys
import qdarkstyle
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, qApp


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        file_menu = menu_bar.addMenu('File')

        about_action = QAction('About Daze', self)
        about_action.setShortcut('Ctrl+A')

        settings_action = QAction('Settings', self)
        settings_action.setShortcut('Ctrl+S')

        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.quit_application)

        file_menu.addAction(about_action)
        file_menu.addAction(settings_action)
        file_menu.addAction(quit_action)

        self.setWindowTitle("Daze")
        self.setGeometry(100, 100, 640, 400)
        self.statusBar()

    def quit_application(self):
        qApp.quit()


def main(args):
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # app.setStyleSheet('') default style sheet
    main_window.show()
    sys.exit(app.exec())

