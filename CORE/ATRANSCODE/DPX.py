#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from math import log
import os
import sys
import re
from tempfile import  NamedTemporaryFile
from datetime import datetime as pdatetime
from HEADER_STRUCTURE.FIX_HEADER import *

if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from CORE.DECO_DB import *
from CORE.APATH.APATH import *
from CORE.ATIMECODE.ATIMECODE import *

NON_ASCII = re.compile(r'[^\w \xC0-\xFF]')


class GENERICFILEHEADER(STRUCTURE_BASE):
    _fields = [('4s', 'Magic'),
               ('I', 'ImageOffset'),
               ('8s', 'Version'),
               ('I', 'FileSize'),
               ('I', 'DittoKey'),
               ('I', 'GenericSize'),
               ('I', 'IndustrySize'),
               ('I', 'UserSize'),
               ('100s', 'FileName'),
               ('24s', 'TimeDate'),
               ('100s', 'Creator'),
               ('200s', 'Project'),
               ('200s', 'Copyright'),
               ('I', 'EncryptKey'),
               ('104s', 'Reserved'),
               ]


class ImageElement(STRUCTURE_BASE):
    _fields = [('I', 'DataSign'),
               ('I', 'LowData'),
               ('f', 'LowQuantity'),
               ('I', 'HighData'),
               ('f', 'HighQuantity'),
               ('B', 'Descriptor'),
               ('B', 'Transfer'),
               ('B', 'Colorimetric'),
               ('B', 'BitSize'),
               ('H', 'Packing'),
               ('H', 'Encoding'),
               ('I', 'DataOffset'),
               ('I', 'EndOfLinePadding'),
               ('I', 'EndOfImagePadding'),
               ('32s', 'Description'),
               ]


class GENERICIMAGEHEADER(STRUCTURE_BASE):
    _fields = [('H', 'Orientation'),
               ('H', 'NumberElements'),
               ('I', 'PixelsPerLine'),
               ('I', 'LinesPerElement'),
               (ImageElement, 'ImageElement_1'),
               (ImageElement, 'ImageElement_2'),
               (ImageElement, 'ImageElement_3'),
               (ImageElement, 'ImageElement_4'),
               (ImageElement, 'ImageElement_5'),
               (ImageElement, 'ImageElement_6'),
               (ImageElement, 'ImageElement_7'),
               (ImageElement, 'ImageElement_8'),
               ('52s', 'Reserved'),
               ]


class _Border(STRUCTURE_BASE):
    _fields = [('H', 'XL'),
               ('H', 'XR'),
               ('H', 'YT'),
               ('H', 'YB'),
               ]


class _AspectRatio(STRUCTURE_BASE):
    _fields = [('I', 'H'),
               ('I', 'V'),
               ]


class GENERICORIENTATIONHEADER(STRUCTURE_BASE):
    _fields = [('I', 'XOffset'),
               ('I', 'YOffset'),
               ('f', 'XCenter'),
               ('f', 'YCenter'),
               ('I', 'XOriginalSize'),
               ('I', 'YOriginalSize'),
               ('100s', 'FileName'),
               ('24s', 'TimeDate'),
               ('32s', 'InputName'),
               ('32s', 'InputSN'),
               (_Border, 'Border'),
               (_AspectRatio, 'AspectRatio'),
               ('28s', 'Description'),
               ]


class INDUSTRYFILMINFOHEADER(STRUCTURE_BASE):
    _fields = [('2s', 'FilmMfgId'),
               ('2s', 'FilmType'),
               ('2s', 'Offset'),
               ('6s', 'Prefix'),
               ('4s', 'Count'),
               ('32s', 'Format'),
               ('I', 'FramePosition'),
               ('I', 'SequenceLen'),
               ('I', 'HeldCount'),
               ('f', 'FrameRate'),
               ('f', 'ShutterAngle'),
               ('32s', 'FrameId'),
               ('100s', 'SlateInfo'),
               ('56s', 'Reserved'),
               ]


class _TimeCode(STRUCTURE_BASE):
    _fields = [('B', 'HH'),
               ('B', 'MM'),
               ('B', 'SS'),
               ('B', 'FF'),
               ]


class INDUSTRYTELEVISIONINFOHEADER(STRUCTURE_BASE):
    _fields = [(_TimeCode, 'TimeCode'),
               ('I', 'UserBits'),
               ('B', 'Interlace'),
               ('B', 'FieldNumber'),
               ('B', 'VideoSignal'),
               ('B', 'Padding'),
               ('f', 'HorzSampleRate'),
               ('f', 'VertSampleRate'),
               ('f', 'FrameRate'),
               ('f', 'TimeOffset'),
               ('f', 'Gamma'),
               ('f', 'BlackLevel'),
               ('f', 'BlackGain'),
               ('f', 'Breakpoint'),
               ('f', 'WhiteLevel'),
               ('f', 'IntegrationTimes'),
               ('76s', 'Reserved'),
               ]


class USERDEFINEDDATA(STRUCTURE_BASE):
    _fields = [('32s', 'UserId'),
               ]


