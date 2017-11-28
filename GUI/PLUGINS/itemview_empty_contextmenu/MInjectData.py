#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *
from GUI.WIDGETS.MInjectDataDialog import MInjectDataDialog


class MInjectData(MPluginBase):
    name = 'Inject Data'
    icon = 'icon-add.png'
    needRefresh = True

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        dialog = MInjectDataDialog(orm, parentWidget)
        dialog.exec_()
        super(MInjectData, self).run(event)
        return

    def validate(self, event):
        return True
