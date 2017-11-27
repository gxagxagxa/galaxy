#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

from GUI.QT import *
from GUI.WIDGETS.MToolButton import *
from functools import partial


class MFilterEditor(QDialog):
    def __init__(self, parent=None):
        super(MFilterEditor, self).__init__(parent)
        self.setWindowTitle('Filter Editor')
        # self.setStyleSheet('font-family:Microsoft YaHei')
        self.initUI()

    def initUI(self):
        self.filterNameLineEdit = QLineEdit('New Filter')
        filterNameLay = QHBoxLayout()
        filterNameLay.addWidget(QLabel('Filter Name:'))
        filterNameLay.addWidget(self.filterNameLineEdit)

        self.filterGrp = MFilterGroup()

        cancelButton = QPushButton('Cancel')
        self.duplicateButton = QPushButton('Duplicate')
        self.duplicateButton.setVisible(False)
        self.createButton = QPushButton('Create')
        self.updateButton = QPushButton('Update')
        self.updateButton.setVisible(False)
        self.connect(cancelButton, SIGNAL('clicked()'), self.close)
        self.connect(self.duplicateButton, SIGNAL('clicked()'), self.slotDuplicate)
        self.connect(self.createButton, SIGNAL('clicked()'), self.slotCreate)
        self.connect(self.updateButton, SIGNAL('clicked()'), self.slotUpdate)

        buttonLay = QHBoxLayout()
        buttonLay.addWidget(cancelButton)
        buttonLay.addStretch()
        buttonLay.addWidget(self.createButton)

        mainLay = QVBoxLayout()
        mainLay.addLayout(filterNameLay)
        mainLay.addWidget(self.filterGrp)
        mainLay.addLayout(buttonLay)
        self.setLayout(mainLay)

    def initData(self):
        self.createButton.setVisible(False)
        self.duplicateButton.setVisible(True)
        self.updateButton.setVisible(True)

    def slotCreate(self):
        self.accept()

    def slotUpdate(self):
        self.accept()

    def slotDuplicate(self):
        print self.getDataDict()

    def getDataDict(self):
        dataDict = {'name': self.filterNameLineEdit.text(),
                    'mode': self.filterGrp.conditionComboBox.currentText(),
                    'filters': self.filterGrp.filterSet.getFilterDataList()}
        return dataDict


