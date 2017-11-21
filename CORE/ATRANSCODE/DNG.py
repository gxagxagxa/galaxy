#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os
import sys
import subprocess
from tempfile import NamedTemporaryFile
from collections import OrderedDict
from datetime import datetime as pdatetime
from collections import Iterable
from HEADER_STRUCTURE.IFD_HEADER import *

if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from CORE.DECO_DB import *
from CORE.ATIMECODE.ATIMECODE import *
from CORE.APATH.APATH import *


class DNG_HEADER(IFD_BASE):
    @DECO_LAZY
    def _full_path(self):
        return self.file.name

    @DECO_LAZY
    def _master_reel(self):
        return ''

    @DECO_LAZY
    def _master_timecode(self):
        _timecode = getattr(self, 'TimeCode', None)
        if _timecode:
            return '{:02X}:{:02X}:{:02X}:{:02X}'.format(_timecode.value[3], _timecode.value[2],
                                                        _timecode.value[1], _timecode.value[0])
        else:
            return ''

    @DECO_LAZY
    def _fps(self):
        _fps = getattr(self, 'Fps', None)
        if _fps:
            return round(float(_fps.value[0][0]) / _fps.value[0][1], 2)

    @DECO_LAZY
    def _duration(self):
        return '00:00:00:01'

    @DECO_LAZY
    def _frames(self):
        return 1

    @DECO_LAZY
    def _full_width(self):
        return self.ImageWidth.value[0]

    @DECO_LAZY
    def _full_height(self):
        return self.ImageLength.value[0]

    @DECO_LAZY
    def _active_width(self):
        _active = getattr(self, 'DefaultCropSize', None)
        if _active:
            return _active.value[0][0] if isinstance(_active.value[0], Iterable) else _active.value[0]
        else:
            return self._full_width

    @DECO_LAZY
    def _active_height(self):
        _active = getattr(self, 'DefaultCropSize', None)
        if _active:
            return _active.value[0][1] if isinstance(_active.value[0], Iterable) else _active.value[1]
        else:
            return self._full_height

    @DECO_LAZY
    def _channel(self):
        channel_count = self.SamplesPerPixel.value[0] + getattr(getattr(self, 'ExtraSamples', None), 'value', [0])[0]
        return '{} channels'.format(channel_count)

    @DECO_LAZY
    def _codec(self):
        _depth = '{}-bit'.format(self.BitsPerSample.value[0])
        _compression = {1    : 'No compression',
                        2    : 'RLE',
                        7    : 'BMD',
                        32773: 'PackBits'}
        return _depth + ' ' + _compression.get(self.Compression.value[0])

    @DECO_LAZY
    def _creation_date(self):
        if hasattr(self, 'DateTime'):
            return re.sub(r'\00', '', self.DateTime.value[0])
        else:
            with open(self.file.name, 'r') as f:
                return str(pdatetime.fromtimestamp(os.fstat(f.fileno()).st_ctime))

    @DECO_LAZY
    def _file_size(self):
        with open(self.file.name, 'r') as f:
            return os.fstat(f.fileno()).st_size

    @DECO_LAZY
    def _Camera_Model(self):
        _camera = getattr(self, 'UniqueCameraModel', None)
        if _camera:
            return re.sub(r'\00', '', _camera.value[0])
        else:
            return ''

    @DECO_LAZY
    def _Camera_Serial_Number(self):
        _camera_sn = getattr(self, 'Software', None) or getattr(self, 'CameraSerialNumber', None)
        if _camera_sn:
            return re.sub(r'\00', '', _camera_sn.value[0])
        else:
            return ''


class DNG_TRANSCODE(object):
    def __init__(self, first_dng, last_dng=None):
        self.filename = first_dng
        self.end_filename = last_dng

    @DECO_LAZY
    def all_metadata(self):
        first_header = None
        last_header = None
        with open(self.filename, 'r') as f:
            first_header = DNG_HEADER.read_file(f)

        if self.end_filename:
            with open(self.end_filename, 'r') as f:
                last_header = DNG_HEADER.read_file(f)
        else:
            last_header = None

        return first_header, last_header if last_header else first_header

    @property
    def basic_metadata(self):
        first_meta = None
        last_meta = None
        if isinstance(self.all_metadata, tuple):
            first_meta, last_meta = self.all_metadata
        else:
            first_meta = self.all_metadata
            last_meta = None

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
        cmd = ['sips',
               '-Z', '720',
               '-s', 'format', 'jpeg',
               self.filename,
               '--out', temp_image + '.jpg']
        # print cmd
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
    # dng = '/Volumes/work/TEST_Footage/~Footage/BM-Pocket/Greggs BMPCC_1_2015-01-25_1144_C0009_000009.dng'
    dng = '/Volumes/BACKUP/TEST_Footage/Footage/CION-Day/00000002.dng'
    test = DNG_TRANSCODE(dng)
    print test.lds_metadata

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
