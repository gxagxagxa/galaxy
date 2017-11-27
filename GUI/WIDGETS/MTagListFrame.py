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

EXAMPLE_TAG_LIST = [
    {'name': 'Heroine', 'color': '#e3a0b1'},
    {'name': 'Hero', 'color': '#81d8cf'},
    {'name': 'Green Screen', 'color': '#0c8c2b'},
    {'name': 'Blue Screen', 'color': '#0040da'},
    {'name': 'Passed', 'color': '#c577db'},
    {'name': 'Cut', 'color': '#db8577'},
    {'name': 'OK', 'color': '#9cdb77'},
]


class MTagList(QFrame):
    def __init__(self, parent=None):
        super(MTagList, self).__init__(parent)
        self.initUI()

    def initUI(self):
        print 'initUI'


class MAddFavoriteFrame(QFrame):
    def __init__(self, parent=None):
        super(MAddFavoriteFrame, self).__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setWindowFlags(Qt.Popup | Qt.Window)
        self.setFixedHeight(200)
        self.initUI()

    def initUI(self):
        self.searchLineEdit = QLineEdit()
        self.tagListView = MListView()
        self.connect(self.searchLineEdit, SIGNAL('textChanged(QString)'),
                     self.tagListView.sortFilterModel.setFilterFixedString)
        self.tagListView.realModel.setDataList(EXAMPLE_TAG_LIST)
        self.showAllButton = QPushButton('Show All...')
        mainLay = QVBoxLayout()
        mainLay.addWidget(self.searchLineEdit)
        mainLay.addWidget(self.tagListView)
        mainLay.addWidget(self.showAllButton)
        self.setLayout(mainLay)

    def setExceptDataList(self, dataList):
        self.exceptDataList = [(i.id, i.__tablename__) for i in dataList]

    @Slot(str)
    def slotSearch(self, context):
        pass

    @Slot(object)
    def slotUpdateExceptList(self, dataList):
        self.setExceptDataList(dataList)
        self._updateDataList()

    def _updateDataList(self, arg=None):
        self.rightListView.slotUpdate(self.projectComboBox.currentItemData())
        baseORMList = self.rightListView.getAllItemsData()
        self.rightListView.realModel.setDataList(
            [i for i in baseORMList if (i.id, i.__tablename__) not in self.exceptDataList])

    @Slot()
    def slotAdd(self):
        addList = self.rightListView.getSelectedItemsData()
        if addList:
            self.emit(SIGNAL('sigAddFavoriteORMList(PyObject)'), addList)


def getTextColor(backgroundColor):
    light = backgroundColor.redF() * 0.30 + backgroundColor.greenF() * 0.59 + backgroundColor.blueF() * 0.11
    if light < 0.5:
        return QColor.fromRgbF(1 - 0.3 * light, 1 - 0.3 * light, 1 - 0.3 * light)
    else:
        return QColor.fromRgbF((1 - light) * 0.3, (1 - light) * 0.3, (1 - light) * 0.3)


class MAZTagListWidget(QListWidget):
    def __init__(self, isCheckable, parent=None):
        super(MAZTagListWidget, self).__init__(parent)
        self.checkable = isCheckable
        self.updateContent()

    def updateContent(self):
        self.clear()
        result = EXAMPLE_TAG_LIST
        for dataDict in result:
            print dataDict
            tempItem = QListWidgetItem(dataDict['name'])
            tempItem.setData(Qt.UserRole, dataDict)
            # tempItem.setData(Qt.BackgroundRole, QBrush(QColor(dataDict['color_string'])))
            # tempItem.setData(Qt.ForegroundRole, QBrush(getTextColor(QColor(dataDict['color_string']))))
            # if dataDict['description']:
            #     tempItem.setToolTip(dataDict['description'])
            if self.checkable:
                tempItem.setCheckState(Qt.Unchecked)
            self.addItem(tempItem)

    def getAllItems(self):
        resultItemList = []
        for i in range(self.count()):
            resultItemList.append(self.item(i))
        return resultItemList

    def getCheckedList(self):
        '''
        return: tag id list
        '''
        if not self.checkable:
            return []
        resultList = []
        for item in self.getAllItems():
            if item.checkState() == Qt.Checked:
                resultList.append(item.data(Qt.UserRole))
        return resultList

    def setAllChecked(self):
        if not self.checkable:
            return
        for item in self.getAllItems():
            item.setCheckState(Qt.Checked)

    def setAllUnchecked(self):
        if not self.checkable:
            return
        for item in self.getAllItems():
            item.setCheckState(Qt.Unchecked)

    def setUncheckedList(self, uncheckedIdList):
        if not self.checkable:
            return
        if uncheckedIdList:
            for item in self.getAllItems():
                if item.data(Qt.UserRole) in uncheckedIdList:
                    item.setCheckState(Qt.Unchecked)

    def setCheckedList(self, checkedIdList):
        if not self.checkable:
            return
        if checkedIdList:
            for item in self.getAllItems():
                if item.data(Qt.UserRole) in checkedIdList:
                    item.setCheckState(Qt.Checked)

    def showSelectedTags(self, state):
        if not self.checkable:
            return
        if state == Qt.Checked:
            for item in self.getAllItems():
                if item.checkState() == Qt.Unchecked:
                    item.setHidden(True)
        else:
            self.showAll()

    def showAll(self):
        for item in self.getAllItems():
            if item.isHidden():
                item.setHidden(False)

    def filter(self, text):
        if text:
            resultItems = self.findItems(text, Qt.MatchContains)
            for item in self.getAllItems():
                if item.data(Qt.UserRole) not in [i.data(Qt.UserRole) for i in resultItems]:
                    item.setHidden(True)
        else:
            self.showAll()


