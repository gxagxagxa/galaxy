#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.PLUGINS.MPluginBase import MPluginBase
from GUI.PLUGINS.MTableHandle import *
from CORE.DB_UTIL import *


class MDelete(MPluginBase):
    name = 'Delete Selected'
    icon = 'icon-trash.png'
    needRefresh = True
    shortcut = QKeySequence.Delete

    def run(self, event):
        parentWidget = event.get('parentWidget')
        ormList = event.get('orm')
        msg = QMessageBox(parentWidget)
        msg.setText('Are you sure?')
        msg.setInformativeText(
            'Delete: \n{}'.format('\n'.join(['{}: {}'.format(orm.__tablename__, orm.name) for orm in ormList])))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Yes)
        ret = msg.exec_()
        if ret == QMessageBox.Yes:
            for orm in ormList:
                print orm.__tablename__, orm.name, isinstance(orm, ATOM)
                if (not isinstance(orm, ATOM)) or MAtom.canDelete(orm):
                    try:
                        sess().delete(orm)
                        sess().commit()
                    except Exception as e:
                        QMessageBox.critical(parentWidget, 'ERROR',
                                             'Fail to Delete {}:{}\n{}'.format(orm.sid, orm.name, e))
                        break
                else:
                    QMessageBox.critical(parentWidget, 'ERROR', 'Atom <%s> has children. Can\'t delete' % orm.name)
                    break
            super(MDelete, self).run(event)

    def validate(self, event):
        return True
