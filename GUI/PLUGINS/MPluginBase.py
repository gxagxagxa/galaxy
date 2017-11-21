#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################


from GUI.QT import *


class MPluginBase(QObject):
    name = None
    icon = None
    needRefresh = True

    def __init__(self, parent = None):
        super(MPluginBase, self).__init__(parent)

    def run(self, event):
        pass

    def validate(self, event):
        pass