#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from fractions import Fraction
import re

SMPTE_TIMECODE_NDF = 'SMPTE_TIMECODE_NDF'
SMPTE_TIMECODE_DF = 'SMPTE_TIMECODE_DF'
SRT_TIMECODE = 'SRT_TIMECODE'
DLP_TIMECODE = 'DLP_TIMECODE'
FFMPEG_TIMECODE = 'FFMPEG_TIMECODE'


class FRAMERATE(float):
    def __init__(self, fps):
        super(FRAMERATE, self).__init__()
        # self.value = fps


class TIMECODE(object):
    SMPTE_Regex_NDF = re.compile(r'^(?:(?:(?:([01]?\d|2[0-3]|\d{3}):)?([0-5]?\d):)?([0-5]?\d):)?([0-5]?\d)$')
    SMPTE_Regex_DF = re.compile(r'^(?:(?:(?:([01]?\d|2[0-3]|\d{3}):)?([0-5]?\d):)?([0-5]?\d);)?([0-5]?\d)$')
    SRT_Regex = re.compile(r'^(?:(?:(?:([01]?\d|2[0-3]|\d{3}):)?([0-5]?\d):)?([0-5]?\d),)?(\d\d\d)$')
    DLP_Regex = re.compile(r'^(?:(?:(?:([01]?\d|2[0-3]|\d{3}):)?([0-5]?\d):)?([0-5]?\d):)?([0-2][0-4]\d)$')
    ffmpeg_Regex = re.compile(r'^(?:(?:(?:([01]?\d|2[0-3]|\d{3}):)?([0-5]?\d):)?([0-5]?\d)\.)?(\d?\d)$')

    def __init__(self, *args, **kwargs):
        self.value = None
        self.fps = FRAMERATE(kwargs.get('fps', 24.0))
        # print args
        # print kwargs
        if isinstance(args[0], TIMECODE):
            self.value = args[0].value
            self.fps = args[0].fps
        if isinstance(args[0], Fraction):
            self.value = args[0]
        if isinstance(args[0], (int, float)):
            if len(args) > 1:
                self.value = Fraction(args[0], args[1]) / self.fps
            else:
                self.value = Fraction(args[0]) / self.fps
        if isinstance(args[0], str):
            if TIMECODE.SMPTE_Regex_NDF.match(args[0]):
                mytc = [x for x in TIMECODE.SMPTE_Regex_NDF.match(args[0]).groups()]
                mytc = map(lambda x: int(x) if x else 0, mytc)
                framecount = mytc[0] * 3600 + mytc[1] * 60 + mytc[2] + mytc[3] / self.fps
                self.value = Fraction(framecount)
            if TIMECODE.SMPTE_Regex_DF.match(args[0]):
                mytc = [x for x in TIMECODE.SMPTE_Regex_DF.match(args[0]).groups()]
                mytc = map(lambda x: int(x) if x else 0, mytc)
                framecount = mytc[0] * 3600 + mytc[1] * 60 + mytc[2] + mytc[3] / self.fps
                # framecount = framecount - mytc[1] * 2 + mytc[1] // 10 * 2
                self.value = Fraction(framecount)
            if TIMECODE.SRT_Regex.match(args[0]):
                mytc = [x for x in TIMECODE.SRT_Regex.match(args[0]).groups()]
                mytc = map(lambda x: int(x) if x else 0, mytc)
                framecount = mytc[0] * 3600 + mytc[1] * 60 + mytc[2] + mytc[3] / 1000.0
                self.value = Fraction(framecount)
            if TIMECODE.DLP_Regex.match(args[0]):
                mytc = [x for x in TIMECODE.DLP_Regex.match(args[0]).groups()]
                mytc = map(lambda x: int(x) if x else 0, mytc)
                framecount = mytc[0] * 3600 + mytc[1] * 60 + mytc[2] + mytc[3] / 250.0
                self.value = Fraction(framecount)
            if TIMECODE.ffmpeg_Regex.match(args[0]):
                mytc = [x for x in TIMECODE.ffmpeg_Regex.match(args[0]).groups()]
                mytc = map(lambda x: int(x) if x else 0, mytc)
                framecount = mytc[0] * 3600 + mytc[1] * 60 + mytc[2] + mytc[3] / 100.0
                self.value = Fraction(framecount)

    def __get_hhmmssff(self):
        round_value = round(self.value, 5)
        hh = round_value // 3600
        mm = (round_value - hh * 3600) // 60
        ss = round((round_value - hh * 3600 - mm * 60) // 1, 0)
        ff = float(round_value - hh * 3600 - mm * 60 - ss)
        hh = hh if hh >= 0 else hh + abs(hh) * 24
        return int(hh), int(mm), int(ss), ff

    def framecount(self):
        return int(round(self.value * self.fps, 0))

    def _convert_to_SMPTE_TIMECODE_NDF(self):
        hh, mm, ss, ff = self.__get_hhmmssff()
        return '{:02d}:{:02d}:{:02d}:{:02d}'.format(hh, mm, ss, int(round(ff * self.fps, 0)))

    def _convert_to_SMPTE_TIMECODE_DF(self):
        hh, mm, ss, ff = self.__get_hhmmssff()
        return '{:02d}:{:02d}:{:02d};{:02d}'.format(hh, mm, ss, int(round(ff * self.fps, 0)))

    def _convert_to_SRT_TIMECODE(self):
        hh, mm, ss, ff = self.__get_hhmmssff()
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(hh, mm, ss, int(round(ff * 1000.0, 0)))

    def _convert_to_DLP_TIMECODE(self):
        hh, mm, ss, ff = self.__get_hhmmssff()
        return '{:02d}:{:02d}:{:02d}:{:03d}'.format(hh, mm, ss, int(round(ff * 250.0, 0)))

    def _convert_to_FFMPEG_TIMECODE(self):
        hh, mm, ss, ff = self.__get_hhmmssff()
        return '{:02d}:{:02d}:{:02d}.{:02d}'.format(hh, mm, ss, int(round(ff * 100.0, 0)))

    def timecode(self, type=SMPTE_TIMECODE_NDF):
        func = getattr(self, '_convert_to_{}'.format(type), None)
        if func:
            return func()

    def is_inside(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return other.start <= self and self <= other.end
        return False

    def __ne__(self, other):
        try:
            return self.value != TIMECODE(other, fps=self.fps).value
        except:
            raise Exception('TIMECODE and only compare with TIMECODE')

    def __le__(self, other):
        try:
            return self.value <= TIMECODE(other, fps=self.fps).value
        except:
            raise Exception('TIMECODE and only compare with TIMECODE')

    def __ge__(self, other):
        try:
            return self.value >= TIMECODE(other, fps=self.fps).value
        except:
            raise Exception('TIMECODE and only compare with TIMECODE')

    def __lt__(self, other):
        try:
            return self.value < TIMECODE(other, fps=self.fps).value
        except:
            raise Exception('TIMECODE and only compare with TIMECODE')

    def __gt__(self, other):
        try:
            return self.value > TIMECODE(other, fps=self.fps).value
        except:
            raise Exception('TIMECODE and only compare with TIMECODE')

    def __eq__(self, other):
        try:
            return self.value == TIMECODE(other, fps=self.fps).value
        except:
            raise Exception('TIMECODE and only compare with TIMECODE')

    def __add__(self, other):
        try:
            return TIMECODE(Fraction(self.value + TIMECODE(other, fps=self.fps).value), fps=self.fps)
        except:
            raise Exception('TIMECODE and only add with TIMECODE')

    def __sub__(self, other):
        try:
            return TIMECODE(Fraction(self.value - TIMECODE(other, fps=self.fps).value), fps=self.fps)
        except:
            raise Exception('TIMECODE and only sub with TIMECODE')

    def __mul__(self, other):
        try:
            return TIMECODE(Fraction(self.value * other), fps=self.fps)
        except:
            raise Exception('TIMECODE and only sub with int / float')

    def __div__(self, other):
        try:
            return TIMECODE(Fraction(self.value / other), fps=self.fps)
        except:
            raise Exception('TIMECODE and only sub with int / float')

    def __repr__(self):
        return '<TIMECODE> ({} | {} @ {}fps)'.format(self.timecode(), self.framecount(), self.fps)


class MORE_TIMECODE_RANGE(object):
    def __init__(self, start, end):
        local_start = TIMECODE(start)
        local_end = TIMECODE(end)
        self.start = min(local_start, local_end)
        self.end = max(local_start, local_end)
        self.duration = self.end - self.start
        self.fps = self.start.fps
        self.current = 0

    def is_inside(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return self.start >= other.start and self.end <= other.end
        else:
            return False

    def is_contain(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return self.start <= other.start and self.end >= other.end
        else:
            return False

    def is_overlap(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return self.start <= other.start and other.start <= self.end \
                   or other.start <= self.start and self.start <= other.end
        else:
            return False

    def is_freeze(self):
        if self.duration > 1:
            return False
        else:
            return True

    def union(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return MORE_TIMECODE_RANGE(min(self.start, other.start), max(self.end, other.end))
        else:
            return self

    def intersection(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            if self.is_overlap(other):
                return MORE_TIMECODE_RANGE(max(self.start, other.start), min(self.end, other.end))
        return None

    def difference(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            temp_list = [self.start, self.end, other.start, other.end]
            temp_list.sort()
            return MORE_TIMECODE_RANGE(temp_list[0], temp_list[1]), MORE_TIMECODE_RANGE(temp_list[2], temp_list[3])
        return None

    def offset(self, head, tail=None):
        local_tail = head if tail is None else tail
        return MORE_TIMECODE_RANGE(self.start + head, self.end + local_tail)

    def handle(self, head, tail=None):
        local_tail = head if tail is None else tail
        return MORE_TIMECODE_RANGE(self.start - head, self.end + local_tail)

    def speed(self, speed):
        if speed == 0:
            return MORE_TIMECODE_RANGE(self.start, self.start + 1)
        else:
            return MORE_TIMECODE_RANGE(self.start, self.start + self.duration / speed)

    def transition(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            trans = self.intersection(other)
            if trans:
                return trans.start + trans.duration / 2.0
        return None

    def move(self, point):
        local_point = TIMECODE(point, fps=self.fps)
        if local_point:
            return MORE_TIMECODE_RANGE(local_point, local_point + self.duration)
        return None

    def cut(self, point):
        local_point = TIMECODE(point, fps=self.fps)
        if local_point.is_inside(self):
            return MORE_TIMECODE_RANGE(self.start, local_point), MORE_TIMECODE_RANGE(local_point, self.end)
        return self

    def timecode(self):
        return self.start, self.end

    def __iter__(self):
        self.current = 0
        return self

    def next(self):
        if self.current <= self.duration.framecount():
            result = self.start + self.current
            self.current += 1
            return result
        else:
            raise StopIteration()

    def __gt__(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return self.start > other.start
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return self.start < other.start
        else:
            return False

    def __le__(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return self.start <= other.start
        else:
            return False

    def __ge__(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return self.start >= other.start
        else:
            return False

    def __eq__(self, other):
        if isinstance(other, MORE_TIMECODE_RANGE):
            return self.start == other.start and self.end == other.end
        else:
            return False

    def __repr__(self):
        return '<TIMECODE_RANGE> ({} - {} | {} - {} @ {}fps)'.format(self.start.timecode(), self.end.timecode(),
                                                                     self.start.framecount(), self.end.framecount(),
                                                                     self.fps)


if __name__ == '__main__':
    tc1 = TIMECODE('00:00:01:00', fps=FRAMERATE(48))
    tc2 = TIMECODE('00:00:02:00', fps=FRAMERATE(48))
    tc3 = TIMECODE(150, fps=FRAMERATE(24))
    tc4 = TIMECODE(400, fps=FRAMERATE(24))
    a = [tc2, tc3, tc4, tc1]
    print a
    a.sort()
    print a
    # tc = 25.0
    # print max(tc, tc2)
    ran = MORE_TIMECODE_RANGE(tc1, tc2)
    ran2 = MORE_TIMECODE_RANGE(tc3, tc4)
    # print ran.is_inside(ran2)
    # print ran2.is_contain(ran)
    # print ran.intersection(ran2)
    # print ran.difference(ran2)
    print ran.intersection(ran2)
    print ran
    print ran.move(tc2)
    print ran.timecode()
    # ran = ran.add_handel(15, 0)
    print ran.offset(10)
    for x in ran:
        print x
