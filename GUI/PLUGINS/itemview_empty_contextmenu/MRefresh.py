#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.QT import *


class MRefresh(MPluginBase):
    name = 'Refresh'
    icon = 'icon-refresh.png'
    needRefresh = True
    shortcut = Qt.Key_F5

    def run(self, event):
        super(MRefresh, self).run(event)

    def validate(self, event):
        return True
