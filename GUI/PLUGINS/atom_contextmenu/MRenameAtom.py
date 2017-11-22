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


class MRenameAtom(MPluginBase):
    name = 'Rename Folder'
    icon = 'icon-edit.png'
    needRefresh = True
    shortcut = Qt.Key_F2

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')[0]
        result = True
        name = orm.name
        while result:
            name, result = MInputDialog.getText(parentWidget, 'New ATOM', 'Name:', name, MAtom._nameRegExp)
            if result:
                if MAtom.validateExist(name, orm.parent):
                    QMessageBox.critical(parentWidget, 'ERROR', 'This name exists.')
                    continue
                else:
                    MAtom.update(orm, name=name)
                    self.emit(SIGNAL('sigRefresh()'))
                    break

    def validate(self, event):
        orm = event.get('orm')
        if len(orm) == 1:
            return True
        else:
            return False