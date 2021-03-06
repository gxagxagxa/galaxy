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
from CORE.DB_UTIL import *
from GUI.WIDGETS.MReplaceOrSkipDialog import MReplaceOrSkipDialog

class MPaste(MPluginBase):
    name = 'Paste'
    icon = 'icon-paste.png'
    needRefresh = True
    shortcut = QKeySequence.Paste

    def run(self, event):
        parentWidget = event.get('parentWidget')
        currentORM = event.get('orm')
        clipBoard = QApplication.clipboard()
        mimeData = clipBoard.mimeData()
        operator, ormList = mmd.unpackMimeData(mimeData)

        ormList = ormList if isinstance(ormList, (list, tuple)) else (ormList, )
        existing_name = [x.name for x in DB_UTIL.traverse(currentORM)]
        handleSameName = None
        for x in ormList:
            new_name = x.name
            if new_name in existing_name:
                if handleSameName is None:
                    dialog = MReplaceOrSkipDialog(parentWidget)
                    dialog.exec_()
                    handleSameName = dialog.getResult()
                if handleSameName == MReplaceOrSkipDialog.Skip:
                    continue
                else:
                    start = 1
                    new_name += '_{:04d}'.format(start)
                    while new_name in existing_name:
                        start += 1
                        new_name = x.name + '_{:04d}'.format(start)

            if operator == 'copy':
                if isinstance(x, ATOM):
                    sym_link = LINK(name=new_name, parent=currentORM, target=x)
                elif isinstance(x, LINK):
                    sym_link = LINK(name=new_name, parent=currentORM.target, target=x)
                elif isinstance(x, (DATA, RAW)):
                    sym_link = LINK(name=new_name, parent=currentORM, target=x)

                sess().add(sym_link)
                existing_name.append(new_name)
                sess().commit()

            elif operator == 'move':
                x = DB_UTIL.refresh(x)
                x.parent = currentORM
                x.name = new_name
                x.label = new_name
                sess().commit()

        super(MPaste, self).run(event)
        # print operator, currentORM.name, ormList.name

    def validate(self, event):
        clipBoard = QApplication.clipboard()
        mimeData = clipBoard.mimeData()
        if mimeData.hasFormat('application/galaxy-table'):
            return True
        return False
