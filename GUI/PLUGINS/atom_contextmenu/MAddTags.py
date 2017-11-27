#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *
from GUI.WIDGETS.MTagWidget import MChooseTagDialog

class MAddTags(MPluginBase):
    name = 'Add Tags'
    icon = 'icon-tag.png'
    needRefresh = True
    shortcut = QKeySequence.Copy

    def run(self, event):
        cur = QCursor.pos()
        ormList = event.get('orm')
        parentWidget = event.get('parentWidget')
        dialog = MChooseTagDialog(parentWidget)
        dialog.setTargetORM(ormList[0])
        dialog.move(cur + QPoint(-dialog.width(), 0))
        dialog.show()

    def validate(self, event):
        orm = event.get('orm')
        if isinstance(orm, list) and len(orm) > 1:
            return False
        return True
