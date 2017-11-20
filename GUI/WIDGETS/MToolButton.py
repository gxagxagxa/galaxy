#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################

from GUI.QT import *
from GUI.IMAGES import IMAGE_PATH


class MToolButton(QToolButton):
    _toolTip = 'tooltips'
    _toolTip_unchecked = 'tooltips_unchecked'
    _icon = 'icon-default.png'
    _icon_unchecked = 'icon-default.png'

    def __init__(self, size=24, checkable=False, userData=None, parent=None):
        super(MToolButton, self).__init__(parent)
        if checkable:
            self.setCheckable(checkable)
            self.connect(self, SIGNAL('toggled(bool)'), self.slotCheckStateChanged)
            self.setChecked(True)
        self.userData = userData
        self.connect(self, SIGNAL('clicked()'), self.slotClicked)
        self.setToolTip(self._toolTip)
        self.setIcon(QIcon('%s/%s' % (IMAGE_PATH, self._icon)))
        # print '%s/%s' % (IMAGE_PATH, self._icon)
        self.setFixedSize(size + 1, size + 1)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)

    @Slot(bool)
    def slotCheckStateChanged(self, checked):
        self.setChecked(checked)
        if checked:
            self.setToolTip(self._toolTip)
            self.setIcon(QIcon('%s/%s' % (IMAGE_PATH, self._icon)))
        else:
            self.setToolTip(self._toolTip_unchecked)
            self.setIcon(QIcon('%s/%s' % (IMAGE_PATH, self._icon_unchecked)))

    @Slot()
    def slotClicked(self):
        self.emit(SIGNAL('sigClicked(PyObject)'), self.userData)


class MRefreshButton(MToolButton):
    _toolTip = 'refresh_data'
    _icon = 'icon-refresh.png'


class MDeleteButton(MToolButton):
    _toolTip = 'delete_data'
    _icon = 'icon-trash.png'


class MEditButton(MToolButton):
    _toolTip = 'edit_data'
    _icon = 'icon-edit.png'


class MSettingButton(MToolButton):
    _toolTip = 'setting'
    _icon = 'icon-setting.png'


class MAddButton(MToolButton):
    _toolTip = 'add_data'
    _icon = 'icon-add.png'


class MAtomButton(MToolButton):
    _toolTip = 'open'
    _icon = 'icon-atom.png'


class MHomeButton(MToolButton):
    _toolTip = 'start_from_here'
    _icon = 'icon-home.png'


class MBigPictureButton(MToolButton):
    _toolTip = 'click_to_switch_to_big_picture_view_mode'
    _toolTip_unchecked = 'click_to_active'
    _icon = 'icon-big-picture.png'
    _icon_unchecked = 'icon-big-picture-unchecked.png'


class MTableViewButton(MToolButton):
    _toolTip = 'click_to_switch_to_big_picture_view_mode'
    _toolTip_unchecked = 'click_to_active'
    _icon = 'icon-list-view.png'
    _icon_unchecked = 'icon-list-view-unchecked.png'

class MMultiViewButton(MToolButton):
    _toolTip = 'click_to_switch_to_big_picture_view_mode'
    _toolTip_unchecked = 'click_to_active'
    _icon = 'icon-multi-view.png'
    _icon_unchecked = 'icon-multi-view-unchecked.png'
