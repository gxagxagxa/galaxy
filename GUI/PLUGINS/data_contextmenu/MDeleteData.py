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


class MDeleteData(MPluginBase):
    name = 'Delete DATA'
    icon = 'icon-trash.png'
    needRefresh = True
    shortcut = QKeySequence.Delete

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        if MAtom.canDelete(orm):
            msg = QMessageBox(parentWidget)
            msg.setText('Are you sure?')
            msg.setInformativeText('Delete Data: %s' % orm.name)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Yes)
            ret = msg.exec_()
            if ret == QMessageBox.Yes:
                # TODO: delete data orm
                self.emit(SIGNAL('sigRefresh()'))
        else:
            QMessageBox.critical(parentWidget, 'ERROR', 'This data can\'t delete')

    def validate(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        print orm.name
        return True