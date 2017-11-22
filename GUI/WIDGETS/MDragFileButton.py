#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.QT import *
from GUI.IMAGES import IMAGE_PATH
import os


class MDragFileButton(QPushButton):
    FOLDER = 0
    FILE = 1

    def __init__(self, parent=None):
        super(MDragFileButton, self).__init__(parent)
        self.extList = []
        self.folderMode = MDragFileButton.FILE
        toolQss = '''QPushButton{padding:5px; border:2px dashed #aaa ;border-radius:5px;}'''
        self.setStyleSheet(toolQss)
        self.connect(self, SIGNAL('clicked()'), self.slotClicked)
        self.setAcceptDrops(True)
        self._setIcon()

    def setExtList(self, extList):
        self.extList = extList

    def setFolderMode(self, flag):
        self.folderMode = flag
        self._setIcon()

    def _setIcon(self):
        if self.folderMode == MDragFileButton.FOLDER:
            self.setIcon(QIcon(IMAGE_PATH + '/icon-drag-folder.png'))
            self.setIconSize(QSize(220, 40))
        else:
            self.setIcon(QIcon(IMAGE_PATH + '/icon-drag-file.png'))
            self.setIconSize(QSize(200, 40))

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        QPushButton.enterEvent(self, event)

    @Slot()
    def slotClicked(self):
        if self.folderMode == MDragFileButton.FOLDER:
            folder = QFileDialog.getExistingDirectory(self, 'Folder', '', )
            if folder:
                self.emit(SIGNAL('sigGetFile(QString)'), folder)
        else:
            filterFormat = 'File(%s)' % (' '.join(['*' + e for e in self.extList]))
            fileName, fileType = QFileDialog.getOpenFileName(self, 'File', '', filterFormat)
            if fileName:
                self.emit(SIGNAL('sigGetFile(QString)'), fileName)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            urls = event.mimeData().urls()
            if len(urls) == 1:
                fileName = urls[0].toLocalFile()
                if self.folderMode == MDragFileButton.FILE and os.path.splitext(fileName)[-1] in self.extList:
                    event.acceptProposedAction()
                elif os.path.isdir(fileName) and self.folderMode == MDragFileButton.FOLDER:
                    event.acceptProposedAction()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        fileName = url.toLocalFile()
        self.emit(SIGNAL('sigGetFile(QString)'), fileName)
        print fileName



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    test = MDragFileButton()
    test.setExtList(['.ma', '.mb'])
    test.show()
    sys.exit(app.exec_())
