#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.8
# Email : muyanru345@163.com
###################################################################

from MItemView import MTableView
from CORE.DB_CONNECT import *
from CORE.DB_UTIL import *
from GUI.CONFIG import MJobMonitorConfigFunc
from GUI.QT import *
from MToolButton import MRefreshButton


class MJobThread(QThread):
    def __init__(self):
        super(MJobThread, self).__init__()

    def run(self):
        # center = MORE_DB_JOB_CENTER_SINGLE(reactive=True)
        # center.run()
        pass


class MUIThread(QThread):
    PROCESS = 0
    def __init__(self):
        super(MUIThread, self).__init__()

    def setTaskDetails(self, tableView):
        self.tableView = tableView

    def run(self):
        #TODO: get job list
        # currentArtist = DB_UTIL.get_current_artist(session)
        # sql_cmd = sess().query(JOB)
        # sql_cmd = sql_cmd.filter(and_(JOB.active == True,
        #                               or_(JOB.job_flag == JOB_READY,
        #                                   JOB.job_flag == JOB_RUNNING),
        #                               JOB.created_by_id == currentArtist.id))
        # result = sql_cmd.all()
        result = [{"description":'pl_0010_comp_master.v0004.%04d.exr',
                   "label":'Copy',
                   "progress":MUIThread.PROCESS,
                   "status":'Running',
                   "created_time":'2017-11-27 18:45',
                   "Created At":'2017-11-27 18:45',
                   "updated_time": '2017-11-27 18:45'}]
        if MUIThread.PROCESS <= 100:
            self.emit(SIGNAL('sigUpdateModel(PyObject)'), result)
        else:
            self.emit(SIGNAL('sigUpdateModel(PyObject)'), result)
            self.emit(SIGNAL('stopUpdate()'))
        MUIThread.PROCESS += 10


class MJobMonitor(QDialog):
    def __init__(self, parent=None):
        super(MJobMonitor, self).__init__(parent)
        self.setWindowTitle('Job Monitor')
        self.uiThread = MUIThread()
        # self.jobThread = MJobThread()
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.uiThread.start)
        self.connect(self.uiThread, SIGNAL('stopUpdate()'), self.slotFinished)
        self.initUI()
        self.initData()
        geo = QApplication.desktop().screenGeometry()
        self.setGeometry(geo.width() / 4, geo.height() / 4, geo.width() / 2, geo.height() / 2)

    def initUI(self):
        dataDict = MJobMonitorConfigFunc().get('jobTable')
        self.tableView = MTableView(headerList=dataDict.get('header'), parent=self)
        self.searchLineEdit = QLineEdit()
        self.connect(self.searchLineEdit, SIGNAL('textChanged(QString)'), self.slotSearch)
        self.refreshButton = MRefreshButton(size=18)
        self.runButton = MRefreshButton(size=18)
        searchLay = QHBoxLayout()
        searchLay.addStretch()
        searchLay.addWidget(self.searchLineEdit)
        searchLay.addWidget(self.refreshButton)

        self.connect(self.uiThread, SIGNAL('sigUpdateModel(PyObject)'), self.slotUpdateData)

        mainLay = QVBoxLayout()
        mainLay.addLayout(searchLay)
        mainLay.addWidget(self.tableView)
        self.setLayout(mainLay)

    @Slot(str)
    def slotSearch(self, content):
        self.tableView.sortFilterModel.setFilterKeyColumn(0)
        self.tableView.sortFilterModel.setFilterRegExp(content)

    @Slot(object)
    def slotUpdateData(self, dataList):
        self.tableView.realModel.setDataList(dataList)

    @Slot()
    def initData(self):
        self.timer.start(1000)
        # self.jobThread.start()

    @Slot()
    def slotFinished(self):
        self.timer.stop()
        # self.jobThread.quit()
        self.accept()

    def closeEvent(self, event):
        event.accept()
        # if self.jobThread.isFinished():
        #     event.accept()
        # else:
        #     QMessageBox.information(self, 'INFO', 'Job is still running. You can close it')
        #     event.ignore()


if __name__ == '__main__':
    # aa = MORE_DB_JOB_CENTER(2)
    # aa.run()

    import sys

    app = QApplication(sys.argv)
    test = MJobMonitor()
    test.show()
    sys.exit(app.exec_())
