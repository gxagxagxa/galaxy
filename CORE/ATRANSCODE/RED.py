#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os
import sys
import subprocess
from tempfile import NamedTemporaryFile
from collections import OrderedDict
from datetime import datetime as pdatetime

if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from CORE.DECO_DB import *
from CORE.ATIMECODE.ATIMECODE import *


class RED_TRANSCODE(object):
    def __init__(self, r3d_file):
        super(RED_TRANSCODE, self).__init__()
        cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK)
                                   for path in os.environ["PATH"].split(os.pathsep))
        if sys.platform != 'darwin' or not cmd_exists('REDline'):
            raise Exception('not a Mac or Not install RedCine-X')
        self.filename = r3d_file

    @DECO_LAZY
    def all_metadata(self):
        cmd = ['REDline', '--i', self.filename, '--printMeta', '3']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        header, values = p.communicate()[0].strip().splitlines()
        return OrderedDict(zip(header.split(','), values.split(',')))

    @property
    def basic_metadata(self):
        meta = self.all_metadata
        result = {'filename'   : self.filename,
                  'clip_name'  : meta.get('Clip Name', None),
                  'reel'       : meta.get('AltReelID', None),
                  'project_fps': float(meta.get('FPS', 24)),
                  'record_fps' : float(meta.get('Record FPS', 24))}
        result['start_tc'] = TIMECODE(meta.get('Abs TC', '00:00:00:00'), fps=result['project_fps'])
        result['end_tc'] = TIMECODE(meta.get('End Abs TC', '00:00:00:00'), fps=result['project_fps'])
        result['start_fc'] = result['start_tc'].framecount()
        result['end_fc'] = result['end_tc'].framecount()
        result['duration'] = int(meta.get('Total Frames', result['end_fc'] - result['start_fc'] + 1))
        result['shot_date'] = pdatetime.strptime(meta.get('Date'), '%Y%m%d').date()
        result['iso'] = meta.get('ISO', 800)
        result['white_balance'] = int(meta.get('Kelvin', 5600))
        result['shutter'] = float(meta.get('Shutter (deg)', 180.0))
        result['full_width'] = int(meta.get('Frame Width', None))
        result['full_height'] = int(meta.get('Frame Height', None))
        result['active_width'] = result['full_width']
        result['active_height'] = result['full_height']

        return result

    @property
    def lds_metadata(self):
        meta = self.all_metadata
        result = {}
        result['lens'] = meta.get('Lens Name', None)
        result['aperture'] = meta.get('Aperture', None)
        result['focal'] = meta.get('Focal Length', None)
        result['focus'] = meta.get('Focus Distance', None)

        return result

    @property
    def clue(self):
        meta = self.all_metadata
        return {'cam_clue'     : meta.get('Clip Name', None),
                'vfx_seq_clue' : None,
                'vfx_shot_clue': None,
                'scene_clue'   : meta.get('Scene', None),
                'shot_clue'    : meta.get('Shot', None),
                'take_clue'    : meta.get('Take', None)}

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
    test = RED_TRANSCODE(
            u'/Volumes/BACKUP/TEST_Footage/Footage/R3D/offical/weapon-sth-8k-50fps-14to1redcode中文/C003_C004_0902S7_001.R3D')
    print test.basic_metadata
    print test.lds_metadata

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
