#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Mu yanru
# Date  : 2017.11
# Email : muyanru345@163.com
###################################################################
from GUI.QT import *


def getTextColor(backgroundColor):
    light = backgroundColor.redF() * 0.30 + backgroundColor.greenF() * 0.59 + backgroundColor.blueF() * 0.11
    if light < 0.5:
        return QColor.fromRgbF(1 - 0.3 * light, 1 - 0.3 * light, 1 - 0.3 * light)
    else:
        return QColor.fromRgbF((1 - light) * 0.3, (1 - light) * 0.3, (1 - light) * 0.3)


class MAZTagRect(QLabel):
    def __init__(self, orm=None, parent=None):
        super(MAZTagRect, self).__init__(parent)
        self.isPressed = False
        self.tagORM = orm
        self.setText(self.tagORM.name if self.tagORM else '')
        self.setColor( QColor(self.tagORM.color if self.tagORM else 'f00'))

    def setORM(self, orm):
        self.tagORM = orm

    def setColor(self, color):
        self.backgroundColor = color
        self.foregroundColor = getTextColor(self.backgroundColor)
        self.update()

    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def leaveEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.isPressed = True

    def mouseReleaseEvent(self, event):
        if self.isPressed:
            self.emit(SIGNAL('clicked(PyObject)'), self.tagORM)
            self.isPressed = False

    def rect(self):
        content = self.text()
        font1 = QFont("Microsoft YaHei", 9, QFont.Light)
        metrics = QFontMetricsF(font1)
        fontWidth = metrics.width(content)
        return QRect(0, 0, fontWidth + 10, metrics.height() + 8)

    def paintEvent(self, event):
        content = self.text()
        font1 = QFont("Microsoft YaHei", 9, QFont.Light)
        metrics = QFontMetricsF(font1)
        fontWidth = metrics.width(content)
        fontHeight = metrics.width(content)

        h = 22
        w = fontWidth + h * 1.2
        self.setFixedSize(w, h)
        painter = QPainter()
        backgroundBrush = QBrush(self.backgroundColor)

        backgroundPen = QPen()
        backgroundPen.setWidth(1)
        backgroundPen.setColor(self.backgroundColor)

        textPen = QPen()
        textPen.setWidth(1)
        textPen.setColor(self.foregroundColor)

        painter.begin(self)
        painter.setBrush(backgroundBrush)
        painter.setPen(QPen(self.backgroundColor))
        painter.drawRoundedRect(self.rect(), self.height() / 2, self.height() / 2)

        painter.setPen(textPen)
        painter.setFont(font1)
        painter.drawText(QPointF(h * 1 / 4, h / 2.0 + 5), content)
        painter.end()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # dataDict = {'id':125, 'name': u'蓝天白云', 'color_string': '#f955ff', 'en_name':'Blue Sky'}
    dataDict = {'id': 125, 'name': u'蓝天白云', 'color': '#f955ff', 'en_name': 'Blue Sky'}
    test = MAZTagRect()
    # test.setText(dataDict['name'] + dataDict['en_name'])
    # test.setColor(QColor(dataDict['color']))
    # test = MAZTagLabelSimple()
    test.show()
    sys.exit(app.exec_())
