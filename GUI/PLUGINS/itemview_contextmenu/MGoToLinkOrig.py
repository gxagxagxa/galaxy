#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *


class MGoToLinkOrig(MPluginBase):
    name = 'Go To Orig Object'
    icon = 'icon-edit.png'
    needRefresh = True
    shortcut = QKeySequence.Copy

    def run(self, event):
        orm = event.get('orm')[0]
        parentWidget = event.get('parentWidget')
        targetORM = orm.target
        if targetORM is None:
            QMessageBox.information(parentWidget, 'Warning', 'This Link\'s original object has been deleted.')
        else:
            parentWidget.emit(SIGNAL('sigGoTo(object)'), targetORM)

    def validate(self, event):
        ormList = event.get('orm')
        if len(ormList) == 1 and isinstance(ormList[0], LINK):
            return True
        else:
            return False
