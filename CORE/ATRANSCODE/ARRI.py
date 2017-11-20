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
from CORE.APATH.APATH import *


class ARRI_TRANSCODE(object):
    def __init__(self, ari_mxf_file):
        super(ARRI_TRANSCODE, self).__init__()
        cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK)
                                   for path in os.environ["PATH"].split(os.pathsep))
        if sys.platform != 'darwin' or not cmd_exists('ARC_CMD') or not cmd_exists('ARRIMetaExtract_CMD'):
            raise Exception('not a Mac or Not install Arri cmd tools')
        self.filename = ari_mxf_file

    @DECO_LAZY
    def all_metadata(self):
        temp_csv = APATH(NamedTemporaryFile().name).parent
        source = APATH(self.filename).parent if APATH(self.filename).ext == '.ari' else APATH(self.filename)
        first_cmd = ['ARRIMetaExtract_CMD', '-i', source, '-o', temp_csv, '-s', ',', '-r', 'first']
        last_cmd = ['ARRIMetaExtract_CMD', '-i', source, '-o', temp_csv, '-s', ',', '-r', 'last']

        p1 = subprocess.Popen(first_cmd, stdout=subprocess.PIPE)
        p1.wait()
        first_csv = \
        next((x for x in p1.communicate()[0].splitlines()[::-1] if 'Finished (csv):' in x), None).split(': ')[-1]
        p2 = subprocess.Popen(last_cmd, stdout=subprocess.PIPE)
        p2.wait()
        last_csv = \
        next((x for x in p2.communicate()[0].splitlines()[::-1] if 'Finished (csv):' in x), None).split(': ')[-1]

        result = None
        with open(first_csv, 'r') as first_file:
            header, first_value = first_file.read().splitlines()
            with open(last_csv, 'r') as last_file:
                _, last_value = last_file.read().splitlines()
                first_dict = OrderedDict(zip(header.split(','), first_value.split(',')))
                last_dict = OrderedDict(zip(header.split(','), last_value.split(',')))
                result = first_dict
                result['End Master TC'] = last_dict.get('Master TC')
                result['End Master TC Frame Count'] = last_dict.get('Master TC Frame Count')
                result['Duration'] = int(last_dict['Master TC Frame Count']) - \
                                     int(first_dict['Master TC Frame Count']) + 1

        print first_csv, last_csv
        os.unlink(first_csv)
        os.unlink(last_csv)
        return result

    @property
    def basic_metadata(self):
        meta = self.all_metadata
        result = {'filename'   : self.filename,
                  'clip_name'  : meta.get('Camera Clip Name', None),
                  'reel'       : meta.get('Reel', None),
                  'project_fps': float(meta.get('Project FPS', 24)),
                  'record_fps' : float(meta.get('Master TC Time Base', 24))}
        result['start_tc'] = TIMECODE(meta.get('Master TC', '00:00:00:00'), fps=result['project_fps'])
        result['end_tc'] = TIMECODE(meta.get('End Master TC', '00:00:00:00'), fps=result['project_fps'])
        result['start_fc'] = int(meta.get('Master TC Frame Count'))
        result['end_fc'] = int(meta.get('End Master TC Frame Count'))
        result['duration'] = meta.get('Duration')
        result['shot_date'] = pdatetime.strptime(meta.get('System Image Creation Date'), '%Y/%m/%d').date()
        result['iso'] = int(meta.get('White Balance', 800))
        result['white_balance'] = int(meta.get('White Balance', 5600))
        result['shutter'] = float(meta.get('Shutter Angle', 180.0))
        result['full_width'] = int(meta.get('Image Width', None))
        result['full_height'] = int(meta.get('Image Height', None))
        result['active_width'] = int(meta.get('Active Image Width', None))
        result['active_height'] = int(meta.get('Active Image Height', None))

        return result

    @property
    def lds_metadata(self):
        meta = self.all_metadata
        result = {}
        result['lens'] = meta.get('Lens Model', None)
        result['aperture'] = meta.get('Lens Iris', None)
        result['focal'] = meta.get('Lens Focal Length', None)
        result['focus'] = meta.get('Lens Focus Distance', None)

        return result

    @property
    def clue(self):
        meta = self.all_metadata
        return {'cam_clue'     : meta.get('Camera Clip Name', None),
                'vfx_seq_clue' : None,
                'vfx_shot_clue': None,
                'scene_clue'   : meta.get('Scene', None),
                'shot_clue'    : None,
                'take_clue'    : None}

    def thumbnail(self, frame=0, qimage=True):
        temp_image = APATH(NamedTemporaryFile().name)
        cmd = ['ARC_CMD', '-i', self.filename,
               '--output.directory', temp_image.parent,
               '--output.filename', temp_image.stem,
               '--output.startnumber', '0',
               '--output.format', 'jpg',
               '-c', APATH(__file__).parent.child('configs', 'arri_thumbnail_config.xml')]
        print cmd
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        print p.communicate()[0]
        temp_image = temp_image + '.jpg'

        if qimage:
            from PySide.QtGui import QImage
            result = QImage(temp_image)
            os.unlink(temp_image)
            return result

        return temp_image


if __name__ == '__main__':
    test = ARRI_TRANSCODE(
            # '/Volumes/BACKUP/TEST_Footage/Footage/Alexa_mini_RAW/S001C001_160215_R00H.mxf')
            u'/Volumes/BACKUP/TEST_Footage/Footage/A136C011_141119_R6QB中文/A136C011_141119_R6QB.1346649.ari')
    # print test.all_metadata
    # print test.basic_metadata
    # print test.lds_metadata

    import sys
    from PySide.QtCore import  *
    from PySide.QtGui import *

    app = QApplication(sys.argv)
    a = QLabel()
    qq = QPixmap()
    qq.convertFromImage(test.thumbnail())
    a.setPixmap(qq)
    # mainWin = MainWindow()
    a.show()
    sys.exit(app.exec_())
