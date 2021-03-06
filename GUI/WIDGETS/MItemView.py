# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.1
# Email : muyanru345@163.com
###################################################################

from functools import partial
import sys
import subprocess

from GUI.IMAGES import IMAGE_PATH
from GUI.PLUGINS import MPluginManager
from GUI.PLUGINS.MTableHandle import *
from MItemModel import MTableModel
from CORE.DB_UTIL import *


@Slot(QModelIndex, QModelIndex)
def _slotCurrentItemChanged(self, currentIndex, before):
    self.emit(SIGNAL('sigCurrentChanged(PyObject)'), self.getCurrentItemData())


@Slot(QItemSelection, QItemSelection)
def _slotSelectedItemChanged(self, currentSelected, before):
    self.emit(SIGNAL('sigSelectedChanged(PyObject)'), self.getSelectedItemsData())


@Slot(QModelIndex)
def _slotDoubleClicked(self, index):
    realIndex = self.sortFilterModel.mapToSource(index)
    self.emit(SIGNAL('sigDoubleClicked(PyObject)'), self.realModel.getORM(realIndex))


def _getCurrentIndex(self):
    return self.sortFilterModel.mapToSource(self.currentIndex())


def _getSelectedIndexes(self):
    return [self.sortFilterModel.mapToSource(i) for i in self.selectedIndexes()]


def _getCurrentItemData(self):
    return self.realModel.getORM(self.getCurrentIndex())


def _clear(self):
    self.realModel.setDataList([])


def _getAllItemsData(self):
    return self.realModel.dataList[:]


@Slot(QPoint)
def _slotContextMenu(self, point):
    if self.parentORM is None:
        return
    cur = QCursor.pos()
    proxyIndex = self.indexAt(point)
    contextMenu = QMenu(self)
    if proxyIndex.isValid():
        dataORMList = self.getSelectedItemsData()
        for plugin in MPluginManager.loadPlugins(self, 'itemview_contextmenu'):
            event = {'parentWidget': self, 'orm': dataORMList}
            if plugin.validate(event):
                action = contextMenu.addAction(QIcon(IMAGE_PATH + '/' + plugin.icon), plugin.name)
                self.connect(action, SIGNAL('triggered()'), partial(plugin.run, event))
                if plugin.shortcut is not None:
                    action.setShortcut(QKeySequence(plugin.shortcut))
                if plugin.needRefresh:
                    self.connect(plugin, SIGNAL('sigRefresh()'), partial(self.slotUpdate, self.parentORM))
    else:
        for plugin in MPluginManager.loadPlugins(self, 'itemview_empty_contextmenu'):
            event = {'parentWidget': self, 'orm': self.parentORM}
            if plugin.validate(event):
                action = contextMenu.addAction(QIcon(IMAGE_PATH + '/' + plugin.icon), plugin.name)
                self.connect(action, SIGNAL('triggered()'), partial(plugin.run, event))
                if plugin.shortcut is not None:
                    action.setShortcut(QKeySequence(plugin.shortcut))
                if plugin.needRefresh:
                    self.connect(plugin, SIGNAL('sigRefresh()'), partial(self.slotUpdate, self.parentORM))
    contextMenu.exec_(cur)


def _getSelectedItemsData(self):
    return [self.realModel.getORM(i) for i in self.getSelectedIndexes()]


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


