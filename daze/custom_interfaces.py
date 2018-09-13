'''
Custom intefaces
'''
import os

from PyQt5.QtWidgets import QListView, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QVariant, pyqtSignal, QModelIndex, Qt


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