class DPX_HEADER(STRUCTURE_BASE):
    _fields = [(GENERICFILEHEADER, 'FileHeader'),
               (GENERICIMAGEHEADER, 'ImageHeader'),
               (GENERICORIENTATIONHEADER, 'OrientHeader'),
               (INDUSTRYFILMINFOHEADER, 'FilmHeader'),
               (INDUSTRYTELEVISIONINFOHEADER, 'TvHeader'),
               (USERDEFINEDDATA, 'UserData'),

               ]

    @classmethod
    def read_file(cls, f):
        cls.file = f
        f.seek(0)
        if unpack_from('4s', f.read(4))[0] == 'SDPX':
            STRUCTURE_BASE._bit_order = 'big'
        else:
            STRUCTURE_BASE._bit_order = 'little'
        f.seek(0)
        return cls(f.read(cls.structure_size))

    @DECO_LAZY
    def _full_path(self):
        return self.file.name

    @DECO_LAZY
    def _master_reel(self):
        return NON_ASCII.sub('', self.OrientHeader.InputName)

    @DECO_LAZY
    def _master_timecode(self):
        return '{0:02X}:{1:02X}:{2:02X}:{3:02X}'.format(self.TvHeader.TimeCode.HH,
                                                        self.TvHeader.TimeCode.MM,
                                                        self.TvHeader.TimeCode.SS,
                                                        self.TvHeader.TimeCode.FF)

    @DECO_LAZY
    def _fps(self):
        return round(self.FilmHeader.FrameRate, 2)

    @DECO_LAZY
    def _duration(self):
        return '00:00:00:01'

    @DECO_LAZY
    def _frames(self):
        return 1

    @DECO_LAZY
    def _full_width(self):
        return self.ImageHeader.PixelsPerLine

    @DECO_LAZY
    def _full_height(self):
        return self.ImageHeader.LinesPerElement

    @DECO_LAZY
    def _active_width(self):
        return self._full_width

    @DECO_LAZY
    def _active_height(self):
        return self._full_height

    @DECO_LAZY
    def _channel(self):
        _lookup = {0  : 'User-defined',
                   1  : 'Red',
                   2  : 'Green',
                   3  : 'Blue',
                   4  : 'Alpha',
                   6  : 'Luminance',
                   7  : 'Chrominance',
                   8  : 'Depth',
                   9  : 'Composite video',
                   50 : 'R/G/B',
                   51 : 'R/G/B/A',
                   52 : 'A/B/G/R',
                   100: 'Cb/Y/Cr/Y',
                   101: 'Cb/Ya/Cr/Ya',
                   102: 'Cb/Y/Cr',
                   103: 'Cb/Y/Cr/a',
                   150: 'User-defined 2-component element',
                   151: 'User-defined 3-component element',
                   152: 'User-defined 4-component element',
                   153: 'User-defined 5-component element',
                   154: 'User-defined 6-component element',
                   155: 'User-defined 7-component element',
                   156: 'User-defined 8-component element',
                   }

        return _lookup.get(self.ImageHeader.ImageElement_1.Descriptor, 'unknown')

    @DECO_LAZY
    def _codec(self):
        return '{}-bit'.format(int(log(self.ImageHeader.ImageElement_1.HighData + 1, 2)))

    @DECO_LAZY
    def _creation_date(self):
        return re.sub(r'\00', '', self.FileHeader.TimeDate)

    @DECO_LAZY
    def _file_size(self):
        with open(self.file.name, 'r') as f:
            return os.fstat(f.fileno()).st_size


class DPX_TRANSCODE(object):
    def __init__(self, first_dpx, last_dpx=None):
        self.filename = first_dpx
        self.end_filename = last_dpx

    @DECO_LAZY
    def all_metadata(self):
        first_header = None
        last_header = None
        with open(self.filename, 'r') as f:
            first_header = DPX_HEADER.read_file(f)

        if self.end_filename:
            with open(self.end_filename, 'r') as f:
                last_header = DPX_HEADER.read_file(f)
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
                  'reel'       : first_meta._master_reel,
                  'project_fps': first_meta._fps,
                  'record_fps' : first_meta._fps}
        result['start_tc'] = TIMECODE(first_meta._master_timecode, fps=result['project_fps'])
        result['end_tc'] = TIMECODE(last_meta._master_timecode, fps=result['project_fps']) if last_meta else result[
            'start_tc']
        result['start_fc'] = result['start_tc'].framecount()
        result['end_fc'] = result['end_tc'].framecount()
        result['duration'] = result['end_fc'] - result['start_fc'] + 1
        result['shot_date'] = pdatetime.strptime(first_meta.FileHeader.TimeDate[:10], '%Y:%m:%d').date()
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
    dpxfile = '/Volumes/BACKUP/TEST_Footage/Footage/DPX/A003C028_140924_R6QB.0403757 copy.dpx'
    test = DPX_TRANSCODE(dpxfile)
    print  test.basic_metadata

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
