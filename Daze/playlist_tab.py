'''
Playlist tab functionality
'''
import os
import re
import shutil

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
                             QTextEdit,
                             QAbstractItemView)
from PyQt5.QtGui import (QStandardItem,
                         QStandardItemModel,
                         QIcon,
                         QKeySequence)
from PyQt5.QtCore import (pyqtSignal,
                          QModelIndex,
                          QVariant,
                          Qt)


class QNonStandardItemModel(QStandardItemModel):
    '''
    Subclass QStandardItemModel to intercept the changing text of an item to
    represent the change made in daze_data
    '''
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


class NonStandardQListView(QListView):
    '''
    Subclass QListView to provide specified drag/drop capabilities
    '''
    dropped_value = pyqtSignal(str, str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.setDropAction(Qt.MoveAction)
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                if os.path.isfile(url.path()):
                    self.dropped_value.emit(url.fileName(), url.path())
        else:
            e.ignore()


class PlaylistTab(QWidget):
    def __init__(self, daze_data):
        '''
        Initialization of the playlist tab

        @daze_data: dictionary of daze related data
        '''
        super().__init__()

        self.playlist = NonStandardQListView(self)
        self.playlist_item = QNonStandardItemModel()
        # self.playlist.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.playlist.setDragEnabled(True)
        # self.playlist.setDragDropMode(QAbstractItemView.InternalMove)
        self.playlist.setModel(self.playlist_item)

        # default directory path is the user's Downloads folder
        self.directory_path = os.path.expanduser('~/Downloads')
        self.file_dialog = QFileDialog()

        # set the text to the default directory path
        self.directory_path_text = QTextEdit(self)
        self.directory_path_text.setReadOnly(True)
        self.directory_path_text.setMaximumHeight(28)

        # button to allow users to change the directory path
        self.choose_directory = QPushButton("Choose Folder", self)

        # load daze data
        try:
            self.daze_data = daze_state.load_state()
            self.load_daze()
        except DazeStateException:
            self.daze_data = daze_data
            self.set_defaults()

        self.initUI()

    def load_daze(self):
        '''
        load daze data
        '''
        for name, metadata in self.daze_data.setdefault('Playlist', {}).items():
            item = QStandardItem(name)
            item.setDropEnabled(False)
            self.playlist_item.appendRow(item)

        self.directory_path = (self.daze_data.get('Preferences')
                                             .get('directory_path'))
        self.directory_path_text.setText(self.directory_path)

    def set_defaults(self):
        '''
        set defaults
        '''
        # set empty playlist
        self.daze_data.setdefault('Playlist', {})

        # set default directory path
        directory_path = (self.daze_data.setdefault('Preferences', {})
                                        .setdefault('directory_path',
                                                    self.directory_path))
        self.directory_path_text.setText(directory_path)

        daze_state.save_state(self.daze_data)

    def initUI(self):
        # wire up signals
        QShortcut(QKeySequence('Ctrl+v'), self).activated.connect(self.handle_paste)
        QShortcut(QKeySequence('Ctrl+r'), self).activated.connect(self.handle_remove)

        self.playlist.clicked.connect(self.item_clicked)
        self.playlist.dropped_value.connect(self.audio_dropped)
        self.playlist_item.itemBeforeAndAfterChanged.connect(self.callback)

        self.choose_directory.clicked.connect(self.open_directory)

        # get playlist item icon
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

    def open_directory(self):
        '''
        User selects the directory to store audio files in
        '''
        self.directory_path = self.file_dialog.getExistingDirectory(None, "Select Folder")
        self.directory_path_text.setText(self.directory_path)
        self.daze_data.get('Preferences')['directory_path'] = self.directory_path
        daze_state.save_state(self.daze_data)

    def handle_paste(self):
        '''
        User pastes link into the playlist. Trigger download/conversion of the
        link provided to mp3 format and store it in the default directory path
        '''
        paste_output = QApplication.instance().clipboard().text()

        # ensure valid url pasted
        regex = re.compile(
                r'^(?:http|ftp)s?://'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, paste_output) is None:
            print('{} is not a valid URL'.format(paste_output))
            return

        youtubedl_item = YoutubeDLUtility(paste_output, self.directory_path)
        item = QStandardItem(youtubedl_item.name)
        item.setDropEnabled(False)
        self.playlist_item.appendRow(item)
        self.daze_data.get('Playlist')[youtubedl_item.name] = youtubedl_item.metadata
        daze_state.save_state(self.daze_data)

    def item_clicked(self, index):
        '''
        User clicks a playlist item
        '''
        pass

    def handle_remove(self):
        '''
        User removes a playlist item
        '''
        item = self.playlist.currentIndex()
        del self.daze_data.get('Playlist')[item.data()]
        self.playlist_item.removeRow(item.row())
        daze_state.save_state(self.daze_data)

    def audio_dropped(self, file_name, path):
        '''
        User drags/drops an mp3 file into the playlist

        @param file_name: name of the file dragged into the playlist
        @param path: the path of the file dragged into the playlist
        '''
        if not file_name.endswith('.mp3'):
            print('Only mp3 files support dragging/dropping')
            return
        # move mp3 file into directory_path if not already in there
        if self.directory_path not in path:
            shutil.move(path, self.directory_path)

        new_path = os.path.join(self.directory_path, file_name)
        name = file_name.split('.mp3')[0]
        item = QStandardItem(name)
        item.setDropEnabled(False)
        self.playlist_item.appendRow(item)
        self.daze_data.get('Playlist')[name] = {'filename': new_path}
        daze_state.save_state(self.daze_data)

    def callback(self,
                 index_qmodel_index,
                 role,
                 before_value,
                 after_value):
        '''
        User changes a playlist item's name
        '''
        new_filename = (self.daze_data.get('Playlist')
                                      .get(before_value)
                                      .get('filename').replace(before_value,
                                                               after_value))

        del self.daze_data.get('Playlist')[before_value]
        self.daze_data.get('Playlist')[after_value] = {'filename': new_filename}
        daze_state.save_state(self.daze_data)

