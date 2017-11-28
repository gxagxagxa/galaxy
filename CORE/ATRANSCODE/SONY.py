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


class SONY_TRANSCODE(object):
    def __init__(self, r3d_file):
        super(SONY_TRANSCODE, self).__init__()
        cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK)
                                   for path in os.environ["PATH"].split(os.pathsep))
        if sys.platform != 'darwin' or not cmd_exists('/Applications/RAW Viewer.app/Contents/MacOS/rawexporter'):
            raise Exception('not a Mac or Not install rawexporter')
        self.filename = r3d_file

    @DECO_LAZY
    def all_metadata(self):
        cmd = ['/Applications/RAW Viewer.app/Contents/MacOS/rawexporter', '--input', self.filename, '--metalist']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        result = OrderedDict()
        for x in p.communicate()[0].strip().splitlines()[:-1]:
            # print x.split(':\t')
            key, value = x.split(':\t')
            result[key] = value

        return result

    @property
    def basic_metadata(self):
        meta = self.all_metadata
        result = {'filename'   : self.filename,
                  'clip_name'  : os.path.basename(self.filename).split('.')[0],
                  'reel'       : os.path.basename(self.filename)[:8],
                  'project_fps': float(meta.get('Format FPS', 24)[:-1])}
        result['project_fps'] = float(meta.get('Capture FPS', 24)[:-1]) if meta.get('Capture FPS', None) else result[
            'project_fps']
        result['start_tc'] = TIMECODE(meta.get('Start', '00:00:00:00'), fps=result['project_fps'])
        result['end_tc'] = TIMECODE(meta.get('End', '00:00:00:00'), fps=result['project_fps'])
        result['start_fc'] = result['start_tc'].framecount()
        result['end_fc'] = result['end_tc'].framecount()
        result['duration'] = int(meta.get('Total Frames', result['end_fc'] - result['start_fc'] + 1))
        result['shot_date'] = pdatetime.strptime(meta.get('Creation Date')[:10], '%Y-%m-%d').date()
        result['iso'] = meta.get('ISO Sensitivity', 800)
        result['white_balance'] = int(meta.get('White Balance', 5600))
        result['shutter'] = float(
            meta.get('Shutter Speed Angle', 180.0) if meta.get('Shutter Speed Angle', 180.0) else 180.0)
        result['full_width'] = int(meta.get('Resolution', None).split('x')[0])
        result['full_height'] = int(meta.get('Resolution', None).split('x')[1])
        result['active_width'] = result['full_width']
        result['active_height'] = result['full_height']

        return result

    @property
    def lds_metadata(self):
        meta = self.all_metadata
        result = {}
        result['lens'] = meta.get('Lens Name', None)
        result['aperture'] = meta.get('Aperture Value', None)
        result['focal'] = meta.get('Current Focal Length', None)
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
        raise NotImplementedError

        temp_image = NamedTemporaryFile().name
        print temp_image
        cmd = ['/Applications/RAW Viewer.app/Contents/MacOS/rawexporter',
               '--input', self.filename,
               '--in', (self.basic_metadata['start_tc'] + frame).timecode(),
               '--out', (self.basic_metadata['start_tc'] + frame).timecode(),
               '--output', temp_image + '.jpg',
               '--metaIgnoreFrameGuide',
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
    test = SONY_TRANSCODE(
            u'/Volumes/BACKUP/TEST_Footage/Footage/Sony_F55/Short raw samples/Merli-overexposed.mxf')
    print test.basic_metadata
    # print test.lds_metadata
    #
    # import sys
    # from PySide.QtCore import *
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
