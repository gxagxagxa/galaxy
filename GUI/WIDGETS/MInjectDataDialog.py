#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

from GUI.QT import *
from MDragFileButton import MDragFileButton
from MToolButton import *
from MItemView import MTableView
from CORE.DB_UTIL import *


class MInjectDataDialog(QDialog):
    def __init__(self, orm, parent = None):
        super(MInjectDataDialog, self).__init__(parent)
        self.setWindowTitle('Inject Data')
        self.parentORM = orm
        self.initUI()

    def initUI(self):
        self.ormLabel = QLabel()
        context = '<span style="font-size:16px;color:#888">{}</span>'.format(DB_UTIL.hierarchy(self.parentORM, posix=True))
        self.ormLabel.setText(context)
        self.dragFolderButton = MDragFileButton()
        self.dragFolderButton.setFixedHeight(100)
        self.dragFolderButton.setFolderMode(MDragFileButton.FOLDER)
        self.dragFileButton = MDragFileButton()
        self.dragFileButton.setFixedHeight(100)
        # self.dragFileButton.setExtList(['.csv', '.jpg', '.png'])
        self.connect(self.dragFolderButton, SIGNAL('sigGetFile(QString)'), self.slotAddFolder)
        self.connect(self.dragFileButton, SIGNAL('sigGetFile(QString)'), self.slotAddFile)

        fileLay = QFormLayout()
        fileLay.addRow('Folder:', self.dragFolderButton)
        fileLay.addRow('File:', self.dragFileButton)

        self.resultTableView = MTableView()

        self.deleteButton = MDeleteButton(size=18)
        self.connect(self.deleteButton, SIGNAL('clicked()'), self.slotDelete)

        settingLay = QHBoxLayout()
        settingLay.addStretch()
        settingLay.addWidget(self.deleteButton)
        self.continueButton = QPushButton(self.tr('Next'))
        self.connect(self.continueButton, SIGNAL('clicked()'), self.slotContinue)
        buttLay = QHBoxLayout()
        buttLay.addWidget(self.deleteButton)
        buttLay.addStretch()
        buttLay.addWidget(self.continueButton)
        mainLay = QVBoxLayout()
        mainLay.addLayout(fileLay)
        mainLay.addWidget(self.resultTableView)
        mainLay.addLayout(buttLay)
        self.setLayout(mainLay)

    def slotAddFolder(self, folder):
        print folder

    def slotAddFile(self, fileName):
        print fileName

    def slotDelete(self):
        indexes = self.csvTableView.selectedIndexes()
        if indexes:
            rows = list(set(index.row() for index in indexes))
            rows.sort()
            for offset, i in enumerate(rows):
                self.csvTableView.tableModel.dataList.pop(i - offset)
            self.csvTableView.tableModel.reset()
        else:
            QMessageBox.warning(self, self.tr('warning'), self.tr('please_select_a_row'))

    def slotContinue(self):
        print self.resultTableView.getAllItemsData()
        
        

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    orm = sess().quert(ATOM).filter(ATOM.name=='2017-11-22').one()
    test = MInjectDataDialog(orm)
    test.show()
    sys.exit(app.exec_())
        