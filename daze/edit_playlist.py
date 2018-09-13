'''
Edit playlist item
'''
import datetime
from .qrangeslider import QRangeSlider
from pydub import AudioSegment
from mutagen import mp3
from PyQt5.QtWidgets import (QDialog,
                             QHBoxLayout,
                             QVBoxLayout,
                             QStyle,
                             QPushButton,
                             QLabel)
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class EditPlaylistItem(QDialog):
    def __init__(self, parent, daze_data, current_item):
        super().__init__(parent)
        self.daze_data = daze_data
        self.media_player = QMediaPlayer(self)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)

        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.hbox2 = QHBoxLayout()

        self.setGeometry(200, 200, 550, 150)

        self.current_item = current_item
        self.audio_name = QLabel(current_item.data())
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_clicked)
        self.close_button = QPushButton('Close', self)
        self.close_button.clicked.connect(self.close_clicked)
        self.play_button = QPushButton(self)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setEnabled(True)

        media_path = (self.daze_data.get('Playlist')
                                    .get(self.current_item.data())
                                    .get('filename'))
        audio = mp3.MP3(media_path)
        self.audio_length = audio.info.length

        self.qrangeslider = QRangeSlider(parent=self)
        self.qrangeslider.setFixedHeight(50)
        self.qrangeslider.setMin(0)
        self.qrangeslider.setMax(round(self.audio_length))
        self.max_val = round(self.audio_length)
        self.min_val = round(0)
        self.qrangeslider.setRange(0, round(self.audio_length))
        self.qrangeslider.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        self.qrangeslider.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        self.qrangeslider.handle.setTextColor(0)
        self.qrangeslider.start_changed.connect(self.start_changed)
        self.qrangeslider.end_changed.connect(self.end_changed)

        self.end_time = str(datetime.timedelta(seconds=round(self.audio_length)))
        self.length_time = self.end_time
        self.start_time = str(datetime.timedelta(seconds=round(0)))
        self.current_time = self.start_time
        self.running_time = QLabel('{}/{}'.format(self.current_time,
                                                  self.length_time))

        self.vbox.addWidget(self.audio_name)
        self.hbox2.addWidget(self.play_button)
        self.hbox2.addWidget(self.qrangeslider)
        self.hbox2.addWidget(self.running_time)
        self.hbox.addWidget(self.close_button)
        self.hbox.addWidget(self.save_button)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

        self.audio_filename = (self.daze_data.get('Playlist')
                                             .get(current_item.data())
                                             .get('filename'))
        # possibly set slider to audio length here
        audio_file = QUrl.fromLocalFile(self.audio_filename)
        audio_content = QMediaContent(audio_file)
        self.media_player.setMedia(audio_content)

    def end_changed(self, max_val):
        self.media_player.pause()
        self.max_val = max_val
        self.end_time = str(datetime.timedelta(seconds=round(self.max_val)))

    def start_changed(self, min_val):
        self.min_val = min_val
        self.media_player.pause()
        self.start_time = str(datetime.timedelta(seconds=round(self.min_val)))
        self.media_player.setPosition(self.min_val * 1000)

    def media_state_changed(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, value):
        # maybe add a slider to update here
        pos = int((self.media_player.position() / 1000))

        self.running_time.setText('{}/{}'.format(datetime.timedelta(seconds=pos),
                                                 self.length_time))
        if int((self.media_player.position() / 1000)) == self.max_val:
            self.media_player.pause()

    def play_audio(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def save_clicked(self):
        song = AudioSegment.from_mp3(self.audio_filename)
        min_mili = self.min_val * 1000
        max_mili = self.max_val * 1000
        new_song = song[min_mili: max_mili + 1000]
        new_song.export(self.audio_filename, format='mp3')
        self.close_clicked()

    def close_clicked(self):
        self.media_player.stop()
        self.close()

    def closeEvent(self, event):
        self.media_player.stop()
        super().closeEvent(event)

