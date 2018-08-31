'''
Reponsible for playlist tab creation
'''
import os

from .utils.youtube_dl import YoutubeDLUtility
from .utils import daze_state
from .errors import DazeStateException
from PyQt5.QtWidgets import (QWidget,
                             QListView,
                             QHBoxLayout,
                             QVBoxLayout,
                             QShortcut,
                             QApplication,
                             QPushButton,
                             QFileDialog,
                             QTextEdit)
from PyQt5.QtGui import (QStandardItem,
                         QStandardItemModel,
                         QIcon,
                         QKeySequence)
from PyQt5.QtCore import (pyqtSignal,
                          QModelIndex,
                          QVariant,
                          Qt)


class QNonStandardItemModel(QStandardItemModel):
    itemBeforeAndAfterChanged = pyqtSignal(QModelIndex,
                                           int,
                                           QVariant,
                                           QVariant)

    def setData(self,
                index_qmodel_index,
                after_value,
                role=Qt.EditRole):

        before_value = self.data(index_qmodel_index, role)
        self.itemBeforeAndAfterChanged.emit(index_qmodel_index,
                                            role,
                                            before_value,
                                            after_value)
        return QStandardItemModel.setData(self,
                                          index_qmodel_index,
                                          after_value,
                                          role)


class PlaylistTab(QWidget):
    def __init__(self, daze_data):
        '''
        Playlist Initialization
        @data: dictionary of daze related data
        '''
        super().__init__()

        self.playlist = QListView(self)
        self.playlist_item = QNonStandardItemModel()
        self.playlist.setModel(self.playlist_item)

        self.directory_path = os.path.expanduser('~/Downloads')
        self.file_dialog = QFileDialog()

        self.directory_path_text = QTextEdit(self)
        self.directory_path_text.setReadOnly(True)
        self.directory_path_text.setMaximumHeight(28)

        self.choose_directory = QPushButton("Choose Folder", self)

        try:
            self.daze_data = daze_state.load_state()
            self.load_daze()
        except DazeStateException:
            self.daze_data = daze_data
            self.load_defaults()

        self.initUI()

    def load_daze(self):
        for name, metadata in self.daze_data.setdefault('Playlist', {}).items():
            item = QStandardItem(name)
            self.playlist_item.appendRow(item)

        self.directory_path_text.setText((self.daze_data.setdefault('Preferences')
                                                        .setdefault('directory_path',
                                                                    self.directory_path)))

    def load_defaults(self):
        for name, metadata in self.daze_data.setdefault('Playlist', {}).items():
            item = QStandardItem(name)
            self.playlist_item.appendRow(item)

        # load empty playlist
        self.daze_data.setdefault('Playlist', {})

        # load default directory path
        self.daze_data.setdefault('Preferences', {}).setdefault('directory_path',
                                                                self.directory_path)
        self.directory_path_text.setText((self.daze_data.setdefault('Preferences')
                                                        .setdefault('directory_path',
                                                                    self.directory_path)))
        daze_state.save_state(self.daze_data)

    def initUI(self):
        # wire up signals
        QShortcut(QKeySequence('Ctrl+v'), self).activated.connect(self.handle_paste)
        QShortcut(QKeySequence('Ctrl+r'), self).activated.connect(self.handle_remove)
        self.playlist.clicked.connect(self.item_clicked)
        self.playlist_item.itemBeforeAndAfterChanged.connect(self.callback)
        self.choose_directory.clicked.connect(self.open_folder)

        # get playlist icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'daze_icon.png')
        self.icon = QIcon(icon_path)

        # set layouts
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.playlist)
        self.hbox.addWidget(self.choose_directory)
        self.hbox.addWidget(self.directory_path_text)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)

    def open_folder(self):
        self.directory_path = self.file_dialog.getExistingDirectory(None, "Select Folder")
        self.directory_path_text.setText(self.directory_path)
        self.daze_data.setdefault('Preferences', {})['directory_path'] = self.directory_path
        daze_state.save_state(self.daze_data)

    def handle_paste(self):
        clipboard_text = QApplication.instance().clipboard().text()
        # XXX temporarily commenting out mp3 download/conversion
        # youtubedl_item = YoutubeDLUtility(clipboard_text, self.directory_path)
        # item = QStandardItem(self.icon, youtubedl_item.name)
        item = QStandardItem(self.icon, clipboard_text)
        self.playlist_item.appendRow(item)
        self.daze_data.setdefault('Playlist', {})[clipboard_text] = {'filename': '/dazesomething.mp3'}
        daze_state.save_state(self.daze_data)

    def item_clicked(self, index):
        print('This item has been clicked: ', index)

    def handle_remove(self):
        item = self.playlist.currentIndex()
        del self.daze_data.setdefault('Playlist', {})[item.data()]
        self.playlist_item.removeRow(item.row())
        daze_state.save_state(self.daze_data)

    def callback(self,
                 index_qmodel_index,
                 role,
                 before_value,
                 after_value):
        new_filename = (self.daze_data.setdefault('Playlist', {})
                                      .setdefault(before_value, {})
                                      .get('filename').replace(before_value,
                                                               after_value))
        self.daze_data.setdefault('Playlist', {})[after_value] = {'filename': new_filename}
        del self.daze_data.setdefault('Playlist', {})[before_value]
        daze_state.save_state(self.daze_data)

