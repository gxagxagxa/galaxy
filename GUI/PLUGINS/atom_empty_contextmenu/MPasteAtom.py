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

class MPasteAtom(MPluginBase):
    name = 'Paste Folder'
    icon = 'icon-edit.png'
    needRefresh = True
    shortcut = QKeySequence.Paste

    def run(self, event):
        parentWidget = event.get('parentWidget')
        currentORM = event.get('orm')
        clipBoard = QApplication.clipboard()
        mimeData = clipBoard.mimeData()
        operator, ormList = mmd.unpackMimeData(mimeData)
        # TODO: operator is copy, create link
        print operator, currentORM.name, ormList.name
        # TODO: operator is move, change parent

    def validate(self, event):
        clipBoard = QApplication.clipboard()
        mimeData = clipBoard.mimeData()
        if mimeData.hasFormat('application/galaxy-table'):
            return True
        return False