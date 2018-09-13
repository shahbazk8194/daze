import datetime
from mutagen import mp3
from PyQt5.QtWidgets import (QDialog,
                             QPushButton,
                             QSlider,
                             QLabel,
                             QVBoxLayout,
                             QHBoxLayout,
                             QStyle,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer


class MediaPlayer(QDialog):
    def __init__(self, parent, current_item, media_path):
        super().__init__(parent)
        self.initUI(current_item.data(), media_path)

    def initUI(self, current_item, media_path):
        '''
        Initialize the media player
        '''
        self.resize(550, 150)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        self.media_player = QMediaPlayer(self)
        media_url = QUrl.fromLocalFile(media_path)
        media_content = QMediaContent(media_url)
        self.media_player.setMedia(media_content)
        media_mp3 = mp3.MP3(media_path)
        media_length = media_mp3.info.length

        # set potentiona error message
        self.error_label = QLabel(self)
        self.error_label.setSizePolicy(QSizePolicy.Preferred,
                                       QSizePolicy.Maximum)

        # set play/pause button
        self.action_button = QPushButton(self)
        self.action_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.action_button.setEnabled(True)

        # media slider
        self.media_slider = QSlider(Qt.Horizontal, self)
        self.media_slider.setEnabled(True)
        self.media_slider.setRange(0, media_length)
        self.media_slider.setFocusPolicy(Qt.NoFocus)

        # display time
        self.end_time = str(datetime.timedelta(seconds=round(media_length)))
        self.display_time = QLabel('{}/{}'.format(str(datetime.timedelta(seconds=0)),
                                                  self.end_time))

        # current item name
        self.current_item = QLabel(current_item)

        # set layouts
        vbox.addWidget(self.current_item)
        hbox.addWidget(self.action_button)
        hbox.addWidget(self.media_slider)
        hbox.addWidget(self.display_time)
        vbox.addLayout(hbox)
        vbox.addWidget(self.error_label)
        self.setLayout(vbox)

        # set up signals
        self.action_button.clicked.connect(self.trigger_action)
        self.media_slider.sliderMoved.connect(self.slider_value_changed)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)

    def trigger_action(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def slider_value_changed(self, new_value):
        self.media_player.setPosition(new_value * 1000)

    def media_state_changed(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.action_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.action_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, new_position):
        self.display_time.setText('{}/{}'.format(str(datetime.timedelta(seconds=round(new_position / 1000))),
                                                 self.end_time))
        if not self.media_slider.isSliderDown():
            self.media_slider.setValue(new_position / 1000.0)

    def closeEvent(self, event):
        self.media_player.stop()
        super().closeEvent(event)

