#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################

from GUI.QT import *
import pickle


def createMimeData(operator, ormList):
    itemData = QByteArray(pickle.dumps((operator, ormList)))
    mimeData = QMimeData()
    mimeData.setData('application/galaxy-table', itemData)
    return mimeData


def unpackMimeData(mimeData):
    if mimeData.hasFormat('application/galaxy-table'):
        itemData = mimeData.data('application/galaxy-table')
        operator, ormList = pickle.loads(itemData)
        return operator, ormList
    if mimeData.hasFormat("text/uri-list"):
        urls = mimeData.urls()
        return [url.toLocalFile() for url in urls]
