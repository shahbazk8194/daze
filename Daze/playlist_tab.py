'''
Reponsible for playlist tab creation
'''
import os

from .youtubedl_utility import YoutubeDLUtility
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
        self.daze_data = daze_data
        self.daze_data['Playlist'] = {}
        super().__init__()
        self.initUI()

    def _loadPlaylist(self):
        '''
        Responsible for loading/creating initial playlist dictionary
        '''
        pass

    def initUI(self):
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

        self.playlist = QListView(self)
        self.audio_item = QNonStandardItemModel()

        # default path is user's Downloads folder
        self.folder_path = os.path.expanduser('~/Downloads')
        self.daze_data['Preferences']['directory_path'] = self.folder_path

        # set the shortcut ctrl+v for paste
        QShortcut(QKeySequence('Ctrl+v'), self).activated.connect(self._handlePaste)
        QShortcut(QKeySequence('Ctrl+r'), self).activated.connect(self._handleRemove)

        # wire up signals
        self.playlist.clicked.connect(self.item_clicked)
        self.audio_item.itemBeforeAndAfterChanged.connect(self.callback)

        path = os.path.join(os.path.dirname(__file__), 'icons', 'daze_icon1.png')
        self.icon = QIcon(path)
        self.playlist.setModel(self.audio_item)
        self.vbox.addWidget(self.playlist)

        choose_directory = QPushButton("Choose Folder", self)
        choose_directory.clicked.connect(self.open_folder)

        self.display_text = QTextEdit(self)
        self.display_text.setText(self.folder_path)
        self.display_text.setReadOnly(True)
        self.display_text.setMaximumHeight(28)

        self.hbox.addWidget(choose_directory)
        self.hbox.addWidget(self.display_text)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

    def open_folder(self):
        dialog = QFileDialog()
        self.folder_path = dialog.getExistingDirectory(None, "Select Folder")
        self.display_text.setText(self.folder_path)
        self.daze_data['Preferences']['directory_path'] = self.folder_path

    def _handlePaste(self):
        clipboard_text = QApplication.instance().clipboard().text()
        # youtubedl_item = YoutubeDLUtility(clipboard_text, self.folder_path)
        # item = QStandardItem(self.icon, youtubedl_item.name)
        item = QStandardItem(self.icon, clipboard_text)
        self.audio_item.appendRow(item)
        self.daze_data['Playlist'][clipboard_text] = {'filename': '/dazesomething.mp3'}
        print(self.daze_data)

    def item_clicked(self, index):
        print('This item has been clicked: ', index)

    def _handleRemove(self):
        item = self.playlist.currentIndex()
        del self.daze_data['Playlist'][item.data()]
        self.audio_item.removeRow(item.row())
        print(self.daze_data)

    def callback(self,
                 index_qmodel_index,
                 role,
                 before_value,
                 after_value):
        new_filename = (self.daze_data.get('Playlist')
                                      .get(before_value)
                                      .get('filename').replace(before_value,
                                                               after_value))
        self.daze_data['Playlist'][after_value] = {'filename': new_filename}
        del self.daze_data['Playlist'][before_value]
        print(self.daze_data)

