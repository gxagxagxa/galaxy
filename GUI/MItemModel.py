# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2016.12
# Email : muyanru345@163.com
###################################################################

import datetime

from CORE import *
from IMAGES import IMAGE_PATH
from QT import *

TEXT_COLOR = '#c8c8c8'
BACKGROUND_COLOR = '#323232'
ODD_ROW_COLOR = '#3a3a3a'
EVEN_ROW_COLOR = '#353535'
ICON_DICT = {}


def getValue(obj, attr):
    if isinstance(obj, dict):
        value = obj.get(attr, None)
        if isinstance(value, dict):
            return value.get('name').decode('utf-8') if value.has_key('name') else value.get('code', None)
        elif isinstance(value, list):
            result = []
            for i in value:
                if isinstance(i, dict):
                    result.append(i.get('name').decode('utf-8') if i.has_key('name') else i.get('code', None))
                else:
                    result.append(str(i) if not isinstance(i, basestring) else i.decode('utf-8'))
            return  ','.join(result)
        else:
            return value if not isinstance(value, basestring) else value.decode('utf-8')
    else:
        return getattr(obj, attr, None)


def _setDataList(self, dataList):
    self.beginResetModel()
    self.dataList = dataList
    self.endResetModel()


def _headerData(self, section, orientation, role=Qt.DisplayRole):
    if not self.headerList or section >= len(self.headerList):
        return None
    if orientation != Qt.Horizontal:
        return None
    if role == Qt.DisplayRole:
        return self.headerList[section]['name']
    if role == Qt.UserRole:
        return self.headerList[section]['default_show']
    return None


def _sort(self, column, order):
    self._sortColumn = column
    if order == Qt.AscendingOrder:
        self.setDataList(sorted(self.dataList, self.sortAscendingFunc))
    elif order == Qt.DescendingOrder:
        self.setDataList(sorted(self.dataList, self.sortDescendingFunc))


def sortAscendingFunc(self, ormX, ormY):
    valX = getattr(ormX, self.headerList[self._sortColum].get('attr'))
    valY = getattr(ormY, self.headerList[self._sortColum].get('attr'))
    if valX > valY:
        return -1
    if valX < valY:
        return 1
    return 0


def sortDescendingFunc(self, ormX, ormY):
    valX = getattr(ormX, self.headerList[self._sortColum].get('attr'))
    valY = getattr(ormY, self.headerList[self._sortColum].get('attr'))
    if valX > valY:
        return 1
    if valX < valY:
        return -1
    return 0


def _setHeaders(self, headerDictList):
    self.headerList = headerDictList
    self.statusColumn = -1
    for index, dataDict in enumerate(self.headerList):
        if dataDict.get('attr', '') == 'sg_status_list':
            self.statusColumn = index


def _rowCount(self, index=QModelIndex()):
    return len(self.dataList)


def _columnCount(self, index=QModelIndex()):
    return len(self.headerList)


def _findSameName(self, name):
    for index, data in enumerate(self.dataList):
        if getValue(data, 'name') == name:
            return index
    return -1


def _getORM(self, index):
    return self.dataList[index.row()]


def _currentData(self, index):
    keyName = self.headerList[index.column()]['attr']
    result = getValue(self.dataList[index.row()], keyName)
    if keyName in ['sg_ot', 'duration', 'sg_plan_day', 'time_logs_sum']:
        return '%.1f hrs' % (result / 60.0) if result else '--'
    if isinstance(result, datetime.datetime):
        return result.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(result, bool):
        result = 'Need' if result else 'OK'
    return result if result is not None else '--'


def _data(self, index, role=Qt.DisplayRole):
    if not index.isValid():
        return None
    # 特别处理 shotgun 的 sg_status_list
    if index.column() == self.statusColumn:
        if role == Qt.DisplayRole: return self.currentData(index)
        if role == Qt.TextAlignmentRole: return Qt.AlignCenter
        if role == Qt.DecorationRole:
            keyName = self.currentData(index)
            if not keyName: return None
            if not ICON_DICT.has_key(keyName):
                ICON_DICT[keyName] = QIcon('%s/status/%s.png' % (IMAGE_PATH, keyName))
            return ICON_DICT.get(keyName)

    # 其他情况
    if role == Qt.DisplayRole:
        return self.currentData(index)
    if role == Qt.EditRole:
        return self.currentData(index)
    if role == Qt.UserRole:
        return self.getORM(index)
    if role == Qt.ForegroundRole:
        return QBrush(QColor(TEXT_COLOR))
    if role == Qt.BackgroundRole:
        if self.headerList[index.column()].get('isColored', False):
            return QBrush(
                QColor(self.headerList[index.column()].get('colorDict', {}).get(self.currentData(index), Qt.gray)))
        elif self.backgroundColorAttr:
            dataORM = self.getORM(index)
            isNew = getattr(dataORM, 'is_new')
            return QBrush(
                QColor(self.backgroundColorAttr.get('colorDict', {}).get(isNew, Qt.gray)))
        if index.row() % 2 == 0:
            return QBrush(QColor(EVEN_ROW_COLOR))
        else:
            return QBrush(QColor(ODD_ROW_COLOR))

    if role == Qt.DecorationRole:
        if index.column() == 0:
            try:
                dataORM = self.getORM(index)
                if self.supportThumbnail:
                    thumbnailORM = dataORM.thumbnail if hasattr(dataORM, 'thumbnail') else dataORM['thumbnail']
                    if thumbnailORM:
                        keyName = thumbnailORM.name
                        if ICON_DICT.has_key(keyName):
                            return ICON_DICT[keyName]
                        else:
                            pic = thumbnailORM.thumbnail_full_path
                            if pic.exists():
                                ICON_DICT[keyName] = QIcon(pic)
                                return ICON_DICT[keyName]
                    if not ICON_DICT.has_key('default'):
                        ICON_DICT['default'] = QIcon('%s/default.png' % (IMAGE_PATH))
                    return ICON_DICT['default']
                else:
                    keyName = getattr(dataORM, '__tablename__') if hasattr(dataORM, '__tablename__') else dataORM.get(
                        'type')
                    if not ICON_DICT.has_key(keyName):
                        ICON_DICT[keyName] = QIcon('%s/icon-%s.png' % (IMAGE_PATH, keyName))
                    return ICON_DICT.get(keyName)
            except:
                return None

    if role == Qt.ToolTipRole:
        return self.currentData(index)
    return None


