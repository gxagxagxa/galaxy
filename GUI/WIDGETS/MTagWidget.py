#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################
from GUI.QT import *
from GUI.WIDGETS.MItemView import MListView
from MTagLabel import MAZTagRect
from MToolButton import MAddButton
from GUI.PLUGINS.MTableHandle import MTag
from CORE.DB_CONNECT import *


def getTextColor(backgroundColor):
    light = backgroundColor.redF() * 0.30 + backgroundColor.greenF() * 0.59 + backgroundColor.blueF() * 0.11
    if light < 0.5:
        return QColor.fromRgbF(1 - 0.3 * light, 1 - 0.3 * light, 1 - 0.3 * light)
    else:
        return QColor.fromRgbF((1 - light) * 0.3, (1 - light) * 0.3, (1 - light) * 0.3)


class MTagEditDialog(QDialog):
    def __init__(self, parent=None):
        super(MTagEditDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('edit_tag'))
        self.initUI()
        self.refreshData()

    def initUI(self):
        self.tagListView = MListView()
        self.connect(self.tagListView, SIGNAL('sigCurrentChanged(PyObject)'), self.slotUpdateButton)

        self.newTagWidget = MAddTagWidget()
        self.connect(self.newTagWidget, SIGNAL('sigAddTag(PyObject)'), self.slotNewTag)

        self.editButton = QPushButton('Edit')
        self.editButton.setEnabled(False)
        self.connect(self.editButton, SIGNAL('clicked()'), self.slotEditTag)

        self.deleteButton = QPushButton('Delete')
        self.deleteButton.setEnabled(False)
        self.connect(self.deleteButton, SIGNAL('clicked()'), self.slotDeleteType)

        self.cancelButton = QPushButton('Close')
        self.connect(self.cancelButton, SIGNAL('clicked()'), self.close)

        editLay = QHBoxLayout()
        editLay.addWidget(self.editButton)
        editLay.addWidget(self.deleteButton)

        commitLay = QHBoxLayout()
        commitLay.addStretch()
        commitLay.addWidget(self.cancelButton)

        mainLay = QVBoxLayout()
        mainLay.addLayout(editLay)
        mainLay.addWidget(self.tagListView)
        mainLay.addWidget(self.newTagWidget)
        mainLay.addLayout(commitLay)

        self.setLayout(mainLay)

    @Slot(object)
    def slotUpdateButton(self, orm):
        if orm:
            self.editButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
        else:
            self.editButton.setEnabled(False)
            self.deleteButton.setEnabled(False)

    @Slot(object)
    def slotNewTag(self, tagORM):
        self.refreshData()

    def slotEditTag(self):
        dialog = MEditTagDialog(self)
        dialog.setTagORM(self.tagListView.getCurrentItemData())
        if dialog.exec_():
            self.refreshData()

    def refreshData(self):
        self.tagListView.realModel.setDataList(sess().query(TAG).all())

    def slotDeleteType(self):
        currentORM = self.tagListView.getCurrentItemData()
        but = QMessageBox.question(self, 'WARNING', 'Are you sure to delete?')
        if but == QMessageBox.Ok:
            MTag.delete(currentORM)
            self.refreshData()


class MEditTagDialog(QDialog):
    def __init__(self, parent = None):
        super(MEditTagDialog, self).__init__(parent)
        self.backgroundColor = QColor('#f00')
        self.initUI()
        self.setColorButtonIcon()

    def initUI(self):
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setPlaceholderText('Enter new tag name')
        self.colorButton = QToolButton()
        self.connect(self.colorButton, SIGNAL('clicked()'), self.slotColor)
        self.addButton = MAddButton()
        self.connect(self.addButton, SIGNAL('clicked()'), self.slotEditTag)
        mainLay = QHBoxLayout()
        mainLay.setContentsMargins(0, 0, 0, 0)
        mainLay.addWidget(self.nameLineEdit)
        mainLay.addWidget(self.colorButton)
        mainLay.addWidget(self.addButton)
        self.setLayout(mainLay)

    def setTagORM(self, tagORM):
        self.targetORM = tagORM
        self.backgroundColor = QColor(self.targetORM.color)
        self.nameLineEdit.setText(self.targetORM.name)

    def slotColor(self):
        penColor = QColorDialog.getColor(self.backgroundColor, self)
        if penColor.isValid():
            self.backgroundColor = penColor
            self.setColorButtonIcon()

    def setColorButtonIcon(self):
        pix = QPixmap(20, 20)
        pix.fill(self.backgroundColor)
        self.colorButton.setIcon(QIcon(pix))

    def slotEditTag(self):
        self.targetORM.name = self.nameLineEdit.text()
        self.targetORM.color = self.backgroundColor.name()
        sess().commit()
        self.accept()


