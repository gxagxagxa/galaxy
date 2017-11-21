#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

import pickle

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *
import GUI.PLUGINS.MMimeData as mmd

class MMoveData(MPluginBase):
    name = 'Cut DATA'
    icon = 'icon-edit.png'
    needRefresh = True
    shortcut = QKeySequence.Cut

    def run(self, event):
        orm = event.get('orm')
        clipBoard = QApplication.clipboard()
        clipBoard.setMimeData(mmd.createMimeData('cut', orm))

    def validate(self, event):
        return True