class MAZTagBaseWidget(QWidget):
    def __init__(self, isCheckable=False, parent=None):
        super(MAZTagBaseWidget, self).__init__(parent)
        self.checkable = isCheckable
        self.initUI()

    def initUI(self):
        tagGrpBox = QGroupBox(u'tag')
        self.tagSearchLineEdit = QLineEdit()
        showSelectedTagsCheckBox = QCheckBox(self.tr('show_selected'))
        tagAllUncheckedBut = QPushButton(self.tr('clear_selected'))
        tagButLay = QHBoxLayout()
        tagButLay.addWidget(showSelectedTagsCheckBox)
        tagButLay.addWidget(tagAllUncheckedBut)

        self.tagListWidget = MAZTagListWidget(self.checkable)
        self.connect(showSelectedTagsCheckBox, SIGNAL('stateChanged(int)'), self.tagListWidget.showSelectedTags)
        self.connect(tagAllUncheckedBut, SIGNAL('clicked()'), self.tagListWidget.setAllUnchecked)
        self.connect(self.tagSearchLineEdit, SIGNAL('textChanged(QString)'), self.tagListWidget.filter)

        tagLay = QVBoxLayout()
        if self.checkable:
            tagLay.addLayout(tagButLay)
        tagLay.addWidget(self.tagSearchLineEdit)
        tagLay.addWidget(self.tagListWidget)
        tagGrpBox.setLayout(tagLay)

        mainLay = QVBoxLayout()
        mainLay.setContentsMargins(0, 0, 0, 0)
        mainLay.addWidget(tagGrpBox)

        self.setLayout(mainLay)

    def setNoSearch(self):
        self.tagSearchLineEdit.hide()

    def setAllChecked(self):
        self.tagListWidget.setAllChecked()

    def setTagCheckedList(self, checkedList):
        self.tagListWidget.setCheckedList(checkedList)

    def setTagUncheckedList(self, uncheckedList):
        self.tagListWidget.setUncheckedList(uncheckedList)

    def getTagCheckedList(self):
        return self.tagListWidget.getCheckedList()

    def getTagUncheckedList(self):
        return self.tagListWidget.getUncheckedList()


