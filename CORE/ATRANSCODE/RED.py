#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os
import sys
import subprocess
from tempfile import NamedTemporaryFile
from collections import OrderedDict

if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from CORE.DECO_DB import *

class RED_TRANSCODE(object):
    def __init__(self, r3d_file):
        super(RED_TRANSCODE, self).__init__()
        cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK)
                                   for path in os.environ["PATH"].split(os.pathsep))
        if sys.platform != 'darwin' or not cmd_exists('REDline'):
            raise Exception('not a Mac or Not install RedCine-X')
        self.filename = r3d_file

    @DECO_LAZY
    def metadata(self):
        cmd = ['REDline', '--i', self.filename, '--printMeta', '3']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        header, values = p.communicate()[0].strip().splitlines()
        return OrderedDict(zip(header.split(','), values.split(',')))

    @property
    def clue(self):
        meta = self.metadata
        return {'cam_clue': meta.get('D113_C001_0609M2', None),
                'vfx_seq_clue': None,
                'vfx_shot_clue': None,
                'scene_clue': meta.get('Scene', None),
                'shot_clue': meta.get('Shot', None),
                'take_clue': meta.get('Take', None)}

    def thumbnail(self, frame=0, qimage=True):
        temp_image = NamedTemporaryFile().name
        # print temp_image
        cmd = ['REDline', '--i', self.filename, '--o', temp_image,
               '--format', '3', '--start', str(frame), '--end', str(frame),
               '--useMeta', '--metaIgnoreFrameGuide',
               '--res', '8']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        temp_image = '{}.{:06d}.jpg'.format(temp_image, frame)

        if qimage:
            from PySide.QtGui import QImage
            result = QImage(temp_image)
            os.unlink(temp_image)
            return result
        return temp_image


if __name__ == '__main__':
    test = RED_TRANSCODE('/Volumes/VIP_DATA/TEST_Footage/Footage/R3D/D113_C001_0609M2.RDC/D113_C001_0609M2_001.R3D')
    print test.clue

    # import sys
    # from PySide.QtCore import  *
    # from PySide.QtGui import *
    #
    # app = QApplication(sys.argv)
    # a = QLabel()
    # qq = QPixmap()
    # qq.convertFromImage(test.thumbnail())
    # a.setPixmap(qq)
    # # mainWin = MainWindow()
    # a.show()
    # sys.exit(app.exec_())
