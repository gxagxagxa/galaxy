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
from WIDGETS.MTagWidget import MTagEditDialog


class MHSeparator(QFrame):
    def __init__(self, parent=None):
        super(MHSeparator, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


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

        rootButton = QToolButton()
        rootButton.setText('< Root View >')
        self.connect(rootButton, SIGNAL('clicked()'), self.slotRoot)

        mainLay = QVBoxLayout()
        mainLay.addWidget(rootButton)
        mainLay.addWidget(MHSeparator())
        mainLay.addWidget(lab1)
        for i in range(5):
            button = QToolButton()
            button.setText('My Filter %d' % (i + 1))
            self.connect(button, SIGNAL('clicked()'), partial(self.slotFavorite, i + 1))
            self.favoriteListButton.append(button)
            mainLay.addWidget(button)

        addFilterButton = QToolButton()
        addFilterButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        addFilterButton.setText('Filter...')
        addFilterButton.setIcon(QIcon('{}/icon-add.png'.format(IMAGE_PATH)))
        self.connect(addFilterButton, SIGNAL('clicked()'), self.slotAddFilter)
        mainLay.addWidget(addFilterButton)
        mainLay.addSpacing(10)
        mainLay.addWidget(MHSeparator())
        mainLay.addWidget(lab2)
        for i in range(5):
            button = QToolButton()
            button.setText('Share %d' % (i + 1))
            self.connect(button, SIGNAL('clicked()'), partial(self.slotShare, i + 1))
            self.sharedListButton.append(button)
            mainLay.addWidget(button)
        mainLay.addSpacing(10)
        mainLay.addWidget(MHSeparator())
        mainLay.addWidget(lab3)
        for tagORM in sess().query(TAG).all():
            pix = QPixmap('%s/icon-%s.png' % (IMAGE_PATH, 'tag'))
            mask = pix.mask()
            pix.fill(QColor(getattr(tagORM, 'color')))
            pix.setMask(mask)
            button = QToolButton()
            button.setIcon(QIcon(pix))
            button.setText(tagORM.name)
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.connect(button, SIGNAL('clicked()'), partial(self.slotTag, tagORM))
            self.tagsListButton.append(button)
            mainLay.addWidget(button)

        mainLay.addStretch()
        self.setLayout(mainLay)

    def slotRoot(self):
        self.emit(SIGNAL('sigShowRoot()'))

    @Slot(int)
    def slotFavorite(self, index):
        print 'slotFavorite', index

    @Slot(int)
    def slotShare(self, index):
        print 'slotShare', index

    @Slot(object)
    def slotTag(self, tagORM):
        self.emit(SIGNAL('sigShowTag(PyObject)'), tagORM)

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

        self.connect(self.rootListView, SIGNAL('sigSelectedChanged(PyObject)'),
                     partial(self.slotCurrentChanged, self.rootListView))
        self.connect(self.rootListView, SIGNAL('sigGoTo(object)'), SIGNAL('sigGoTo(object)'))
        self.splitter.addWidget(self.rootListView)
        self.splitter.addWidget(self.detailWidget)
        self.scrollArea.setWidget(self.splitter)
        mainLay = QVBoxLayout()
        mainLay.addWidget(self.scrollArea)
        self.setLayout(mainLay)

    def slotScroll2Right(self, a, b):
        self.scrollArea.horizontalScrollBar().setValue(b)

    def slotGoTo(self, targetORM):
        # self.rootListView.slotUpdate(DB_UTIL.get_root())
        ormList = DB_UTIL.hierarchy(targetORM, posix=False)
        listView = self.rootListView
        for orm in ormList:
            listView.setCurrentItemData(orm)
            listView = listView.childListView

    @Slot(MListView, object)
    def slotCurrentChanged(self, parentListView, parentORMs):
        parentORM = parentORMs
        if isinstance(parentORMs, list) and len(parentORMs) >= 1:
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
            self.connect(newListView, SIGNAL('sigSelectedChanged(PyObject)'),
                         partial(self.slotCurrentChanged, newListView))
            self.connect(newListView, SIGNAL('sigGoTo(PyObject)'), self.slotGoTo)
            self.connect(newListView, SIGNAL('sigGetFocus(PyObject)'), self.slotGetFocus)
            self.connect(newListView, SIGNAL('sigDropFile(PyObject)'),
                         partial(self.slotShowInjectDataDialog, newListView))

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
            for i in range(len(self.listViewList) - 1, -1, -1):
                tempView = self.listViewList[i]
                if tempView.getAllItemsData():
                    return tempView
        return None

    def slotSwitchTo(self, path):
        orm = DB_UTIL.goto(path)[-1]
        self.slotGoTo(orm)


class MBigPictureViewWidget(QWidget):
    def __init__(self, parent=None):
        super(MBigPictureViewWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.listView = MListView()
        self.listView.setViewMode(QListView.IconMode)
        self.listView.setResizeMode(QListView.Adjust)
        self.listView.setUniformItemSizes(False)
        self.listView.setMovement(QListView.Static)
        self.listView.setSpacing(10)
        self.listView.setIconSize(QSize(160, 160))
        mainLay = QVBoxLayout()
        mainLay.addWidget(QLabel('Big Picture View Mode'))
        mainLay.addWidget(self.listView)
        self.setLayout(mainLay)

    def currentListView(self):
        return self.listView

    def slotGoTo(self, targetORM):
        self.listView.slotUpdate(targetORM.parent)
        self.listView.setCurrentItemData(targetORM)

    def slotSwitchTo(self, path):
        orm = DB_UTIL.goto(path)[-1]
        self.listView.slotUpdate(orm.parent)

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
        self.slotShowRootView()

    def initUI(self):
        self.leftWidget = MLeftWidget()
        self.stackWidget = QStackedWidget()
        self.multiViewWidget = MMultiListViewWidget()
        self.bigPictureViewWidget = MBigPictureViewWidget()
        self.connect(self.multiViewWidget, SIGNAL('sigPathChanged(QString)'), self.slotSetWindowTitle)
        self.connect(self.multiViewWidget, SIGNAL('sigGoTo(object)'), self.slotGoToNewFinder)
        self.connect(self.bigPictureViewWidget, SIGNAL('sigPathChanged(QString)'), self.slotSetWindowTitle)
        self.connect(self.leftWidget, SIGNAL('sigShowTag(PyObject)'), self.slotShowTagChildren)
        self.connect(self.leftWidget, SIGNAL('sigShowRoot()'), self.slotShowRootView)
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
                              statusTip="Create a new file", triggered=self.slotNewFinder)
        self.tagAct = QAction(QIcon('%s/%s' % (IMAGE_PATH, 'icon-tag.png')), "Tag Manager",
                              self, shortcut=QKeySequence(Qt.Key_K),
                              statusTip="Open Tag Manager", triggered=self.slotShowTagManager)
        self.copyAct = QAction(QIcon('%s/%s' % (IMAGE_PATH, 'icon-copy.png')), "Copy",
                               self, shortcut=QKeySequence.Copy,
                               statusTip="Copy Current Selected", triggered=self.slotCopy)
        self.cutAct = QAction(QIcon('%s/%s' % (IMAGE_PATH, 'icon-cut.png')), "Cut",
                              self, shortcut=QKeySequence.Cut,
                              statusTip="Cut Current Selected", triggered=self.slotCut)
        self.linkAct = QAction(QIcon('%s/%s' % (IMAGE_PATH, 'icon-link.png')), "Link",
                               self, shortcut=QKeySequence('ctrl+l'),
                               statusTip="Link Current Selected", triggered=self.slotLink)
        self.pasteAct = QAction(QIcon('%s/%s' % (IMAGE_PATH, 'icon-paste.png')), "Paste",
                                self, shortcut=QKeySequence.Paste,
                                statusTip="Link Current Selected", triggered=self.slotPaste)

    @Slot()
    def slotNewFinder(self):
        other = MFinder()
        MFinder.windowList.append(other)
        other.move(self.x() + 40, self.y() + 40)
        other.show()

    @Slot(object)
    def slotGoToNewFinder(self, targetORM):
        other = MFinder()
        other.stackWidget.setCurrentIndex(self.stackWidget.currentIndex())
        listView = other.stackWidget.currentWidget()
        listView.slotGoTo(targetORM)
        MFinder.windowList.append(other)
        other.move(self.x() + 40, self.y() + 40)
        other.show()

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.tagAct)
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addAction(self.linkAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setFloatable(False)
        self.fileToolBar.setMovable(False)

        self.preButton = MPreButton()
        self.nextButton = MNextButton()

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

        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.tagAct)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.copyAct)
        self.fileToolBar.addAction(self.cutAct)
        self.fileToolBar.addAction(self.pasteAct)
        self.fileToolBar.addAction(self.linkAct)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.preButton)
        self.fileToolBar.addWidget(self.nextButton)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.bigPictureButton)
        self.fileToolBar.addWidget(self.multiViewButton)
        self.fileToolBar.addWidget(self.tableViewButton)
        self.fileToolBar.addWidget(self.searchLineEdit)

    def slotClipboardDataChanged(self):
        md = QApplication.clipboard().mimeData()

    def slotSwitchViewMode(self, index):
        self.stackWidget.setCurrentIndex(index)
        self.stackWidget.currentWidget().slotSwitchTo(self.windowTitle())

    @Slot()
    def slotCopy(self):
        pass

    @Slot()
    def slotCut(self):
        pass

    @Slot()
    def slotPaste(self):
        pass

    @Slot()
    def slotLink(self):
        pass

    @Slot()
    def slotShowTagManager(self):
        test = MTagEditDialog(self)
        test.show()

    @Slot(object)
    def slotShowTagChildren(self, tagORM):
        self.multiViewWidget.rootListView.slotUpdate(tagORM)

    @Slot()
    def slotShowRootView(self):
        self.multiViewWidget.rootListView.slotUpdate(DB_UTIL.get_root())

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
