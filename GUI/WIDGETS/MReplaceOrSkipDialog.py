#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

from MToolButton import *


class MReplaceOrSkipDialog(QDialog):
    Rename = 0
    Skip = 1
    def __init__(self, parent = None):
        super(MReplaceOrSkipDialog, self).__init__(parent)
        self.setWindowTitle('Rename or Skip Files/Folders')
        self.result = None
        self.initUI()

    def initUI(self):
        self.infoLabel = QLabel(u'目标包含同名文件(夹)')
        renameButton = QPushButton('Rename them')
        skipButton = QPushButton('Skip them')

        self.buttonGrp = QButtonGroup()
        self.buttonGrp.addButton(renameButton, MReplaceOrSkipDialog.Rename)
        self.buttonGrp.addButton(skipButton, MReplaceOrSkipDialog.Skip)

        self.connect(self.buttonGrp, SIGNAL('buttonClicked(int)'), self.slotButtonClicked)

        mainLay = QVBoxLayout()
        mainLay.addWidget(self.infoLabel)
        mainLay.addWidget(renameButton)
        mainLay.addWidget(skipButton)
        self.setLayout(mainLay)

    def slotButtonClicked(self, index):
        self.result = index
        self.close()

    def getResult(self):
        return self.result



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    test = MReplaceOrSkipDialog()
    test.setSameCount(10)
    test.exec_()
    print test.getResult()
    sys.exit(app.exec_())
