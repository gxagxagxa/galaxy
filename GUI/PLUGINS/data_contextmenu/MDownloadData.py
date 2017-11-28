#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *
from GUI.WIDGETS.MJobMonitor import MJobMonitor


class MDownloadData(MPluginBase):
    name = 'Download'
    icon = 'icon-download.png'
    needRefresh = True
    shortcut = QKeySequence.Copy

    def run(self, event):
        ormList = event.get('orm')
        parentWidget = event.get('parentWidget')
        folder = QFileDialog.getExistingDirectory(parentWidget, 'Save Folder', '', )
        if folder:
            #TODO: add job to db
            dialog = MJobMonitor(parentWidget)
            if dialog.exec_():
                QMessageBox.information(self, 'OK', 'SUCCESS')

    def validate(self, event):
        return True
