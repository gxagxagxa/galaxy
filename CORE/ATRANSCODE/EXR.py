#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from math import log
import os
import sys
import re
from tempfile import NamedTemporaryFile
from datetime import datetime as pdatetime
from HEADER_STRUCTURE.PACKED_HEADER import *

if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from CORE.DECO_DB import *
from CORE.APATH.APATH import *
from CORE.ATIMECODE.ATIMECODE import *

NON_ASCII = re.compile(r'[^\w \xC0-\xFF]')

NULL = '\x00'


class EXR_HEADER(PACKED_BASE):
    def is_deep_exr(self):
        deep_flag = ''.join(['{:08b}'.format(ord(x), 'b') for x in self.flags[0]])
        return True if deep_flag[4] == '1' else False

    @DECO_LAZY
    def _file_size(self):
        with open(self.file.name, 'r') as f:
            return os.fstat(f.fileno()).st_size

    @DECO_LAZY
    def _full_path(self):
        return self.file.name

    @DECO_LAZY
    def _master_timecode(self):
        _timecode = getattr(getattr(getattr(self, 'timeCode', None), 'value', None), 'timeAndFlags', None)
        if _timecode:
            _timecode = '{:08x}'.format(_timecode)
            return _timecode[0:2] + ':' + _timecode[2:4] + ':' + _timecode[4:6] + ':' + _timecode[6:8]

    @DECO_LAZY
    def _channel(self):
        return '/'.join(self.channels.value.__dict__.keys())

    @DECO_LAZY
    def _codec(self):
        _channel = getattr(self.channels.value, self.channels.value.__dict__.keys()[0], None)
        _compression = getattr(getattr(self, 'compression', None), 'value', None)
        compression_dict = {0: 'NO COMPRESSION',
                            1: 'RLE',
                            2: 'ZIPS',
                            3: 'ZIP',
                            4: 'PIZ',
                            5: 'PX2R4',
                            6: 'B44',
                            7: 'B44A'}

        depth_dict = {0: '16-bit Uint',
                      1: '16-bit half float',
                      2: '32-bit float'}

        return depth_dict[_channel.pixel_type] + ' - ' + compression_dict[_compression]

    @DECO_LAZY
    def master_reel(self):
        return None

    @DECO_LAZY
    def _fps(self):
        _fps = getattr(getattr(self, 'framesPerSecond', None), 'value', None)
        if _fps:
            return round(float(_fps.a1) / _fps.a2, 2)
        return 24.0

    @DECO_LAZY
    def _duration(self):
        return '00:00:00:01'

    @DECO_LAZY
    def _frames(self):
        return 1

    @DECO_LAZY
    def _full_width(self):
        data_window = getattr(getattr(self, 'dataWindow'), 'value', None)
        if data_window:
            return data_window.xMax - data_window.xMin + 1

    @DECO_LAZY
    def _full_height(self):
        data_window = getattr(getattr(self, 'dataWindow'), 'value', None)
        if data_window:
            return data_window.yMax - data_window.yMin + 1

    @DECO_LAZY
    def _active_width(self):
        display = getattr(getattr(self, 'displayWindow'), 'value', None)
        if display:
            return display.xMax - display.xMin + 1

    @DECO_LAZY
    def _active_height(self):
        display = getattr(getattr(self, 'displayWindow'), 'value', None)
        if display:
            return display.yMax - display.yMin + 1

    @DECO_LAZY
    def _creation_date(self):
        with open(self.file.name, 'r') as f:
            return str(pdatetime.fromtimestamp(os.fstat(f.fileno()).st_ctime))


class EXR(object):
    def __init__(self, first_exr, last_exr=None):
        self.filename = first_exr
        self.last_filename = last_exr

    @DECO_LAZY
    def all_metadata(self):
        first_meta = None
        last_meta = None

        if self.last_filename:
            with open(self.filename, 'r') as first_file:
                with open(self.last_filename, 'r') as last_file:
                    first_meta = EXR_HEADER.read_file(first_file)
                    last_meta = EXR_HEADER.read_file(last_file)
        else:
            with open(self.filename, 'r') as first_file:
                first_meta = EXR_HEADER.read_file(first_file)
                last_meta = None

        return first_meta, last_meta if last_meta else first_meta

    @property
    def basic_metadata(self):
        first_meta = None
        last_meta = None
        if isinstance(self.all_metadata, tuple):
            first_meta, last_meta = self.all_metadata
        else:
            first_meta = self.all_metadata
            last_meta = None

        result = {}
        result = {'filename'   : self.filename,
                  'clip_name'  : APATH(self.filename).stem.split('.')[0],
                  'reel'       : None,
                  'project_fps': first_meta._fps,
                  'record_fps' : first_meta._fps}
        result['start_tc'] = TIMECODE(first_meta._master_timecode, fps=result['project_fps'])
        result['end_tc'] = TIMECODE(last_meta._master_timecode, fps=result['project_fps']) if last_meta else result[
            'start_tc']
        result['start_fc'] = result['start_tc'].framecount()
        result['end_fc'] = result['end_tc'].framecount()
        result['duration'] = result['end_fc'] - result['start_fc'] + 1
        result['shot_date'] = pdatetime.strptime(first_meta._creation_date[:10], '%Y-%m-%d').date()
        result['iso'] = None
        result['white_balance'] = None
        result['shutter'] = None
        result['full_width'] = first_meta._full_width
        result['full_height'] = first_meta._full_height
        result['active_width'] = first_meta._active_width
        result['active_height'] = first_meta._active_height

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
        return {'cam_clue'     : APATH(self.filename).stem.split('.')[0],
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
    import types

    # exrfile = '/Users/mac/Desktop/RED_ACES.exr'
    exrfile = '/Volumes/BACKUP/TEST_Footage/Footage/EXR/deep/part_blueBalloon.exr'
    exrfile = '/Volumes/BACKUP/TEST_Footage/Footage/EXR/A003C028_140924_R6QB.0403757.exr'
    # exrfile = '/Users/mac/Desktop/for_andy_testing/gz_0220_lgt_watertest_v0005.VRayRawGlobalIllumination_tiled.1001.exr'
    test = EXR(exrfile)
    print test.all_metadata

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
