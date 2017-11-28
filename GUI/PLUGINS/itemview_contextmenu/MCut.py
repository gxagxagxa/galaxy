#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

import GUI.PLUGINS.MMimeData as mmd
from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *


class MCut(MPluginBase):
    name = 'Cut'
    icon = 'icon-cut.png'
    needRefresh = True
    shortcut = QKeySequence.Cut

    def run(self, event):
        ormList = event.get('orm')
        clipBoard = QApplication.clipboard()
        clipBoard.setMimeData(mmd.createMimeData('move', ormList))

    def validate(self, event):
        return True