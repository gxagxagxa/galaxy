#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os
import sys
import subprocess
from tempfile import NamedTemporaryFile
from collections import OrderedDict
from datetime import datetime as pdatetime
from xml.etree import cElementTree as et

if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from CORE.DECO_DB import *
from CORE.ATIMECODE.ATIMECODE import *
from CORE.APATH.APATH import *


class DSLR_TRANSCODE(object):
    def __init__(self, dslr_file):
        super(DSLR_TRANSCODE, self).__init__()
        cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK)
                                   for path in os.environ["PATH"].split(os.pathsep))
        if sys.platform != 'darwin' or not cmd_exists('sips') or not cmd_exists('mdls'):
            raise Exception('not a Mac or Not install sips or mdls (built-in cmd)')
        self.filename = dslr_file

    @DECO_LAZY
    def all_metadata(self):
        cmd = ['mdls', self.filename, '-plist', '-']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        root = et.fromstring(p.communicate()[0])
        result = {}
        plist = root.find('./dict')
        for index in range(len(plist) / 2):
            result[plist[index * 2].text] = plist[index * 2 + 1].text

        return result

    @property
    def basic_metadata(self):
        meta = self.all_metadata

        result = {'filename'   : self.filename,
                  'clip_name'  : APATH(self.filename).stem,
                  'reel'       : None,
                  'project_fps': 1.0 / float(meta.get('kMDItemExposureTimeSeconds', 1.0)),
                  'record_fps' : 1.0 / float(meta.get('kMDItemExposureTimeSeconds', 1.0))}
        result['start_tc'] = None

        result['start_fc'] = None
        result['duration'] = None
        result['end_tc'] = None
        result['start_fc'] = None
        result['end_fc'] = None
        result['shot_date'] = pdatetime.strptime(meta.get('kMDItemContentCreationDate')[:10],
                                                 '%Y-%m-%d').date() if meta.get('kMDItemContentCreationDate',
                                                                                None) else None
        result['iso'] = meta.get('kMDItemISOSpeed', None)
        result['white_balance'] = meta.get('kMDItemWhiteBalance', None)
        result['shutter'] = None
        result['full_width'] = int(meta.get('kMDItemPixelWidth', None))
        result['full_height'] = int(meta.get('kMDItemPixelHeight', None))
        result['active_width'] = result['full_width']
        result['active_height'] = result['full_height']

        return result

    @property
    def lds_metadata(self):
        meta = self.all_metadata
        result = {}
        result['lens'] = meta.get('kMDItemAcquisitionModel', None)
        result['aperture'] = meta.get('kMDItemAperture', None)
        result['focal'] = meta.get('kMDItemFocalLength', None)
        result['focus'] = None

        return result

    @property
    def clue(self):
        return {'cam_clue'     : APATH(self.filename).stem,
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
    from pprint import pprint

    # print 1.0 / Fraction('1/24')
    test = DSLR_TRANSCODE(
            u'/Volumes/BACKUP/TEST_Footage/HDRI_TEST/包围曝光素材/_MG_6093.CR2')
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
