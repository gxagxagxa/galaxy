# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.1
# Email : muyanru345@163.com
###################################################################

from functools import partial

from MItemModel import MTableModel, MTreeModel
from IMAGES import IMAGE_PATH
from PLUGINS import *
from QT import *

tableViewSettingDict = {
    'reverse': False,
    'menu': False,
    'grid': False,
    'selectionBehavior': QAbstractItemView.SelectRows,
    'selectionMode': QAbstractItemView.SingleSelection
}
treeViewSettingDict = {
    'reverse': False,
    'menu': False,
    'grid': False,
    'selectionBehavior': QAbstractItemView.SelectRows,
    'selectionMode': QAbstractItemView.SingleSelection
}
tableViewHeaderListExample = [
    {'attr': 'label', 'name': 'Version Name', 'width': 150, 'is_filter': False},
]

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


@Slot(QPoint)
def _slotContextMenu(self, point):
    row = self.rowAt(point.y())
    if row >= 0:
        dataORM = self.realModel.dataList[row]
        tableName = getattr(dataORM, '__tablename__') if hasattr(dataORM, '__tablename__') else dataORM.get('type').lower()
        event = '{table}-contextmenu'.format(table=tableName)
        contextMenu = QMenu(self)
        # for plugin in MPluginManager.loadPlugins(self, event):
        #     action = contextMenu.addAction(QIcon(IMAGE_PATH + '/' + plugin.icon),
        #                                    plugin.name) if plugin.icon else contextMenu.addAction(plugin.name)
        #     self.connect(action, SIGNAL('triggered()'),
        #                  partial(plugin.run, self, dataORM))
        #     if plugin.needRefresh:
        #         self.connect(plugin, SIGNAL('sigRefresh()'), self.slotUpdate)
        contextMenu.exec_(QCursor.pos())


def _setFilter(self, filter):
    self._filter = filter


def _setTable(self, table):
    self._orm_handle = getattr(MTableHandle, 'MLocal' + table)
    # self._orm_handle = globals()['MLocal' + table]


def _setCurrentUserOnly(self, flag):
    self._onlyCurrentUser = flag


def _getORMList(self, orm):
    return self._orm_handle.getORMListFromParent(orm, onlyUser=self._onlyCurrentUser)


def _filterORMList(self, ormList):
    if self._filter:
        if self._filter['operator'] == 'in':
            ormList = [orm for orm in ormList if
                       getattr(orm, self._filter['attr'], None) in self._filter['values']]
        elif self._filter['operator'] == 'not_in':
            ormList = [orm for orm in ormList if
                       getattr(orm, self._filter['attr'], None) not in self._filter['values']]
        elif self._filter['operator'] == 'startswith':
            ormList = [orm for orm in ormList if
                       getattr(orm, self._filter['attr'], None).startswith(tuple(self._filter['values']))]
    if self.settingDict.get('reverse', None):
        ormList.reverse()
    return ormList


@Slot(object)
def _slotUpdate(self, parentORM=None):
    self.emit(SIGNAL('sigUpdateData(PyObject)'), parentORM)
    ormList = self._getORMList(parentORM)
    if ormList:
        resultList = self._filterORMList(ormList)
        self.realModel.setDataList(resultList)
    else:
        self.clear()


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


def _setMenu(self):
    self.setContextMenuPolicy(Qt.CustomContextMenu)
    self.connect(self, SIGNAL('customContextMenuRequested(const QPoint&)'),
                 self.slotContextMenu)


def _setSigSlot(self):
    self.connect(self.selectionModel(), SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                 self.slotCurrentItemChanged)
    self.connect(self.selectionModel(), SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                 self.slotSelectedItemChanged)
    self.connect(self, SIGNAL('doubleClicked(QModelIndex)'), self.slotDoubleClicked)


def _resizeHeaders(self, headerList):
    if not headerList: return
    for index, i in enumerate(headerList):
        self._headerView.setSectionHidden(index, not i.get('default_show', True))
        self._headerView.resizeSection(index, i.get('width', 100))


class MTreeView(QTreeView):
    slotCurrentItemChanged = _slotCurrentItemChanged
    slotSelectedItemChanged = _slotSelectedItemChanged
    slotDoubleClicked = _slotDoubleClicked
    # getCurrentIndex = _getCurrentIndex
    # getSelectedIndexes = _getSelectedIndexes
    getCurrentItemData = _getCurrentItemData
    getAllItemsData = _getAllItemsData
    clear = _clear
    setMenu = _setMenu
    setSigSlot = _setSigSlot
    resizeHeaders = _resizeHeaders

    def __init__(self, headerList, settingDict=treeViewSettingDict, parent=None):
        super(MTreeView, self).__init__(parent)
        self.settingDict = settingDict
        self.headerList = headerList
        self.realModel = MTreeModel()
        self.realModel.setHeaders(headerList)
        self._headerView = MHeaderView(Qt.Horizontal)
        self.setHeader(self._headerView)

        self.setModel(self.realModel)
        self.resizeHeaders(headerList)

        self.setSelectionBehavior(self.settingDict.get('selectionBehavior', QAbstractItemView.SelectRows))
        self.setSelectionMode(self.settingDict.get('selectionMode', QAbstractItemView.SingleSelection))

        if self.settingDict.get('menu', False): self.setMenu()
        self.connect(self, SIGNAL('doubleClicked(QModelIndex)'), self.slotDoubleClicked)
        self.setSigSlot()

    def getSelectedItemsData(self):
        ormList = [self.realModel.getORM(i) for i in self.getSelectedIndexes() if
                   not isinstance(self.realModel.getORM(i), dict)]
        result = set(ormList)
        return list(result)

    def getCurrentIndex(self):
        return self.currentIndex()

    def getSelectedIndexes(self):
        return self.selectedIndexes()


