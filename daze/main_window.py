'''
Main window initialization
'''
import sys
import qdarkstyle

from .about_menu import AboutMenu
from .utils import daze_state
from .errors import DazeStateException
from .playlist_tab import PlaylistTab

from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QAction,
                             qApp,
                             QDesktopWidget)


class MainWindow(QMainWindow):
    def __init__(self, app):
        '''
        Main window set up
        @param app: QApplication instance
        '''
        super().__init__()
        self.app = app

        self.menu_setup()

        try:
            self.daze_data = daze_state.load_state()
            self.load_daze()
        except DazeStateException:
            self.daze_data = {}
            self.set_defaults()

        self.initUI()

    def load_daze(self):
        '''
        load daze data
        '''
        if self.daze_data.get('Preferences')['mode'] == 'night':
            self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            self.theme_action.setChecked(True)
        else:
            self.app.setStyleSheet('')
            self.theme_action.setChecked(False)

    def set_defaults(self):
        '''
        set daze data
        '''
        self.daze_data.setdefault('Preferences', {}).setdefault('mode', 'night')
        self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def menu_setup(self):
        '''
        Setup menu
        '''
        # menu
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        file_menu = menu_bar.addMenu('File')
        settings_menu = menu_bar.addMenu('Settings')

        self.about_dialog = AboutMenu()
        about_action = QAction('About Daze', self)
        about_action.setShortcut('Ctrl+A')
        about_action.triggered.connect(self.about_dialog.exec)

        self.theme_action = QAction('Midnight Mode', self, checkable=True)
        self.theme_action.setShortcut('Ctrl+M')
        self.theme_action.triggered.connect(self.toggle_theme)

        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.quit_application)

        file_menu.addAction(about_action)
        file_menu.addAction(quit_action)
        settings_menu.addAction(self.theme_action)

    def initUI(self):
        '''
        Initialize the main window
        '''
        self.setWindowTitle("Daze")
        self.setGeometry(100, 100, 550, 300)

        # center window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # tabs
        playlist_widget = PlaylistTab(self.daze_data)
        self.setCentralWidget(playlist_widget)

    def toggle_theme(self, state):
        '''
        Toggle theme
        @param state: True if checkbox is checked, False otherwise
        '''
        if state:
            self.daze_data.get('Preferences')['mode'] = 'night'
            self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            self.theme_action.setChecked(True)
        else:
            self.daze_data.get('Preferences')['mode'] = 'day'
            self.app.setStyleSheet('')
            self.theme_action.setChecked(False)

        daze_state.save_state(self.daze_data)

    def quit_application(self):
        '''
        Exit the application
        '''
        qApp.quit()


def main(args):
    app = QApplication(args)
    main_window = MainWindow(app)
    main_window.show()
    sys.exit(app.exec())

