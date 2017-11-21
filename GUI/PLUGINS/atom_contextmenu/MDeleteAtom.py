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
    name = 'Delete ATOM'
    icon = 'icon-trash.png'
    needRefresh = True

    # def __init__(self, parent = None):
    #     super(MDeleteAtom, self).__init__(parent)

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        if MAtom.canDelete(orm):
            MAtom.delete(orm)
            self.emit(SIGNAL('sigRefresh()'))
        else:
            QMessageBox.critical(parentWidget, 'ERROR', 'This Atom has children. Can\'t delete')

    def validate(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        print orm.name
        return True