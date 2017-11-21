#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.QT import *
from GUI.WIDGETS.MInputDialog import MInputDialog
from GUI.PLUGINS.MTableHandle import *


class MAddAtom(MPluginBase):
    name = 'New ATOM'
    icon = 'icon-add.png'
    needRefresh = True

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        result = True
        name = 'NewATOM1'
        while result:
            name, result = MInputDialog.getText(parentWidget, 'New ATOM', 'Name:', name, MAtom._nameRegExp)
            if result:
                if MAtom.validateExist(name, orm):
                    QMessageBox.critical(parentWidget, 'ERROR', 'This name exists.')
                    continue
                else:
                    MAtom.inject(name=name, parent=orm)
                    self.emit(SIGNAL('sigRefresh()'))
                    return

    def validate(self, event):
        return True
