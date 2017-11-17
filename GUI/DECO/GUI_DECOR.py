#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.7
# Email : muyanru345@163.com
###################################################################
from functools import wraps
import traceback
from GUI.QT import *
from GUI.CSS import CSS_PATH
import pkgutil

main = pkgutil.get_data('GUI.CSS', 'main.qss').replace('url(',
                                                       'url(%s/' % CSS_PATH.replace('\\', '/'))


def MY_CSS(cssContent=main):
    def wrapper1(func):
        def new_init(*args, **kwargs):
            result = func(*args, **kwargs)
            instance = args[0]
            instance.setStyleSheet(cssContent)
            return result

        return new_init

    return wrapper1
