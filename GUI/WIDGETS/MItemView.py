# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.1
# Email : muyanru345@163.com
###################################################################

from functools import partial

from GUI.IMAGES import IMAGE_PATH
from GUI.PLUGINS import MPluginManager
from GUI.PLUGINS.MTableHandle import *
from MItemModel import MTableModel


class MHeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super(MHeaderView, self).__init__(orientation, parent)
        self.setMovable(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint&)'),
                     self.slotContextMenu)
        self.setDefaultAlignment(Qt.AlignLeft)

    @Slot(QPoint)
    def slotContextMenu(self, point):
        contextMenu = QMenu(self)
        tableModel = self.model()
        fitAction = contextMenu.addAction(self.tr('fit_size'))
        fitAction.setCheckable(True)
        fitAction.setChecked(True if self.resizeMode(0) == QHeaderView.ResizeToContents else False)
        self.connect(fitAction, SIGNAL('toggled(bool)'), self.slotSetResizeMode)
        for i in range(self.count()):
            action = contextMenu.addAction(tableModel.headerData(i, Qt.Horizontal, Qt.DisplayRole))
            action.setCheckable(True)
            action.setChecked(not self.isSectionHidden(i))
            self.connect(action, SIGNAL('toggled(bool)'),
                         partial(self.slotSetSectionVisible, i))
        contextMenu.exec_(QCursor.pos() + QPoint(10, 10))

    @Slot(QModelIndex, int)
    def slotSetSectionVisible(self, index, flag):
        self.setSectionHidden(index, not flag)

    @Slot(bool)
    def slotSetResizeMode(self, flag):
        if flag:
            self.resizeSections(QHeaderView.ResizeToContents)
        else:
            self.resizeSections(QHeaderView.Interactive)

    def setClickable(self, flag):
        try:
            QHeaderView.setSectionsClickable(self, flag)
        except:
            QHeaderView.setClickable(self, flag)

    def setMovable(self, flag):
        try:
            QHeaderView.setSectionsMovable(self, flag)
        except:
            QHeaderView.setMovable(self, flag)

    def resizeMode(self, index):
        try:
            QHeaderView.sectionResizeMode(self, index)
        except:
            QHeaderView.resizeMode(self, index)

    def setResizeMode(self, mode):
        try:
            QHeaderView.setResizeMode(self, mode)
        except:
            QHeaderView.setSectionResizeMode(self, mode)


class MListView(QListView):
    def __init__(self, parent=None):
        super(MListView, self).__init__(parent)
        self.parentORM = None
        self.realModel = MTableModel()
        headerList = [
            {'attr': 'name', 'name': 'Name'}
        ]
        self.headerList = headerList
        self.setHeaderList(headerList)
        self.childListView = None
        self.sortFilterModel = QSortFilterProxyModel()
        self.sortFilterModel.setSourceModel(self.realModel)
        self.setModel(self.sortFilterModel)
        self.setModelColumn(0)
        self.setMenu()
        self.setSigSlot()

    def setHeaderList(self, headerList):
        if not headerList: return
        self.realModel.setHeaders(headerList)

    def getSelectedItemsData(self):
        return [self.realModel.getORM(i) for i in self.getSelectedIndexes()]

    def setChildListView(self, widget):
        self.childListView = widget

    @Slot(QPoint)
    def slotContextMenu(self, point):
        cur = QCursor.pos()
        proxyIndex = self.indexAt(point)
        contextMenu = QMenu(self)
        if proxyIndex.isValid():
            realIndex = self.sortFilterModel.mapToSource(proxyIndex)
            dataORM = self.realModel.getORM(realIndex)
            event = '{table}_contextmenu'.format(table=getattr(dataORM, '__tablename__', None))
            for plugin in MPluginManager.loadPlugins(self, event):
                if plugin.validate({'orm': dataORM}):
                    action = contextMenu.addAction(QIcon(IMAGE_PATH + '/' + plugin.icon), plugin.name)
                    self.connect(action, SIGNAL('triggered()'),
                                 partial(plugin.run, {'parentWidget': self, 'orm': dataORM}))
                    if plugin.shortcut is not None:
                        action.setShortcut(QKeySequence(plugin.shortcut))
                    if plugin.needRefresh:
                        self.connect(plugin, SIGNAL('sigRefresh()'), partial(self.slotUpdate, self.parentORM))
        else:
            event = '{table}_empty_contextmenu'.format(table=getattr(self.parentORM, '__tablename__', None))
            for plugin in MPluginManager.loadPlugins(self, event):
                if plugin.validate({'orm': self.parentORM}):
                    action = contextMenu.addAction(QIcon(IMAGE_PATH + '/' + plugin.icon), plugin.name)
                    self.connect(action, SIGNAL('triggered()'),
                                 partial(plugin.run, {'parentWidget': self, 'orm': self.parentORM}))
                    if plugin.shortcut is not None:
                        action.setShortcut(QKeySequence(plugin.shortcut))
                    if plugin.needRefresh:
                        self.connect(plugin, SIGNAL('sigRefresh()'), partial(self.slotUpdate, self.parentORM))
        contextMenu.exec_(cur)

    def _getORMList(self, parentORM):
        return parentORM.sub_atoms.all()

    def _filterORMList(self, ormList):
        return ormList

    @Slot(object)
    def slotUpdate(self, parentORM=None):
        self.parentORM = parentORM
        self.emit(SIGNAL('sigUpdateData(PyObject)'), parentORM)
        ormList = self._getORMList(parentORM)
        if ormList:
            resultList = self._filterORMList(ormList)
            self.realModel.setDataList(resultList)
        else:
            self.clear()

    @Slot(QModelIndex, QModelIndex)
    def slotCurrentItemChanged(self, currentIndex, before):
        self.emit(SIGNAL('sigCurrentChanged(PyObject)'), self.getCurrentItemData())

    @Slot(QItemSelection, QItemSelection)
    def slotSelectedItemChanged(self, currentSelected, before):
        self.emit(SIGNAL('sigSelectedChanged(PyObject)'), self.getSelectedItemsData())

    @Slot(QModelIndex)
    def slotDoubleClicked(self, index):
        realIndex = self.sortFilterModel.mapToSource(index)
        self.emit(SIGNAL('sigDoubleClicked(PyObject)'), self.realModel.getORM(realIndex))

    def getCurrentIndex(self):
        return self.sortFilterModel.mapToSource(self.currentIndex())

    def getSelectedIndexes(self):
        return [self.sortFilterModel.mapToSource(i) for i in self.selectedIndexes()]

    def getCurrentItemData(self):
        return self.realModel.getORM(self.getCurrentIndex())

    def clear(self):
        self.realModel.setDataList([])

    def getAllItemsData(self):
        return self.realModel.dataList[:]

    def setMenu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint&)'),
                     self.slotContextMenu)

    def setSigSlot(self):
        self.connect(self.selectionModel(), SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                     self.slotCurrentItemChanged)
        self.connect(self.selectionModel(), SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                     self.slotSelectedItemChanged)
        self.connect(self, SIGNAL('doubleClicked(QModelIndex)'), self.slotDoubleClicked)
