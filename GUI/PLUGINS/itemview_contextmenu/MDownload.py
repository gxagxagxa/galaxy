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


class MDownload(MPluginBase):
    name = 'Download'
    icon = 'icon-download.png'
    needRefresh = False
    shortcut = QKeySequence.Copy

    def run(self, event):
        ormList = event.get('orm')
        parentWidget = event.get('parentWidget')
        folder = QFileDialog.getExistingDirectory(parentWidget, 'Save Folder', '', )
        if folder:
            #TODO: add job to db
            #ormList 中有各种类型的 atom data raw link...
            dialog = MJobMonitor(parentWidget)
            if dialog.exec_():
                QMessageBox.information(self, 'OK', 'SUCCESS')

        super(MDownload, self).run(event)

    def validate(self, event):
        return True
