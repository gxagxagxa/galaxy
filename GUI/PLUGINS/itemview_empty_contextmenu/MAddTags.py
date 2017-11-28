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
        orm = event.get('orm')
        parentWidget = event.get('parentWidget')
        dialog = MChooseTagDialog(parentWidget)
        dialog.setTargetORMList([orm])
        dialog.move(cur + QPoint(-dialog.width(), 0))
        dialog.show()
        super(MAddTags, self).run(event)

    def validate(self, event):
        return True
