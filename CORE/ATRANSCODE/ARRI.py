#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os
import sys
import subprocess

class ARRI_TRANSCODE(object):
    def __init__(self, ari_mxf_file):
        super(ARRI_TRANSCODE, self).__init__()
        cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK)
                                   for path in os.environ["PATH"].split(os.pathsep))
        if sys.platform != 'darwin' or not cmd_exists('ARC'):
            raise Exception('not a Mac or Not install ARC cmd')
        self.filename = ari_mxf_file