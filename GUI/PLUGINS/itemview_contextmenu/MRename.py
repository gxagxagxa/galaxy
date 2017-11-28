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


class MRename(MPluginBase):
    name = 'Rename Folder'
    icon = 'icon-edit.png'
    needRefresh = True
    shortcut = Qt.Key_F2

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')[0]
        result = True
        name = orm.name
        handleObj = globals()['M{}'.format(orm.__tablename__.title())]
        while result:
            name, result = MInputDialog.getText(parentWidget, 'New Name', 'Name:', name, handleObj._nameRegExp)
            if result:
                if handleObj.validateExist(name, orm.parent):
                    QMessageBox.critical(parentWidget, 'ERROR', 'This name exists.')
                    continue
                else:
                    try:
                        handleObj.update(orm, name=name)
                    except Exception as e:
                        QMessageBox.critical(parentWidget, 'ERROR', 'Fail to Delete {}:{}\n{}'.format(orm.sid, orm.name, e))
                    self.emit(SIGNAL('sigRefresh()'))
                    break

    def validate(self, event):
        ormLis = event.get('orm')
        if len(ormLis) == 1:
            return True
        else:
            return False