class MAddTagWidget(QWidget):
    def __init__(self, parent=None):
        super(MAddTagWidget, self).__init__(parent)
        self.backgroundColor = QColor('#f00')
        self.initUI()
        self.setColorButtonIcon()

    def initUI(self):
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setPlaceholderText('Enter new tag name')
        self.colorButton = QToolButton()
        self.connect(self.colorButton, SIGNAL('clicked()'), self.slotColor)
        self.addButton = MAddButton()
        self.connect(self.addButton, SIGNAL('clicked()'), self.slotAddTag)
        mainLay = QHBoxLayout()
        mainLay.setContentsMargins(0, 0, 0, 0)
        mainLay.addWidget(self.nameLineEdit)
        mainLay.addWidget(self.colorButton)
        mainLay.addWidget(self.addButton)
        self.setLayout(mainLay)

    def slotColor(self):
        penColor = QColorDialog.getColor(self.backgroundColor, self)
        if penColor.isValid():
            self.backgroundColor = penColor
            self.setColorButtonIcon()

    def setColorButtonIcon(self):
        pix = QPixmap(20, 20)
        pix.fill(self.backgroundColor)
        self.colorButton.setIcon(QIcon(pix))

    def slotAddTag(self):
        newName = self.nameLineEdit.text()
        if newName:
            if not MTag.validateExist(newName):
                orm = MTag.inject(name=newName, color=self.backgroundColor.name())
                self.emit(SIGNAL('sigAddTag(PyObject)'), orm)
                self.nameLineEdit.setText('')
            else:
                QMessageBox.warning(self, 'ERROR', 'Name has already exist.')
        self.nameLineEdit.setFocus(Qt.MouseFocusReason)


class MChooseTagDialog(QDialog):
    def __init__(self, parent=None):
        super(MChooseTagDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.Dialog | Qt.FramelessWindowHint)
        self.targetORMList = None
        self.initUI()

    def initUI(self):
        self.existTagListView = MListView()
        self.existTagListView.setFixedHeight(100)
        self.connect(self.existTagListView, SIGNAL('sigCurrentChanged(PyObject)'), self.slotMoveTag)

        self.tagSearchLineEdit = QLineEdit()
        self.tagSearchLineEdit.setPlaceholderText('Search...')
        self.dbTagListView = MListView()
        self.connect(self.dbTagListView, SIGNAL('sigCurrentChanged(PyObject)'), self.slotAddTag)
        self.connect(self.tagSearchLineEdit, SIGNAL('textChanged(QString)'), self.dbTagListView.sortFilterModel.setFilterFixedString)
        self.addTagWidget = MAddTagWidget()
        self.connect(self.addTagWidget, SIGNAL('sigAddTag(PyObject)'), self.slotAddTag)

        mainLay = QVBoxLayout()
        mainLay.addWidget(self.addTagWidget)
        mainLay.addWidget(self.existTagListView)
        mainLay.addWidget(self.tagSearchLineEdit)
        mainLay.addWidget(self.dbTagListView)

        self.setLayout(mainLay)

    def setTargetORM(self, ormList):
        self.targetORMList = ormList
        self.refreshDataList()

    def refreshDataList(self):
        #TODO: handle ormList
        existTags = self.targetORMList[0].tags.all()
        self.existTagListView.realModel.setDataList(existTags)
        self.dbTagListView.realModel.setDataList([tagORM for tagORM in sess().query(TAG).all() if tagORM not in existTags])

    @Slot(object)
    def slotMoveTag(self, tagORM):
        for orm in self.targetORMList:
            orm.tags.remove(tagORM)
            sess().commit()
        self.refreshDataList()

    @Slot(object)
    def slotAddTag(self, tagORM):
        for orm in self.targetORMList:
            orm.tags.append(tagORM)
            sess().commit()
        self.refreshDataList()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    test = MTagEditDialog()
    test.show()
    sys.exit(app.exec_())
