# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

from PySide.QtCore import *
from PySide.QtGui import *
from functools import partial
from GUI.WIDGETS.MToolButton import *
from WIDGETS.MItemView import MListView
from CORE.DB_CONNECT import *
from DECO import MY_CSS
from IMAGES import IMAGE_PATH


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
        self.pixmap.fromImage(orm.thumbnail)
        self.imageLabel.setPixmap(self.pixmap)
        self.attrLabel.setText(str(orm))


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


class MMultiListViewWidget(QWidget):
    def __init__(self, parent=None):
        super(MMultiListViewWidget, self).__init__(parent)
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.listViewList = []
        self.rootListView = MListView()
        self.detailWidget = MDetailWidget()
        self.detailWidget.setVisible(False)
        self.rootListView._getORMList = lambda parentORM: sess().query(ATOM).filter(ATOM.parent_sid==None).all()
        self.connect(self.rootListView, SIGNAL('sigSelectedChanged(PyObject)'), self.slotCurrentChanged)
        self.splitter.addWidget(self.rootListView)
        self.splitter.addWidget(self.detailWidget)
        mainLay = QVBoxLayout()
        mainLay.addWidget(self.splitter)
        self.setLayout(mainLay)
        self.rootListView.slotUpdate()

    @Slot(object)
    def slotCurrentChanged(self, parentORMs):
        parentListView = self.sender()
        parentORM = parentORMs
        if len(parentORMs)>=1:
            parentORM = parentORMs[0]
        if isinstance(parentORM, ATOM):
            self.detailWidget.setVisible(False)
            self.addNewListView(parentListView, parentORM)
        else:
            currentIndex = self.splitter.indexOf(parentListView)
            for i in range(self.splitter.count()):
                if i > currentIndex:
                    self.splitter.setCollapsible(i, False)
            self.splitter.addWidget(self.detailWidget)

    def addNewListView(self, parentListView, parentORM):
        newListView = parentListView.childListView
        if not newListView:
            newListView = MListView()
            self.connect(newListView, SIGNAL('sigSelectedChanged(PyObject)'), self.slotCurrentChanged)
            parentListView.setChildListView(newListView)
            self.listViewList.append(newListView)
            self.splitter.addWidget(newListView)
        newListView.slotUpdate(parentORM)

    def currentListView(self):
        return None


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
        self.connect(self.viewModeGrp, SIGNAL('buttonClicked(int)'), self.stackWidget.setCurrentIndex)
        self.multiViewButton.setChecked(True)

        self.searchLineEdit = QLineEdit()

        self.fileToolBar.addWidget(self.preButton)
        self.fileToolBar.addWidget(self.nextButton)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.bigPictureButton)
        self.fileToolBar.addWidget(self.multiViewButton)
        self.fileToolBar.addWidget(self.tableViewButton)
        self.fileToolBar.addWidget(self.searchLineEdit)

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
