#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.QT import *


class MInputDialog(QDialog):
    def __init__(self, parent=None, title='MInputDialog', text='', defaultText='', reg=None):
        super(MInputDialog, self).__init__(parent)
        self.label = QLabel(text)
        self.lineEdit = QLineEdit()
        if reg:
            self.setValidator(reg)
        okButton = QPushButton(self.tr('ok'))
        self.connect(okButton, SIGNAL('clicked()'), self.slotOK)
        cancelButton = QPushButton(self.tr('cancel'))
        self.connect(cancelButton, SIGNAL('clicked()'), self.close)
        butLay = QHBoxLayout()
        butLay.addWidget(okButton)
        butLay.addWidget(cancelButton)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        layout.addLayout(butLay)
        self.setLayout(layout)
        self.setWindowTitle(title)

    def setValidator(self, reg):
        validator = QRegExpValidator(reg, self)
        self.lineEdit.setValidator(validator)

    @Slot()
    def slotOK(self):
        if self.lineEdit.text():
            self.accept()
        else:
            self.lineEdit.setFocus()

    @classmethod
    def getText(cls, parent=None, title='MInputDialog', text='', defaultText='', reg=None):
        dialog = MInputDialog(parent, title, text, defaultText, reg)
        result = dialog.exec_()
        return dialog.lineEdit.text(), result
