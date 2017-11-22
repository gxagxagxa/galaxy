#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.QT import *
from GUI.PLUGINS.MTableHandle import *


class MDeleteLink(MPluginBase):
    name = 'Delete'
    icon = 'icon-trash.png'
    needRefresh = True
    shortcut = QKeySequence.Delete

    def run(self, event):
        parentWidget = event.get('parentWidget')
        ormList = event.get('orm')
        msg = QMessageBox(parentWidget)
        msg.setText('Are you sure?')
        msg.setInformativeText('Delete Data: \n%s' % '\n'.join(orm.name for orm in ormList))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Yes)
        ret = msg.exec_()
        if ret == QMessageBox.Yes:
            for orm in ormList:
                sess().delete(orm)
            self.emit(SIGNAL('sigRefresh()'))

    def validate(self, event):
        return True
