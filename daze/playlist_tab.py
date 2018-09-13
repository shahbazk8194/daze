'''
Playlist tab functionality
'''
import os
import re
import shutil

from .utils.youtube_dl import YoutubeDLUtility
from .utils import daze_state
from .errors import DazeStateException
from .custom_interfaces import NonStandardQListView, QNonStandardItemModel
from .edit_playlist import EditPlaylistItem
from .media_player import MediaPlayer

from PyQt5.QtWidgets import (QWidget,
                             QHBoxLayout,
                             QVBoxLayout,
                             QShortcut,
                             QApplication,
                             QPushButton,
                             QFileDialog,
                             QTextEdit,
                             QMenu,
                             QAction)
from PyQt5.QtGui import (QStandardItem,
                         QIcon,
                         QKeySequence)
from PyQt5.QtCore import Qt


class PlaylistTab(QWidget):
    def __init__(self, daze_data):
        '''
        Initialization of the playlist tab

        @daze_data: dictionary of daze related data
        '''
        super().__init__()
        tool_tip = ('Drag/drop mp3 file or copy/paste youtube link to '
                    'download audio. Right-click to play/edit audio files.')
        self.setToolTip(tool_tip)

        self.playlist = NonStandardQListView(self)
        self.playlist_item = QNonStandardItemModel()
        self.playlist.setDragEnabled(True)
        self.playlist.setModel(self.playlist_item)

        # menu
        self.playlist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlist.customContextMenuRequested.connect(self.display_menu)

        # default directory path is the user's Downloads folder
        self.directory_path = os.path.expanduser('~/Downloads')
        self.file_dialog = QFileDialog()

        # set the text to the default directory path
        self.directory_path_text = QTextEdit(self)
        self.directory_path_text.setReadOnly(True)
        self.directory_path_text.setMaximumHeight(28)

        # button to allow users to change the directory path
        self.choose_directory = QPushButton("Choose Folder", self)

        # get playlist item icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'daze_icon.png')
        self.icon = QIcon(icon_path)

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
            item = QStandardItem(self.icon, name)
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

        # self.playlist.clicked.connect(self.item_clicked)
        self.playlist.dropped_value.connect(self.audio_dropped)
        self.playlist_item.itemBeforeAndAfterChanged.connect(self.callback)

        self.choose_directory.clicked.connect(self.open_directory)

        # set layouts
        self.hbox = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.playlist)
        self.hbox.addWidget(self.choose_directory)
        self.hbox.addWidget(self.directory_path_text)
        self.vbox.addLayout(self.hbox2)
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

        try:
            youtubedl_item = YoutubeDLUtility(paste_output, self.directory_path)
            youtubedl_item.download_and_convert()
        except Exception as e:
            print('Unable to download: {}'.format(paste_output))
            print(e)
        else:
            item = QStandardItem(self.icon, youtubedl_item.name)
            item.setDropEnabled(False)
            self.playlist_item.appendRow(item)
            self.daze_data.get('Playlist')[youtubedl_item.name] = youtubedl_item.metadata
            daze_state.save_state(self.daze_data)

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
        item = QStandardItem(self.icon, name)
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
        os.rename((self.daze_data.get('Playlist')
                                 .get(before_value)
                                 .get('filename')), new_filename)

        del self.daze_data.get('Playlist')[before_value]
        self.daze_data.get('Playlist')[after_value] = {'filename': new_filename}
        daze_state.save_state(self.daze_data)

    def display_menu(self, position):
        menu = QMenu('Menu', self)
        play_action = QAction('Play', self)
        play_action.setShortcut('Ctrl+P')
        edit_action = QAction('Edit', self)
        edit_action.setShortcut('Ctrl+E')

        media_path = (self.daze_data.get('Playlist')
                                    .get(self.playlist.currentIndex().data())
                                    .get('filename'))

        menu.addAction(play_action)
        menu.addAction(edit_action)

        media_player = MediaPlayer(self, self.playlist.currentIndex(), media_path)
        edit_media = EditPlaylistItem(self, self.daze_data, self.playlist.currentIndex())

        play_action.triggered.connect(media_player.show)
        edit_action.triggered.connect(edit_media.show)

        menu.exec_(self.playlist.mapToGlobal(position))

