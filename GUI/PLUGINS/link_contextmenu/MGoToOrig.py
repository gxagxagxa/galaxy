#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *


class MGoToOrig(MPluginBase):
    name = 'Go To Orig Object'
    icon = 'icon-edit.png'
    needRefresh = True
    shortcut = QKeySequence.Copy

    def run(self, event):
        orm = event.get('orm')
        targetORM = orm.target
        print targetORM

    def validate(self, event):
        return True