class MFilterGroup(QWidget):
    def __init__(self, parent=None):
        super(MFilterGroup, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.conditionComboBox = QComboBox()
        self.conditionComboBox.addItems(['all', 'any'])
        self.tableComboBox = QComboBox()
        self.tableComboBox.addItems(['DATA', 'ATOM', 'RAW', 'META'])

        titleLay = QHBoxLayout()
        titleLay.addWidget(QLabel('Show '))
        titleLay.addWidget(self.tableComboBox)
        titleLay.addWidget(QLabel(' which match'))
        titleLay.addWidget(self.conditionComboBox)
        titleLay.addWidget(QLabel('of the following conditions:'))
        titleLay.addStretch()

        self.filterSet = MFilterSetWidget()

        mainLay = QVBoxLayout()
        mainLay.setContentsMargins(0, 0, 0, 0)
        mainLay.addLayout(titleLay)
        mainLay.addWidget(self.filterSet)
        self.setLayout(mainLay)


class MFilterSetWidget(QWidget):
    def __init__(self, parent=None):
        super(MFilterSetWidget, self).__init__(parent)
        self.filterItemList = []
        self.initUI()

    def initUI(self):
        self.addButton = MAddButton()
        self.connect(self.addButton, SIGNAL('clicked()'), self.slotAddFilter)
        self.filterLayout = QVBoxLayout()
        self.filterLayout.addStretch()

        mainLay = QVBoxLayout()
        mainLay.addWidget(self.addButton)
        mainLay.addLayout(self.filterLayout)
        self.setLayout(mainLay)

    def reset(self):
        print self.filterItemList

    def slotAddFilter(self):
        newFilter = MFilterItem()
        self.connect(newFilter, SIGNAL('sigRemove()'), self.slotRemoveFilter)
        self.filterLayout.insertWidget(len(self.filterItemList), newFilter)
        self.filterItemList.append(newFilter)

    def slotRemoveFilter(self):
        filterItem = self.sender()
        filterItem.setVisible(False)
        self.filterLayout.removeWidget(filterItem)
        self.filterItemList.remove(filterItem)

    def getFilterDataList(self):
        result = []
        for i in self.filterItemList:
            result.append(i.getDataDict())

        return result


class MFilterItem(QWidget):
    def __init__(self, parent=None):
        super(MFilterItem, self).__init__(parent)
        self.setFixedHeight(20)
        self.initUI()
        self.initData()

    def initUI(self):
        self.checkBox = QCheckBox()
        self.checkBox.setChecked(True)
        self.attrComboBox = QComboBox()
        self.opComboBox = QComboBox()
        self.valueWidget = MValueWidget()
        self.removeButton = QToolButton()
        self.removeButton.setToolTip(self.tr('delete'))
        self.removeButton.setAutoRaise(True)
        self.removeButton.setIcon(QIcon('./images/dustbin.png'))

        self.connect(self.attrComboBox, SIGNAL('currentIndexChanged(int)'), self.slotAttrChanged)
        self.connect(self.opComboBox, SIGNAL('currentIndexChanged(int)'), self.slotOpChanged)
        self.connect(self.removeButton, SIGNAL('clicked()'), self.slotRemove)

        mainLay = QHBoxLayout()
        mainLay.setSpacing(10)
        mainLay.addWidget(self.checkBox)
        mainLay.addWidget(self.attrComboBox)
        mainLay.addWidget(self.opComboBox)
        mainLay.addWidget(self.valueWidget)
        mainLay.addWidget(self.removeButton)
        mainLay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLay)

    def initData(self):
        attrList = [{'name': 'Name', 'type': MValueType.Text},
                    {'name': 'Created By', 'type': MValueType.Entity},
                    {'name': 'Created At', 'type': MValueType.Date},
                    {'name': 'Age', 'type': MValueType.Number}
                    ]
        for attr in attrList:
            self.attrComboBox.addItem(attr.get('name'), attr)

    def slotAttrChanged(self, index):
        itemData = self.attrComboBox.itemData(index)
        self.valueWidget.setType(itemData.get('type'))

    def slotOpChanged(self, index):
        itemData = self.opComboBox.itemData(index)
        print itemData

    def slotRemove(self):
        self.emit(SIGNAL('sigRemove()'))

    def getDataDict(self):
        return {
            'isChecked': self.checkBox.isChecked(),
            'attr': self.attrComboBox.currentText(),
            'op': self.opComboBox.currentText(),
            'value': self.valueWidget.getData()
        }


class MValueType(QObject):
    Date = 0
    Text = 1
    Number = 2
    Entity = 3
    op_is = 0

    def __init__(self, parent=None):
        super(MValueType, self).__init__(parent)

    def getOperators(self, typeId):
        print typeId


class MValueWidget(QWidget):
    def __init__(self, parent=None):
        super(MValueWidget, self).__init__(parent)
        numberValidator = QRegExpValidator(QRegExp("[0-9]+"), self)
        self.dateWidget = QDateEdit(self)
        self.dateWidget.setCalendarPopup(True)
        self.textLineEdit = QLineEdit()
        self.numberLineEdit = QLineEdit()
        self.numberLineEdit.setValidator(numberValidator)
        self.entityLineEdit = QLineEdit()

        self.stackLayout = QStackedLayout()
        self.stackLayout.insertWidget(MValueType.Date, self.dateWidget)
        self.stackLayout.insertWidget(MValueType.Text, self.textLineEdit)
        self.stackLayout.insertWidget(MValueType.Number, self.numberLineEdit)
        self.stackLayout.insertWidget(MValueType.Entity, self.entityLineEdit)

        self.setLayout(self.stackLayout)
        self.setType(MValueType.Text)

    def setType(self, typeId):
        self.stackLayout.setCurrentIndex(typeId)

    def getData(self):
        currentIndex = self.stackLayout.currentIndex()
        if currentIndex == MValueType.Date:
            return self.dateWidget.date()
        elif currentIndex == MValueType.Text:
            return self.textLineEdit.text()
        elif currentIndex == MValueType.Number:
            return self.numberLineEdit.text()
        elif currentIndex == MValueType.Entity:
            return self.entityLineEdit.text()
        else:
            return None


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    test = MFilterEditor()
    test.show()
    sys.exit(app.exec_())
