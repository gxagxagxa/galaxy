#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from unipath import *
from collections import defaultdict, OrderedDict
import re
import sys
import os
import subprocess

IGNORE_SCAN_DICT = {'global': {'start': [".", "~", "tmp"],
                               'end'  : [".db", ".more", ".tmp"]}
                    }


class APATH(Path):
    '''
    核心PATH 解析。
    继承unipath，所以所有unipath 的特性全部支持，同时增加了扫描、解析、常用字段 的功能。
    '''
    version_regex = re.compile(r'.*[vV](\d+).*')
    frame_regex = re.compile(r'.*[^\dvV](\d+)[\D]*\..*')
    pattern_regex = re.compile(r'.*(\%\d+d).*|.*?(#+)|.*(\$F\d)')

    def __init__(self, path=''):
        super(APATH, self).__init__(path)

    @property
    def posix(self):
        return APATH(self.replace('\\', '/'))

    @property
    def version(self):
        '''
        返回解析的version 版本号
        :return: string 类型（例如001、002，注意没有v，方便做int）
                    如果解析不出version，返回None
        '''
        match = APATH.version_regex.match(self.name)
        return match.group(1) if match else None

    @property
    def frame(self):
        '''
        返回解析出的帧数
        :return: int 类型。如果没有解析成功，返回-1
        '''
        match = APATH.frame_regex.match(self.name)
        return int(match.group(1)) if match else -1

    @property
    def pattern(self):
        '''
        返回文件的pattern 内容，支持%0xd 和#### 两种方式。
        :return: string 类型，
                    解析出的pattern 部分（例如，%04d, 或者####）
                    如果失败，返回None
        '''
        match = APATH.pattern_regex.match(self.name)
        return match.group(1) or match.group(2) or match.group(3) if match else None

    def to_pattern(self, pattern='%'):
        '''
        将文件自动解析成pattern 样式
        :param pattern: '%' 表示pattern 样式为%0xd ，'#' 表示 ##### 的样式
        :return: 如果可以解析，那么返回解析后的pattern，如果不能解析，返回原始路径
        '''
        temp_restore_filename = self.restore_pattern(1)
        replace_string = ''
        match = APATH.frame_regex.match(temp_restore_filename.name)
        if match:
            if pattern == '%':
                replace_string = '%0{}d'.format(len(match.group(1)))
            elif pattern == '#':
                replace_string = '#' * len(match.group(1))
            elif pattern == '$':
                replace_string = '$F{}'.format(len(match.group(1)))

            new_name = temp_restore_filename.name[:match.start(1)] + \
                       replace_string + temp_restore_filename.name[match.end(1):]
            return APATH(self.parent + '/' + new_name).posix

        else:
            return self

    def restore_pattern(self, frame):
        '''
        从pattern 样式回复成为实际的文件路径
        :param frame: int，需要复原的帧数
        :return: 如果是pattern 类型，就返回还原的实际文件路径，否则直接返回原始文件名
        '''
        if int(frame) < 0:
            return self

        match = APATH.pattern_regex.match(self.name)
        if match:
            if match.group(1):
                return APATH(self % frame)
            elif match.group(2):
                return APATH(self.replace(match.group(2),
                                          '%0{}d'.format(len(match.group(2)))) % frame)
            elif match.group(3):
                return APATH(self.replace(match.group(3),
                                          '%0{}d'.format(match.group(3)[-1:])) % frame)
        else:
            return self

    def _scan_non_recursive(self):
        file_list = [(x.to_pattern(), x.frame) for x in self.listdir(filter=FILES) if
                     not x.name.startswith(tuple(IGNORE_SCAN_DICT['global']['start']))
                     and not x.name.endswith(tuple(IGNORE_SCAN_DICT['global']['end']))]
        file_list.sort()
        if file_list:
            keys = {x[0]: [y[1] for y in file_list if y[0] == x[0]] for x in file_list}

            result = [{'filename': key,
                       'frames'  : value,
                       'missing' : sorted(set(range(value[0], value[-1] + 1)) - set(value))}
                      for key, value in keys.items()]
            return result

    def _scan_recursive(self):
        keys = defaultdict(list)
        for path in self.walk(filter=FILES):
            if not path.name.startswith(tuple(IGNORE_SCAN_DICT['global']['start'])) \
                    and not path.name.endswith(tuple(IGNORE_SCAN_DICT['global']['end'])):
                keys[path.to_pattern()].append(path.frame)

        result = [{'filename': key,
                   'frames'  : sorted(value),
                   'missing' : sorted(set(range(value[0], value[-1] + 1)) - set(value))}
                  for key, value in keys.items()]
        return result

    def scan(self, recursive=False):
        '''
        扫描。
        有三种情况，如果self 是file，那么就会返回这个file 对应的sequence。
        如果是folder，并且recursive=True，进行递归搜索，给出所有的sequence
        如果是folder，并且recursive=False，只搜索当前层的文件，给出所有的sequence

        :param recursive: True 进行递归搜索，False 只搜索当前文件夹下的文件
        :return: recursive=True，返回dict 类型的list。recursive=False，返回dict
                dict 的样式：
                    {'filename': pattern_name,
                    'frames'  : [1001, 1002...],
                    'missing' : []}
        '''
        if not self.isdir():
            folder = self.parent
            pattern_name = self.to_pattern()
            file_list = folder.listdir(
                    pattern=pattern_name.name.replace(pattern_name.pattern if pattern_name.pattern else '//',
                                                      '?' * int(pattern_name.pattern[1:-1]
                                                                if pattern_name.pattern else 1)),
                    filter=FILES)
            file_list.sort()
            frames = [x.frame for x in file_list]
            return {'filename': pattern_name,
                    'frames'  : sorted(frames),
                    'missing' : sorted(set(range(frames[0], frames[-1] + 1)) - set(frames))}
        else:
            if recursive:
                return self._scan_recursive()

            else:
                return self._scan_non_recursive()

    def _show_in_win32(self, show_file=False):
        if show_file:
            os.startfile(self)
        else:
            os.startfile(self if self.isdir() else self.parent)

    def _show_in_darwin(self, show_file=False):
        if show_file:
            subprocess.Popen('osascript -e \'tell application "Finder" to reveal ("{}" as POSIX file)\''.format(self),
                             shell=True)
        else:
            subprocess.Popen(['open', self if self.isdir() else self.parent])

    def _show_in_linux2(self, show_file=False):
        subprocess.Popen(['xdg-open', self if self.isdir() else self.parent])

    def show(self, show_file=False):
        sub_func = getattr(self, '_show_in_{}'.format(sys.platform), None)
        if sub_func:
            sub_func(show_file=show_file)


