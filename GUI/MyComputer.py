# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

from PySide.QtCore import *
from PySide.QtGui import *
from functools import partial


class MFileListView(QListView):
    def __init__(self, parent=None):
        super(MFileListView, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath(r'C:\Users\muyanru\mu_prj')
        self.setModel(self.fileModel)


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


class MFinder(QMainWindow):
    windowList = []

    def __init__(self, parent=None):
        super(MFinder, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet('font-family:Microsoft Yahei')
        self.setWindowTitle('Finder')
        self.listViewList = []
        self.initUI()

    def initUI(self):
        self.leftWidget = MLeftWidget()
        # self.scrollWidget = QScrollArea()
        self.splitter = QSplitter()
        self.slotAddNewListView()
        # self.scrollWidget.add

        centralWidget = QWidget()
        centralLay = QHBoxLayout()
        centralLay.addWidget(self.leftWidget)
        centralLay.addWidget(self.splitter)
        centralWidget.setLayout(centralLay)
        self.setCentralWidget(centralWidget)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.readSettings()

    def slotAddNewListView(self):
        newListView = MFileListView()
        self.splitter.addWidget(newListView)
        self.listViewList.append(newListView)

    def createActions(self):
        self.newAct = QAction(QIcon(':/images/new.png'), "&New",
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

        self.thumbnailButton = QToolButton()
        self.thumbnailButton.setCheckable(True)
        self.listButton = QToolButton()
        self.listButton.setCheckable(True)
        self.detailButton = QToolButton()
        self.detailButton.setCheckable(True)

        self.viewModeGrp = QButtonGroup()
        self.viewModeGrp.addButton(self.thumbnailButton)
        self.preButton = QPushButton('<')
        self.nextButton = QPushButton('>')

        self.thumbnailButton = QToolButton()
        self.thumbnailButton.setCheckable(True)
        self.listButton = QToolButton()
        self.listButton.setCheckable(True)
        self.detailButton = QToolButton()
        self.detailButton.setCheckable(True)

        self.viewModeGrp = QButtonGroup()
        self.viewModeGrp.addButton(self.thumbnailButton)
        self.viewModeGrp.addButton(self.listButton)
        self.viewModeGrp.addButton(self.detailButton)
        self.listButton.setChecked(True)

        self.searchLineEdit = QLineEdit()

        self.listButton.setChecked(True)

        self.searchLineEdit = QLineEdit()

        self.fileToolBar.addWidget(self.preButton)
        self.fileToolBar.addWidget(self.nextButton)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.thumbnailButton)
        self.fileToolBar.addWidget(self.listButton)
        self.fileToolBar.addWidget(self.detailButton)
        self.fileToolBar.addWidget(self.searchLineEdit)

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
