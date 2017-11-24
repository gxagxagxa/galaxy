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
from CORE.APATH import APATH
from GUI.CONFIG import MInjectDataConfigFunc


class MInjectDataDialog(QDialog):
    def __init__(self, orm, parent=None):
        super(MInjectDataDialog, self).__init__(parent)
        self.setWindowTitle('Inject Data')
        geo = QApplication.desktop().screenGeometry()
        self.setGeometry(geo.width() / 4, geo.height() / 4, geo.width()/2, geo.height()/2)
        self.parentORM = orm
        self.initUI()

    def initUI(self):
        self.ormLabel = QLabel()
        context = '<span style="font-size:16px;color:#888">{}</span>'.format(
            DB_UTIL.hierarchy(self.parentORM, posix=True))
        self.ormLabel.setText(context)
        self.dragFolderButton = MDragFileButton()
        self.dragFolderButton.setFixedHeight(100)
        self.dragFolderButton.setFolderMode(MDragFileButton.FOLDER)
        self.dragFileButton = MDragFileButton()
        self.dragFileButton.setFixedHeight(100)
        # self.dragFileButton.setExtList(['.csv', '.jpg', '.png'])
        self.connect(self.dragFolderButton, SIGNAL('sigGetFile(QString)'), self.slotAddFile)
        self.connect(self.dragFileButton, SIGNAL('sigGetFile(QString)'), self.slotAddFile)

        fileLay = QFormLayout()
        fileLay.addRow('Folder:', self.dragFolderButton)
        fileLay.addRow('File:', self.dragFileButton)

        configDataDict = MInjectDataConfigFunc().get('injectTableView')
        self.resultTableView = MTableView(headerList=configDataDict.get('headerList'), parent=self)

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

    def slotAddFile(self, fileName):
        ap = APATH.APATH(fileName)
        resultList = []
        resultDict = ap.scan()
        if isinstance(resultDict, dict):
            resultList.append(self._addExtraData(resultDict))
        else:
            for dataDict in resultDict:
                resultList.append(self._addExtraData(dataDict))

        origDataList = self.resultTableView.getAllItemsData()
        origDataList.extend(resultList)
        self.resultTableView.realModel.setDataList(origDataList)

    def _addExtraData(self, resultDict):
        resultDict.update({"ui_name": resultDict.get('filename').name,
                           "ui_start": resultDict.get('frames')[0],
                           "ui_end": resultDict.get('frames')[-1],
                           "ui_count": len(resultDict.get('frames')),
                           "ui_missing": '/'.join([str(i) for i in  resultDict.get('missing')]),
                           "ui_path": resultDict.get('filename')
                           })
        return resultDict

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
    orm = sess().query(ATOM).filter(ATOM.name == '2017-11-24').one()
    test = MInjectDataDialog(orm)
    test.show()
    sys.exit(app.exec_())
