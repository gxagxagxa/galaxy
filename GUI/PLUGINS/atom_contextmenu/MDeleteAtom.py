#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.QT import *


class MDeleteAtom(MPluginBase):
    name = 'Delete ATOM'
    icon = 'icon-trash.png'

    # def __init__(self, parent = None):
    #     super(MDeleteAtom, self).__init__(parent)

    @staticmethod
    def run(event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        QMessageBox.information(parentWidget, 'ok', 'success')

    @staticmethod
    def validate(event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        print orm.name
        return True