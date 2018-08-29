'''
Reponsible for about dialog creation
'''
from datetime import datetime
import os

from .constants import NAME, VERSION
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (QDialog,
                             QLabel,
                             QVBoxLayout,
                             QHBoxLayout)


class AboutMenu(QDialog):
    def __init__(self):
        '''
        About dialog initialization
        '''
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(600, 200)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)

        version_font = QFont()
        version_font.setPointSize(11)

        copyright_font = QFont()
        copyright_font.setPointSize(8)
        copyright_font.setBold(True)

        daze_logo = QLabel(self)
        daze_logo_path = QPixmap(os.path.join(os.path.dirname(__file__),
                                              'icons',
                                              'daze_logo.png'))
        daze_logo.setPixmap(daze_logo_path)
        name_message = QLabel(self)
        name_message.setFont(name_font)
        version_message = QLabel(self)
        version_message.setFont(version_font)
        info_message = QLabel(self)
        copyright_message = QLabel(self)
        copyright_message.setFont(copyright_font)

        vbox = QVBoxLayout()
        vbox.addWidget(name_message)
        vbox.addWidget(version_message)
        vbox.addWidget(info_message)
        vbox.addWidget(copyright_message)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(daze_logo)
        self.setLayout(hbox)

        name_msg = '{}'.format(NAME)

        version_msg = 'Version {}'.format(VERSION)

        info_msg = '''
            Daze is not responsible for illegal downloads of any content
            that violate the terms and services agreement of any business.
            '''

        copyright_msg = ('Copyright (c) {} Shahbaz Khan. All Rights '
                         'Reserved'.format(datetime.today().year))

        name_message.setText(name_msg)
        version_message.setText(version_msg)
        info_message.setText(info_msg)
        copyright_message.setText(copyright_msg)

