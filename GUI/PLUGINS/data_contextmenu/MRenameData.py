#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.WIDGETS.MInputDialog import MInputDialog
from GUI.PLUGINS.MTableHandle import *
from CORE.DB_UTIL import *

class MRenameData(MPluginBase):
    name = 'Rename DATA'
    icon = 'icon-edit.png'
    needRefresh = True
    shortcut = Qt.Key_F2

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        result = True
        name = orm.name
        while result:
            name, result = MInputDialog.getText(parentWidget, 'New ATOM', 'Name:', name, MData._nameRegExp)
            if result:
                if MData.validateExist(name, orm.parent):
                    QMessageBox.critical(parentWidget, 'ERROR', 'This name exists.')
                    continue
                else:
                    try:
                        orm = DB_UTIL.refresh(orm)
                        sess().commit()
                        MData.update(orm, name=name)
                        self.emit(SIGNAL('sigRefresh()'))
                    except:
                        sess().rollback()
                        raise Exception('Fail to rename {}:{}'.format(orm.name, orm.sid))

                    break

    def validate(self, event):
        return True