# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

from functools import partial

from CORE.DB_UTIL import *
from DECO import MY_CSS
from GUI.WIDGETS.MToolButton import *
from IMAGES import IMAGE_PATH
from WIDGETS.MItemView import MListView
from WIDGETS.MFilterEditor import MFilterEditor
from WIDGETS.MInjectDataDialog import MInjectDataDialog

class MDetailWidget(QWidget):
    def __init__(self, parent=None):
        super(MDetailWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.pixmap = QPixmap()
        self.attrLabel = QLabel()
        self.attrLabel.setAlignment(Qt.AlignCenter)

        mainLay = QVBoxLayout()
        mainLay.addWidget(self.imageLabel)
        mainLay.addWidget(self.attrLabel)

        self.setLayout(mainLay)

    def initData(self, orm):
        thumbnailImage = orm.thumbnail
        if thumbnailImage.height():
            self.pixmap.fromImage(thumbnailImage)
        else:
            keyName = getattr(orm, '__tablename__')
            if keyName == 'link': keyName = '%slink' % orm.target_table
            self.pixmap = QPixmap('%s/icon-%s.png' % (IMAGE_PATH, keyName))
        self.imageLabel.setPixmap(self.pixmap)
        context = 'Data Link\n\n\n{}'.format(orm.target) if isinstance(orm, LINK) else str(orm)
        self.attrLabel.setText(context)


class MLeftWidget(QWidget):
    def __init__(self, parent=None):
        super(MLeftWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        lab1 = QLabel(u'个人收藏')
        lab2 = QLabel(u'共享的')
        lab3 = QLabel(u'标记')

        self.favoriteListButton = []
        self.sharedListButton = []
        self.tagsListButton = []

        mainLay = QVBoxLayout()
        mainLay.addWidget(lab1)
        for i in range(5):
            button = QPushButton('My Filter %d' % (i + 1))
            self.connect(button, SIGNAL('clicked()'), partial(self.slotFavorite, i + 1))
            self.favoriteListButton.append(button)
            mainLay.addWidget(button)

        addFilterButton = QPushButton('+ Filter...')
        self.connect(addFilterButton, SIGNAL('clicked()'), self.slotAddFilter)
        mainLay.addWidget(addFilterButton)
        mainLay.addSpacing(10)
        mainLay.addWidget(lab2)
        for i in range(5):
            button = QPushButton('Share %d' % (i + 1))
            self.connect(button, SIGNAL('clicked()'), partial(self.slotShare, i + 1))
            self.sharedListButton.append(button)
            mainLay.addWidget(button)
        mainLay.addSpacing(10)
        mainLay.addWidget(lab3)
        for i in range(5):
            button = QPushButton('Tag %d' % (i + 1))
            self.connect(button, SIGNAL('clicked()'), partial(self.slotTag, i + 1))
            self.tagsListButton.append(button)
            mainLay.addWidget(button)

        mainLay.addStretch()
        self.setLayout(mainLay)

    @Slot(int)
    def slotFavorite(self, index):
        print 'slotFavorite', index

    @Slot(int)
    def slotShare(self, index):
        print 'slotShare', index

    @Slot(int)
    def slotTag(self, index):
        print 'slotTag', index

    def slotAddFilter(self):
        dialog = MFilterEditor(self)
        # dialog.setWindowFlags(Qt.Dialog)
        if dialog.exec_():
            print dialog.getDataDict()


class MMultiListViewWidget(QWidget):
    def __init__(self, parent=None):
        super(MMultiListViewWidget, self).__init__(parent)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.connect(self.scrollArea.horizontalScrollBar(), SIGNAL('rangeChanged(int, int)'), self.slotScroll2Right)
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.listViewList = []
        self.rootListView = MListView()
        self.detailWidget = MDetailWidget()
        self.detailWidget.setVisible(False)

        self.connect(self.rootListView, SIGNAL('sigSelectedChanged(PyObject)'), partial(self.slotCurrentChanged, self.rootListView))
        self.connect(self.rootListView, SIGNAL('sigGoTo(object)'), self.slotGoTo)
        self.splitter.addWidget(self.rootListView)
        self.splitter.addWidget(self.detailWidget)
        self.scrollArea.setWidget(self.splitter)
        mainLay = QVBoxLayout()
        mainLay.addWidget(self.scrollArea)
        self.setLayout(mainLay)

        self.rootListView.slotUpdate(DB_UTIL.get_root())

    def slotScroll2Right(self, a, b):
        self.scrollArea.horizontalScrollBar().setValue(b)

    def slotGoTo(self, targetORM):
        #TODO: go to path
        print 'slotGoTo', DB_UTIL.hierarchy(targetORM, posix=True)

    @Slot(MListView, object)
    def slotCurrentChanged(self, parentListView, parentORMs):
        parentORM = parentORMs
        if isinstance(parentORMs, list) and len(parentORMs)>=1:
            parentORM = parentORMs[0]

        if isinstance(parentORM, LINK):
            if parentORM.target_table == 'atom':
                self.handleAtom(parentListView, parentORM)
            else:
                self.handleData(parentListView, parentORM)
        elif isinstance(parentORM, ATOM):
            self.handleAtom(parentListView, parentORM)
        elif isinstance(parentORM, DATA):
            self.handleData(parentListView, parentORM)
        self.emit(SIGNAL('sigPathChanged(QString)'), DB_UTIL.hierarchy(parentORM, posix=True))

    def handleAtom(self, parentListView, parentORM):
        currentIndex = self.splitter.indexOf(parentListView)
        for i in range(self.splitter.count()):
            if i > currentIndex:
                self.splitter.widget(i).setVisible(True)
        self.detailWidget.setVisible(False)
        self.addNewListView(parentListView, parentORM)

    def handleData(self, parentListView, parentORM):
        currentIndex = self.splitter.indexOf(parentListView)
        for i in range(self.splitter.count()):
            if i > currentIndex:
                self.splitter.widget(i).setVisible(False)
        self.splitter.insertWidget(currentIndex + 1, self.detailWidget)
        self.detailWidget.initData(parentORM)
        self.detailWidget.setVisible(True)

    def addNewListView(self, parentListView, parentORM):
        newListView = parentListView.childListView
        if not newListView:
            newListView = MListView()
            self.connect(newListView, SIGNAL('sigSelectedChanged(PyObject)'), partial(self.slotCurrentChanged, newListView))
            self.connect(newListView, SIGNAL('sigGoTo(PyObject)'), self.slotGoTo)
            self.connect(newListView, SIGNAL('sigGetFocus(PyObject)'), self.slotGetFocus)
            self.connect(newListView, SIGNAL('sigDropFile(PyObject)'), partial(self.slotShowInjectDataDialog, newListView))

            parentListView.setChildListView(newListView)
            newListView.setParentListView(parentListView)
            self.listViewList.append(newListView)
            self.splitter.addWidget(newListView)
        else:
            self.clearDownstreamListView(newListView)
        newListView.slotUpdate(parentORM)

    @Slot(object)
    def slotGetFocus(self, orm):
        self.emit(SIGNAL('sigPathChanged(QString)'), DB_UTIL.hierarchy(orm, posix=True))

    @Slot(list)
    def slotShowInjectDataDialog(self, listView, fileList):
        dialog = MInjectDataDialog(listView.parentORM, self)
        dialog.slotAddFiles(fileList)
        dialog.show()

    def clearDownstreamListView(self, startListView):
        child = startListView.childListView
        if child:
            child.clear()
            self.clearDownstreamListView(child)

    def currentListView(self):
        listView = QApplication.focusWidget()
        if isinstance(listView, MListView):
            return listView
        else:
            for i in range(len(self.listViewList)-1, -1, -1):
                tempView = self.listViewList[i]
                if tempView.getAllItemsData():
                    return tempView
        return None
        # for i in range(self.splitter.count()):
        #     listView = self.splitter.widget(i)
        #     if listView.hasFocus():
        #         if listView.getAllItemsData():
        #             return listView
        #         else:
        #             return listView.parentListView


class MBigPictureViewWidget(QWidget):
    def __init__(self, parent=None):
        super(MBigPictureViewWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.listView = MListView()
        self.listView.setViewMode(QListView.IconMode)
        self.listView.setResizeMode(QListView.Adjust)
        self.listView.setUniformItemSizes(True)
        self.listView.setMovement(QListView.Static)
        self.listView.setSpacing(10)
        self.listView.setIconSize(QSize(160, 160))
        mainLay = QVBoxLayout()
        mainLay.addWidget(QLabel('Big Picture View Mode'))
        mainLay.addWidget(self.listView)
        self.setLayout(mainLay)

    def currentListView(self):
        return self.listView

# class MTableViewWidget(QWidget):
#     def __init__(self, parent=None):
#         super(MTableViewWidget, self).__init__(parent)
#         self.initUI()
#
#     def initUI(self):
#         headerList = [{
#             "attr": "code",
#             "name": "Entity Name",
#             "width": 100
#         },
#             {
#                 "attr": "link_type",
#                 "name": "Upload/Local",
#                 "width": 100
#             },
#             {
#                 "attr": "name",
#                 "name": "File Name",
#                 "width": 400
#             },
#             {
#                 "attr": "local_path",
#                 "name": "Path",
#                 "width": 600
#             }]
#         self.tableView = MTableView(headerList=headerList)
#         mainLay = QVBoxLayout()
#         mainLay.addWidget(QLabel('Table View Mode'))
#         mainLay.addWidget(self.tableView)
#         self.setLayout(mainLay)


class MFinder(QMainWindow):
    MULTI_VIEW = 0
    BIG_PICTURE_VIEW = 1
    TABLE_VIEW = 2
    windowList = []

    @MY_CSS()
    def __init__(self, parent=None):
        super(MFinder, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet('font-family:Microsoft Yahei')
        self.setWindowTitle('Finder')
        self.listViewList = []
        self.initUI()

    def initUI(self):
        self.leftWidget = MLeftWidget()
        self.stackWidget = QStackedWidget()
        self.multiViewWidget = MMultiListViewWidget()
        self.bigPictureViewWidget = MBigPictureViewWidget()
        self.connect(self.multiViewWidget, SIGNAL('sigPathChanged(QString)'), self.slotSetWindowTitle)
        self.connect(self.bigPictureViewWidget, SIGNAL('sigPathChanged(QString)'), self.slotSetWindowTitle)
        # self.tableViewWidget = MTableViewWidget()

        self.stackWidget.addWidget(self.multiViewWidget)
        self.stackWidget.addWidget(self.bigPictureViewWidget)
        # self.stackWidget.addWidget(self.tableViewWidget)

        centralWidget = QWidget()
        centralLay = QHBoxLayout()
        centralLay.addWidget(self.leftWidget)
        centralLay.addWidget(self.stackWidget)
        centralWidget.setLayout(centralLay)
        self.setCentralWidget(centralWidget)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.readSettings()
        self.connect(QApplication.clipboard(), SIGNAL('dataChanged()'), self.slotClipboardDataChanged)

    def createActions(self):
        self.newAct = QAction(QIcon('%s/%s' % (IMAGE_PATH, 'icon-add.png')), "&New",
                              self, shortcut=QKeySequence.New,
                              statusTip="Create a new file", triggered=self.newFinder)

    def newFinder(self):
        other = MFinder()
        MFinder.windowList.append(other)
        other.move(self.x() + 40, self.y() + 40)
        other.show()

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setFloatable(False)
        self.fileToolBar.setMovable(False)
        self.fileToolBar.addAction(self.newAct)

        self.preButton = QPushButton('<')
        self.nextButton = QPushButton('>')

        self.bigPictureButton = MBigPictureButton(checkable=True)
        self.multiViewButton = MMultiViewButton(checkable=True)
        self.tableViewButton = MTableViewButton(checkable=True)

        self.viewModeGrp = QButtonGroup()
        self.viewModeGrp.addButton(self.multiViewButton, MFinder.MULTI_VIEW)
        self.viewModeGrp.addButton(self.bigPictureButton, MFinder.BIG_PICTURE_VIEW)
        self.viewModeGrp.addButton(self.tableViewButton, MFinder.TABLE_VIEW)
        self.connect(self.viewModeGrp, SIGNAL('buttonClicked(int)'), self.slotSwitchViewMode)
        self.multiViewButton.setChecked(True)

        self.searchLineEdit = QLineEdit()

        self.fileToolBar.addWidget(self.preButton)
        self.fileToolBar.addWidget(self.nextButton)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.bigPictureButton)
        self.fileToolBar.addWidget(self.multiViewButton)
        self.fileToolBar.addWidget(self.tableViewButton)
        self.fileToolBar.addWidget(self.searchLineEdit)

    def slotClipboardDataChanged(self):
        md = QApplication.clipboard().mimeData()
        print md

    def slotSwitchViewMode(self, index):
        currentView = self.stackWidget.currentWidget().currentListView()
        self.stackWidget.setCurrentIndex(index)
        # if index


    @Slot(int)
    def slotCurrentModeChanged(self, index):
        print index

    @Slot(int)
    def slotSetWindowTitle(self, text):
        self.setWindowTitle(text)
        self.statusBar().showMessage(text)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def readSettings(self):
        settings = QSettings('ZAM', 'Finder')
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings('ZAM', 'Finder')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def closeEvent(self, event):
        if self.maybeSave():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    def maybeSave(self):
        if 0:
            ret = QMessageBox.warning(self, "SDI",
                                      "The document has been modified.\nDo you want to save "
                                      "your changes?",
                                      QMessageBox.Save | QMessageBox.Discard |
                                      QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.save()
            elif ret == QMessageBox.Cancel:
                return False
        return True


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    test = MFinder()
    test.show()
    sys.exit(app.exec_())
