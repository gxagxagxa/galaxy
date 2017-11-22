#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.QT import *
from GUI.WIDGETS.MInjectDataDialog import MInjectDataDialog
from GUI.PLUGINS.MTableHandle import *

class MInjectData(MPluginBase):
    name = 'Inject Data'
    icon = 'icon-add.png'
    needRefresh = True

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        dialog = MInjectDataDialog(orm, parentWidget)
        dialog.exec_()
        self.emit(SIGNAL('sigRefresh()'))
        return

    def validate(self, event):
        return True