def _setData(self, index, value, role=Qt.EditRole):
    if role != Qt.EditRole:
        return False

    if index.isValid() and 0 <= index.row() < len(self.dataList):
        keyName = self.headerList[index.column()]['attr']
        self.dataList[index.row()][keyName] = value
        self.dataChanged.emit(index, index)
        return True

    return False


def _clear(self):
    self.setDataList([])


class MTableModel(QAbstractTableModel):
    # sort = _sort
    headerData = _headerData
    setHeaders = _setHeaders
    rowCount = _rowCount
    columnCount = _columnCount
    findSameName = _findSameName
    getORM = _getORM
    currentData = _currentData
    data = _data
    setData = _setData
    setDataList = _setDataList
    clear = _clear

    def __init__(self, parent=None):
        super(MTableModel, self).__init__(parent)
        self.dataList = []
        self.headerList = []
        self.supportThumbnail = False
        self.backgroundColorAttr = None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if self.headerList[index.column()].get('isEditable', False):
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))


class MTreeItem(object):
    def __init__(self, orm, parent=None):
        self.parentItem = parent
        self.itemORM = orm
        self.isDict = isinstance(self.itemORM, dict)
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def data(self, keyName):
        try:
            if self.isDict:
                return self.itemORM.get(keyName, None)
            else:
                result = getattr(self.itemORM, keyName, None)
                return result
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class MTreeModel(QAbstractItemModel):
    headerData = _headerData
    data = _data
    setHeaders = _setHeaders
    columnCount = _columnCount

    def __init__(self, parent=None):
        super(MTreeModel, self).__init__(parent)
        self.headerList = []
        self.hierarchy = []
        self.rootItem = MTreeItem(self.headerList)

    def getORM(self, index):
        return index.internalPointer().itemORM

    def currentData(self, index):
        item = index.internalPointer()
        keyName = self.headerList[index.column()]['attr']
        result = item.data(keyName)
        if isinstance(result, datetime.datetime):
            return result.strftime('%Y-%m-%d %H:%M:%S')
        return result if result is not None else '--'

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if self.headerList[index.column()].get('isEditable', False):
            return Qt.ItemFlags(QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(QAbstractItemModel.flags(self, index))

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row():
            keyName = self.headerList[index.column()]['attr']
            orm = self.getORM(index)
            if isinstance(orm, dict):
                orm[keyName] = value
            else:
                setattr(orm, keyName, value)
            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
            return True

        return False

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setDataList(self, resourceORMList):
        self.beginResetModel()
        if self.rootItem:
            del self.rootItem
        self.rootItem = MTreeItem(self.headerList)
        self.elementORMs = [orm for orm in resourceORMList if orm.type_group_name == 'element']
        self.cacheORMs = [orm for orm in resourceORMList if orm.type_group_name == 'cache']
        self.nkTemplateORMs = [orm for orm in resourceORMList if orm.type_group_name == 'template']

        elementItem = MTreeItem({'name': 'Elements', 'count': len(self.elementORMs)}, self.rootItem)
        self.rootItem.appendChild(elementItem)
        self.addResourceORMItems(self.elementORMs, elementItem)
        cacheItem = MTreeItem({'name': 'Caches', 'count': len(self.cacheORMs)}, self.rootItem)
        self.rootItem.appendChild(cacheItem)
        self.addResourceORMItems(self.cacheORMs, cacheItem)
        nkTemplateItem = MTreeItem({'name': 'NK Templates', 'count': len(self.nkTemplateORMs)}, self.rootItem)
        self.rootItem.appendChild(nkTemplateItem)
        self.addResourceORMItems(self.nkTemplateORMs, nkTemplateItem)
        self.endResetModel()

    def addResourceORMItems(self, ormList, parentItem):
        packages = {}
        for resourceORM in ormList:
            resourcePackageORMs = resourceORM.packages
            if resourcePackageORMs:
                for packageORM in resourcePackageORMs:
                    if packageORM.id in packages.keys():
                        packageORM, packageItem = packages.get(packageORM.id)
                        packageItem.appendChild(MTreeItem(resourceORM, packageItem))
                    else:
                        newPackageItem = MTreeItem(packageORM, parentItem)
                        parentItem.appendChild(newPackageItem)
                        packages[packageORM.id] = (packageORM, newPackageItem)
                        newPackageItem.appendChild(MTreeItem(resourceORM, newPackageItem))
            else:
                parentItem.appendChild(MTreeItem(resourceORM, parentItem))