class MTableView(QTableView):
    slotCurrentItemChanged = _slotCurrentItemChanged
    slotSelectedItemChanged = _slotSelectedItemChanged
    slotDoubleClicked = _slotDoubleClicked
    getCurrentIndex = _getCurrentIndex
    getSelectedIndexes = _getSelectedIndexes
    getSelectedItemsData = _getSelectedItemsData
    getCurrentItemData = _getCurrentItemData
    clear = _clear
    getAllItemsData = _getAllItemsData
    slotContextMenu = _slotContextMenu

    def __init__(self, headerList, parent=None):
        super(MTableView, self).__init__(parent)
        self.parentORM = None
        self.realModel = MTableModel()
        # headerList = [
        #     {'attr': 'name', 'name': 'Name'}
        # ]
        self.headerList = headerList
        self.setHeaderList(headerList)
        self._headerView = MHeaderView(Qt.Horizontal)
        self.setHorizontalHeader(self._headerView)
        # self.setShowGrid(self.settingDict.get('grid', False))
        self._headerView.setClickable(True)
        self.childListView = None
        self.parentListView = None
        self.sortFilterModel = QSortFilterProxyModel()
        self.sortFilterModel.setSourceModel(self.realModel)
        self.setModel(self.sortFilterModel)
        self.setMenu()
        self.setSigSlot()
        self.resizeHeaders(headerList)

    def setHeaderList(self, headerList):
        if not headerList:
            return
        self.realModel.setHeaders(headerList)

    def resizeHeaders(self, headerList):
        if not headerList:
            return
        for index, i in enumerate(headerList):
            self._headerView.setSectionHidden(index, not i.get('default_show', True))
            self._headerView.resizeSection(index, i.get('width', 100))

    def _getORMList(self, parentORM):
        return DB_UTIL.traverse(parentORM)

    def _filterORMList(self, ormList):
        return ormList

    @Slot(object)
    def slotUpdate(self, parentORM=None):
        self.parentORM = parentORM
        self.emit(SIGNAL('sigUpdateData(PyObject)'), parentORM)
        ormList = self._getORMList(parentORM)
        if ormList:
            resultList = self._filterORMList(list(ormList))
            self.realModel.setDataList(resultList)
        else:
            self.clear()

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


listViewSettingDict = {
    'reverse'          : False,
    'filterable'       : False,
    'menu'             : False,
    'selectionBehavior': QAbstractItemView.SelectRows,
    'selectionMode'    : QAbstractItemView.ContiguousSelection,
    'displayAttr'      : 'name'
}


class MListView(QListView):
    slotCurrentItemChanged = _slotCurrentItemChanged
    slotSelectedItemChanged = _slotSelectedItemChanged
    slotDoubleClicked = _slotDoubleClicked
    getCurrentIndex = _getCurrentIndex
    getSelectedIndexes = _getSelectedIndexes
    getSelectedItemsData = _getSelectedItemsData
    getCurrentItemData = _getCurrentItemData
    clear = _clear
    getAllItemsData = _getAllItemsData
    slotContextMenu = _slotContextMenu

    def __init__(self, headerList=None, parent=None):
        super(MListView, self).__init__(parent)
        self.parentORM = None
        self.realModel = MTableModel()

        if headerList is None:
            headerList = [
                {'attr': 'name', 'name': 'Name'}
            ]
        self.headerList = headerList
        self.setHeaderList(headerList)
        self.childListView = None
        self.parentListView = None
        self.sortFilterModel = QSortFilterProxyModel()
        self.sortFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.sortFilterModel.setSourceModel(self.realModel)
        self.setModel(self.sortFilterModel)
        self.setModelColumn(0)
        self.setMenu()
        self.setSigSlot()
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def setHeaderList(self, headerList):
        if not headerList:
            return
        self.realModel.setHeaders(headerList)

    def minimumSizeHint(self):
        return QSize(200, 50)

    def setChildListView(self, widget):
        self.childListView = widget

    def setParentListView(self, widget):
        self.parentListView = widget

    def _getORMList(self, parentORM):
        return DB_UTIL.traverse(parentORM)

    def _filterORMList(self, ormList):
        return ormList

    @Slot(object)
    def slotUpdate(self, parentORM=None):
        self.parentORM = parentORM
        self.emit(SIGNAL('sigUpdateData(PyObject)'), parentORM)
        ormList = self._getORMList(parentORM)
        if ormList:
            resultList = self._filterORMList(list(ormList))
            self.realModel.setDataList(resultList)
        else:
            self.clear()

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

    def focusInEvent(self, event):
        self.emit(SIGNAL('sigGetFocus(PyObject)'), self.parentORM)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        fileList = [url.toLocalFile() for url in event.mimeData().urls()]
        result = []
        if sys.platform == 'darwin':
            for url in fileList:
                p = subprocess.Popen(
                    'osascript -e \'get posix path of posix file \"file://{}\" -- kthxbai\''.format(url),
                    stdout=subprocess.PIPE,
                    shell=True)
                # print p.communicate()[0].strip()
                result.append(p.communicate()[0].strip())
                p.wait()
        else:
            result = fileList

        self.emit(SIGNAL('sigDropFile(PyObject)'), result)

    def setCurrentItemData(self, orm):
        for row, dataORM in enumerate(self.realModel.dataList):
            if dataORM.sid == orm.sid:
                return self.setCurrentIndex(self.sortFilterModel.mapFromSource(self.realModel.index(row, 0)))
