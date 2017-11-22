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

class MDeleteAtom(MPluginBase):
    name = 'Delete Folder'
    icon = 'icon-trash.png'
    needRefresh = True
    shortcut = QKeySequence.Delete

    def run(self, event):
        parentWidget = event.get('parentWidget')
        ormList = event.get('orm')
        for orm in ormList:
            if MAtom.canDelete(orm):
                MAtom.delete(orm)
                self.emit(SIGNAL('sigRefresh()'))
            else:
                QMessageBox.critical(parentWidget, 'ERROR', 'This Atom <%s> has children. Can\'t delete' % orm.name)

    def validate(self, event):
        return True