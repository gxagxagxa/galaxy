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
    name = 'Rename ATOM'
    icon = 'icon-edit.png'
    needRefresh = True

    @staticmethod
    def run(event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
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
                    break

    @staticmethod
    def validate(event):
        return True