class MAZTagEditDialog(QDialog):
    def __init__(self, op, parent=None):
        super(MAZTagEditDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('edit_tag'))
        self.initUI()

    def initUI(self):
        self.tagWidget = MAZTagBaseWidget(False)
        self.connect(self.tagWidget.tagListWidget, SIGNAL('clicked(const QModelIndex)'), self.slotUpdateButton)

        self.newButton = QPushButton(self.tr('new'))
        self.connect(self.newButton, SIGNAL('clicked()'), self.slotNewTag)

        self.editButton = QPushButton(self.tr('edit'))
        self.editButton.setEnabled(False)
        self.connect(self.editButton, SIGNAL('clicked()'), self.slotEditTag)

        self.deleteButton = QPushButton(self.tr('delete'))
        self.deleteButton.setEnabled(False)
        self.connect(self.deleteButton, SIGNAL('clicked()'), self.slotDeleteType)

        self.cancelButton = QPushButton(self.tr('close'))
        self.connect(self.cancelButton, SIGNAL('clicked()'), self.close)

        editLay = QHBoxLayout()
        editLay.addWidget(self.newButton)
        editLay.addWidget(self.editButton)
        editLay.addWidget(self.deleteButton)

        commitLay = QHBoxLayout()
        commitLay.addStretch()
        commitLay.addWidget(self.cancelButton)

        mainLay = QVBoxLayout()
        mainLay.addLayout(editLay)
        mainLay.addWidget(self.tagWidget)
        mainLay.addLayout(commitLay)

        self.setLayout(mainLay)

    def slotUpdateButton(self, index):
        if index.isValid():
            self.editButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
        else:
            self.editButton.setEnabled(False)
            self.deleteButton.setEnabled(False)

    def slotNewTag(self):
        addTagDialog = MAZTagItemDialog(self)
        if addTagDialog.exec_():
            self.tagWidget.tagListWidget.updateContent()

    def slotEditTag(self):
        selectItem = self.tagWidget.tagListWidget.currentItem()
        editTagItemDialog = MAZTagItemDialog(self)
        currentItemDataDict = selectItem.data(Qt.UserRole)
        editTagItemDialog.setDefaultData(currentItemDataDict)
        if editTagItemDialog.exec_():
            self.tagWidget.tagListWidget.updateContent()

    def slotDeleteType(self):
        selectItem = self.tagWidget.tagListWidget.currentItem()
        but = QMessageBox.question(self, self.tr('warning'), self.tr('really_want_to_delete'))
        if but == QMessageBox.Ok:
            # TODO: delete tag
            # MTag.canDelete()
            self.tagWidget.tagListWidget.updateContent()


class MAddTagFrame(QFrame):
    def __init__(self, parent=None):
        super(MAddTagFrame, self).__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.Window)
        self.initUI()
        self.setColorButtonIcon()

    def initUI(self):
        self.nameLineEdit = QLineEdit()
        self.colorButton = QToolButton()
        self.connect(self.colorButton, SIGNAL('clicked()'), self.slotColor)
        self.connect(self.nameLineEdit, SIGNAL('returnPressed()'), self.slotAddTag)

        mainLay = QHBoxLayout()
        mainLay.addWidget(self.nameLineEdit)
        mainLay.addWidget(self.colorButton)
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
        self.tagPreviewLabel.setColor(self.backgroundColor)

    def slotAddTag(self):
        newName = self.nameLineEdit.text()
        if not newName:
            self.nameLineEdit.setFocus(Qt.MouseFocusReason)
            return
        else:
            if not MTag.validateExist(newName):
                MTag.inject(name=newName, color=self.backgroundColor.name())
                self.close()
            else:
                QMessageBox.warning(self, 'ERROR', 'Name has already exist.')
                self.nameLineEdit.setFocus(Qt.MouseFocusReason)


class MAZChooseTagDialog(QDialog):
    def __init__(self, parent=None):
        super(MAZChooseTagDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('choose_tag'))
        self.initUI()

    def initUI(self):
        self.newButton = MAddButton()
        self.connect(self.newButton, SIGNAL('clicked()'), self.slotNewTag)
        addLay = QHBoxLayout()
        addLay.addStretch()
        addLay.addWidget(self.newButton)

        self.tagWidget = MAZTagBaseWidget(True)
        self.okButton = QPushButton(self.tr('ok'), self)
        self.connect(self.okButton, SIGNAL('clicked()'), self.close)

        self.cancelButton = QPushButton(self.tr('close'), self)
        self.connect(self.cancelButton, SIGNAL('clicked()'), self.close)

        buttonLay = QHBoxLayout()
        buttonLay.addWidget(self.okButton)
        buttonLay.addWidget(self.cancelButton)

        mainLay = QVBoxLayout()
        mainLay.addWidget(self.tagWidget)
        mainLay.addLayout(addLay)
        mainLay.addLayout(buttonLay)

        self.setLayout(mainLay)

    def setCheckedList(self, checkedIdList):
        self.tagWidget.setTagCheckedList(checkedIdList)

    def getSelectedTagIdList(self):
        return self.tagWidget.getTagCheckedList()

    def closeEvent(self, event):
        self.accept()

    def slotNewTag(self):
        addTagDialog = MAZTagItemDialog(self)
        if addTagDialog.exec_():
            checkedIdList = self.tagWidget.tagListWidget.getCheckedList()
            self.tagWidget.tagListWidget.updateContent()
            self.tagWidget.tagListWidget.setCheckedList(checkedIdList)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    test = MAZChooseTagDialog()
    test.show()
    sys.exit(app.exec_())