class MTableView(QTableView):
    _filter = None
    # _orm_handle = MTableHandle.MLocalTable
    slotContextMenu = _slotContextMenu
    setFilter = _setFilter
    setTable = _setTable
    setCurrentUserOnly = _setCurrentUserOnly
    _getORMList = _getORMList
    _filterORMList = _filterORMList
    slotUpdate = _slotUpdate
    slotCurrentItemChanged = _slotCurrentItemChanged
    slotSelectedItemChanged = _slotSelectedItemChanged
    slotDoubleClicked = _slotDoubleClicked
    getCurrentIndex = _getCurrentIndex
    getSelectedIndexes = _getSelectedIndexes
    clear = _clear
    getAllItemsData = _getAllItemsData
    getCurrentItemData = _getCurrentItemData
    setMenu = _setMenu
    setSigSlot = _setSigSlot
    resetHeaders = _resizeHeaders
    _onlyCurrentUser = False

    def __init__(self, headerList=None, settingDict=tableViewSettingDict, parent=None):
        super(MTableView, self).__init__(parent)
        self.settingDict = settingDict
        self.realModel = MTableModel()
        self.realModel.setHeaders(headerList)
        self.headerList = headerList
        self._headerView = MHeaderView(Qt.Horizontal)
        self.setHorizontalHeader(self._headerView)
        self.setShowGrid(self.settingDict.get('grid', False))
        self._headerView.setClickable(True)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(self.settingDict.get('selectionBehavior', QAbstractItemView.SelectRows))
        self.setSelectionMode(self.settingDict.get('selectionMode', QAbstractItemView.SingleSelection))

        self.sortFilterModel = QSortFilterProxyModel()
        self.sortFilterModel.setSourceModel(self.realModel)
        self.sortFilterModel.setDynamicSortFilter(True)
        self.sortFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setModel(self.sortFilterModel)
        self.resetHeaders(headerList)
        if self.settingDict.get('menu', False): self.setMenu()
        self.setSigSlot()

    def getSelectedItemsData(self):
        ormList = [self.realModel.getORM(i) for i in self.getSelectedIndexes()]
        # result = set(ormList)
        # return list(result)
        return ormList


listViewSettingDict = {
    'reverse': False,
    'filterable': False,
    'menu': False,
    'selectionBehavior': QAbstractItemView.SelectRows,
    'selectionMode': QAbstractItemView.SingleSelection,
    'displayAttr': 'name'
}
listViewHeaderListExample = [
    {'attr': 'name', 'name': 'Name'}
]


class MListView(QListView):
    _filter = None
    # _orm_handle = MTableHandle.MLocalTable
    _onlyCurrentUser = False
    slotContextMenu = _slotContextMenu
    setFilter = _setFilter
    setTable = _setTable
    setCurrentUserOnly = _setCurrentUserOnly
    _getORMList = _getORMList
    _filterORMList = _filterORMList
    slotUpdate = _slotUpdate
    slotCurrentItemChanged = _slotCurrentItemChanged
    slotSelectedItemChanged = _slotSelectedItemChanged
    slotDoubleClicked = _slotDoubleClicked
    getCurrentIndex = _getCurrentIndex
    getSelectedIndexes = _getSelectedIndexes
    clear = _clear
    getAllItemsData = _getAllItemsData
    getCurrentItemData = _getCurrentItemData
    setMenu = _setMenu
    setSigSlot = _setSigSlot

    def __init__(self, headerList=listViewHeaderListExample, settingDict=listViewSettingDict, parent=None):
        super(MListView, self).__init__(parent)
        self.settingDict = settingDict
        self.realModel = MTableModel()
        self.headerList = headerList
        self.childListView = None
        self.setHeaderList(headerList)
        self.sortFilterModel = QSortFilterProxyModel()
        self.sortFilterModel.setSourceModel(self.realModel)
        self.setModel(self.sortFilterModel)
        self.setModelColumn(0)

        self.setSelectionBehavior(self.settingDict.get('selectionBehavior', QAbstractItemView.SelectRows))
        self.setSelectionMode(self.settingDict.get('selectionMode', QAbstractItemView.SingleSelection))

        if self.settingDict.get('menu', False): self.setMenu()
        self.setSigSlot()

    def setHeaderList(self, headerList):
        if not headerList: return
        self.realModel.setHeaders(headerList)

    def getSelectedItemsData(self):
        return [self.realModel.getORM(i) for i in self.getSelectedIndexes()]

    def setChildListView(self, widget):
        self.childListView = widget