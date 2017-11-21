#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os
import sys
import subprocess
from tempfile import NamedTemporaryFile
from collections import OrderedDict
from datetime import datetime as pdatetime
import json

if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from CORE.DECO_DB import *
from CORE.ATIMECODE.ATIMECODE import *
from CORE.APATH.APATH import *


class MOV_TRANSCODE(object):
    def __init__(self, mov_file):
        super(MOV_TRANSCODE, self).__init__()
        cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK)
                                   for path in os.environ["PATH"].split(os.pathsep))
        if sys.platform != 'darwin' or not cmd_exists('ffprobe') or not cmd_exists('ffmpeg'):
            raise Exception('not a Mac or Not install ffmpeg!')
        self.filename = mov_file

    @DECO_LAZY
    def all_metadata(self):
        cmd = ['ffprobe', '-v', 'quiet',
               '-print_format', 'json',
               '-show_format',
               '-show_streams',
               self.filename]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        json_data = json.loads(p.communicate()[0])
        return json_data

    @property
    def basic_metadata(self):
        meta = next((x for x in self.all_metadata.get('streams', []) if x['codec_type'] == 'video'), None)
        if not meta:
            return None

        result = {'filename'   : self.filename,
                  'clip_name'  : APATH(self.filename).stem,
                  'reel'       : self.all_metadata.get('format', None).get('tags', None).get('reel_name', None),
                  'project_fps': 1.0 / Fraction(meta.get('codec_time_base', '1/24')),
                  'record_fps' : 1.0 / Fraction(meta.get('codec_time_base', '1/24'))}
        result['start_tc'] = TIMECODE(str(self.all_metadata.get('format', None).get('tags', None).get('timecode',
                                                                                                      '00:00:00:00')),
                                      fps=result['project_fps'])

        result['start_fc'].framecount()
        result['duration'] = int(float(self.all_metadata.get('format').get('duration')) * result['record_fps'])
        result['end_tc'] = TIMECODE(result['start_tc'].framecount() + result['duration'] - 1,
                                    fps=result['record_fps'])
        result['start_fc'] = result['start_tc'].framecount()
        result['end_fc'] = result['end_tc'].framecount()
        result['shot_date'] = pdatetime.strptime(self.all_metadata.get('format').get('tags').get('creation_time')[:10],
                                                 '%Y-%m-%d').date()
        result['iso'] = None
        result['white_balance'] = None
        result['shutter'] = None
        result['full_width'] = int(meta.get('coded_width', None))
        result['full_height'] = int(meta.get('coded_height', None))
        result['active_width'] = result['full_width']
        result['active_height'] = result['full_height']

        return result

    @property
    def lds_metadata(self):
        result = {}
        result['lens'] = None
        result['aperture'] = None
        result['focal'] = None
        result['focus'] = None

        return result

    @property
    def clue(self):
        meta = self.all_metadata
        return {'cam_clue'     : APATH(self.filename).stem,
                'vfx_seq_clue' : None,
                'vfx_shot_clue': None,
                'scene_clue'   : None,
                'shot_clue'    : None,
                'take_clue'    : None}

    def thumbnail(self, frame=0, qimage=True):
        temp_image = NamedTemporaryFile().name
        # print temp_image
        cmd = ['ffmpeg', '-y',
               '-thread_queue_size', '1024',
               '-i', self.filename,
               '-vframes', '1',
               '-vf', 'scale=720:-1',
               '-q:v', '3',
               temp_image + '.jpg']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        temp_image = temp_image + '.jpg'

        if qimage:
            from PySide.QtGui import QImage
            result = QImage(temp_image)
            os.unlink(temp_image)
            return result
        return temp_image


if __name__ == '__main__':
    from pprint import pprint

    # print 1.0 / Fraction('1/24')
    test = MOV_TRANSCODE(
            '/Volumes/BACKUP/TEST_Footage/Footage/MOV/jzs_v2.mov')
    # pprint(test.all_metadata)
    # pprint(test.basic_metadata)
    # print test.lds_metadata

    import sys
    from PySide.QtCore import *
    from PySide.QtGui import *

    app = QApplication(sys.argv)
    a = QLabel()
    qq = QPixmap()
    qq.convertFromImage(test.thumbnail())
    a.setPixmap(qq)
    # mainWin = MainWindow()
    a.show()
    sys.exit(app.exec_())
