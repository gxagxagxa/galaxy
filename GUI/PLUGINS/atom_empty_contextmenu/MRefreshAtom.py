#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *
import GUI.PLUGINS.MMimeData as mmd

class MRefreshAtom(MPluginBase):
    name = 'Refresh'
    icon = 'icon-refresh.png'
    needRefresh = True
    shortcut = Qt.Key_F5

    def run(self, event):
        self.emit(SIGNAL('sigRefresh()'))

    def validate(self, event):
        return True