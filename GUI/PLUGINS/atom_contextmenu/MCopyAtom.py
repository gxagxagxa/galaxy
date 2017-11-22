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


class MCopyAtom(MPluginBase):
    name = 'Copy Folder'
    icon = 'icon-edit.png'
    needRefresh = True
    shortcut = QKeySequence.Copy

    def run(self, event):
        orm = event.get('orm')
        clipBoard = QApplication.clipboard()
        clipBoard.setMimeData(mmd.createMimeData('copy', orm))

    def validate(self, event):
        return True
