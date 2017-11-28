#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

import datetime as dd

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *


class MAddTodayAtom(MPluginBase):
    name = 'Add Today Folder "%s"' % str(dd.date.today())
    icon = 'icon-add.png'
    needRefresh = True

    def run(self, event):
        parentWidget = event.get('parentWidget')
        orm = event.get('orm')
        name = str(dd.date.today())

        if MAtom.validateExist(name, orm):
            QMessageBox.critical(parentWidget, 'ERROR', 'This name exists.')
        else:
            MAtom.inject(name=name, parent=orm)
        super(MAddTodayAtom, self).run(event)
        return
    

    def validate(self, event):
        return True