if __name__ == '__main__':
    path1 = '/Volumes/BACKUP/TEST_Footage/Footage/A104C016_141103_R6QB/A104C016_141103_R6QB.0438785.ari'
    path2 = '/Volumes/BACKUP/TEST_Footage/Footage/A104C016_141103_R6QB/A104C016_141103_R6QB.#######.ari'
    path3 = '/Volumes/BACKUP/TEST_Footage/Footage/'
    path4 = '/Volumes/ORACLE/Temp/guoxiaoao/publish/wkz-test/sequence/nj/nj_0010/element/comp/pl_0010_comp_master/pl_0010_comp_master_v0001/fullres/exr/pl_0010_comp_master_v0001.1001.exr'
    path7 = '/Volumes/x/publish/project_test/sequence/pl/pl_0010/dailies/comp/pl_0010_comp_master/pl_0010_comp_master_v0001/fullres/exr/pl_0010_comp_master_v0001.1001.exr'
    path5 = '/Volumes/ORACLE/work/project_test/sequence/pl/pl_0010/andy/pl_0010_comp_master/pl_0010_comp_master_v0001.001.exr'
    path6 = '/Volumes/x/cache/project_test/sequence/pl/pl_0010/element/comp/pl_0010_comp_master/pl_0010_comp_master_v0001/fullres/exr/pl_0010_comp_master_v0001.1001.exr'
    path7 = 'X:/Temp/guoxiaoao/publish/wkz-test/sequence/pl/pl_0010/dailies/ani/pl_0010_ani_muyr/pl_0010_ani_muyr_v0008/dpx/pl_0010_ani_muyr_v0008.%04d.dpx'
    path8 = '/Users/guoxiaoao/Desktop/test/WUK_s066_c0523_cmp_v004'
    path8 = '/Users/guoxiaoao/Desktop/test/WUK_s066_c0523_cmp_v004/WUK_s066_c0523_cmp_v004.123.dpx'
    # test = MORE_PATH(path2)
    # print  test.version
    # print test.frame
    # result = test.to_pattern()
    # print result
    # print result.restore_pattern(456)
    # print MORE_PATH(path2).restore_pattern(123)
    # pprint(MORE_PATH(path4).parse)
    # test = MORE_PATH(path4)
    # dd = MORE_PATH(
    #         '$HOME/Desktop/flip surface cache/flip_v0001.0001.bgeo.sc')
    # pprint(dd.to_pattern('$'))

    # print MORE_PATH(path5).parse.values().index(str(MORE_PATH(path5).artist))
    # print '/'.join(MORE_PATH(path5).parse.values()[:6])


    workpath = APATH(path5)

    if workpath.platform().is_legal() and workpath.artist:
        values_index = workpath.parse.values().index(workpath.artist)

        # pprint(test.parse)
        # pprint(test.parse)
        # print test.project
