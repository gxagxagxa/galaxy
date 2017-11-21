#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from uuid import uuid1
from functools import wraps
import bisect
import os
import sys

if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from CORE.ATIMECODE.ATIMECODE import *
from CORE.APATH.APATH import *


def ADD_LEFT_RIGHT_LINK(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # print args
        # print kwargs
        func(*args, **kwargs)
        current_index = args[0].trackitems.index(args[1])
        if current_index > 0:
            args[1].left = args[0].trackitems[current_index - 1]
            args[0].trackitems[current_index - 1].right = args[1]
        if current_index < len(args[0].trackitems) - 1:
            args[1].right = args[0].trackitems[current_index + 1]
            args[0].trackitems[current_index + 1].left = args[1]

    return wrapper


def ADD_MEDIA_LINK(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # print args
        # print kwargs
        func(*args, **kwargs)
        args[1].used.add(args[0])
        if args[1].reel:
            args[0].reel = args[1].reel

    return wrapper


def ADD_PARENT_LINK(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # print args
        # print kwargs
        func(*args, **kwargs)
        args[1].parent = args[0]

    return wrapper


def get_abs_time(obj, abs_time=None):
    if abs_time is None:
        abs_time = TIMECODE(0, fps=getattr(obj, 'fps', FRAMERATE(24.0)))
    if isinstance(obj, BASE_SCHEMA) and getattr(obj, 'parent', None):
        return abs_time + get_abs_time(obj.parent, abs_time=abs_time)

    else:
        return obj.target_in

class BASE_SCHEMA(object):
    fps = FRAMERATE(24.0)
    name = None
    label = None
    uuid = None
    parent = None
    target_in = None
    target_out = None

    @property
    def offset(self):
        return get_abs_time(self)

    def __init__(self, **kwargs):
        super(BASE_SCHEMA, self).__init__()
        self.uuid = str(uuid1())
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        if isinstance(other, BASE_SCHEMA) and other.uuid == self.uuid:
            return True
        else:
            return False

    def __repr__(self):
        all_param = [x for x in dir(self)
                     if not x.startswith('__')
                     and type(getattr(self, x)) != type(self.__init__)
                     and not isinstance(getattr(self, x), (BASE_SCHEMA, list))]
        result = ', '.join(['{}={}'.format(x, getattr(self, x)) for x in all_param])
        return '<{}>({})\n'.format(self.__class__.__name__, result)

    @property
    def duration(self):
        if self.target_in is not None and self.target_out is not None:
            return self.target_out - self.target_in
        return None


class BASE_MARKER(BASE_SCHEMA):
    category = None


class BASE_NTOE(BASE_SCHEMA):
    note = ''
    extra_info = {}


class BASE_MEDIA(BASE_SCHEMA):
    ref_id = None
    filename = None
    reel = None
    source_in = None
    source_out = None
    used = set()
    extra_info = {}

    @property
    def duration(self):
        if self.source_in is not None and self.source_out is not None:
            return self.source_out - self.source_in
        return None


class BASE_TRANSITION(BASE_SCHEMA):
    category = None


class BASE_TRACKITEM(BASE_SCHEMA):
    category = None
    speed = []
    left = None
    right = None
    left_transition = None
    right_transition = None
    notes = None
    markers = None

    @property
    def resolved_target_in(self):
        return self.left_transition.target_in \
            if getattr(getattr(self, 'left_transition', None), 'target_in', None) \
            else self.target_in

    @property
    def resolved_target_out(self):
        return self.right_transition.target_out \
            if getattr(getattr(self, 'right_transition', None), 'target_out', None) \
            else self.target_out

    @ADD_PARENT_LINK
    def add_note(self, note):
        if isinstance(note, BASE_NTOE):
            self.notes = self.notes if self.notes else []
            self.notes.append(note)
            return True
        return False

    def delete_note(self, note):
        if isinstance(note, BASE_NTOE):
            self.notes.remove(note)
            return True

        elif isinstance(note, basestring):
            delete_note = next((x for x in self.notes if x.name == note or x.uuid == note), None)
            if delete_note:
                self.notes.remove(delete_note)
                return True

        return False

    @ADD_PARENT_LINK
    def add_marker(self, marker):
        if isinstance(marker, BASE_MARKER):
            self.markers = self.markers if self.markers else []
            marker_tc_list = [x.target_in for x in self.markers]
            insert_pos = bisect.bisect_right(marker_tc_list, marker.target_in)
            self.markers.insert(insert_pos, marker_tc_list)
            return True
        return False

    def delete_mark(self, marker):
        if isinstance(marker, BASE_TRANSITION):
            self.markers.remove(marker)
            return True

        elif isinstance(marker, basestring):
            delete_marker = next((x for x in self.markers if x.name == marker or x.uuid == marker), None)
            if delete_marker:
                self.markers.remove(delete_marker)
                return True

        return False

    @ADD_PARENT_LINK
    def add_transition(self, transition, which):
        setattr(self, '{}_transition'.format(which), transition)

    def delete_transition(self, which):
        if isinstance(which, BASE_TRANSITION):
            if which == self.left_transition:
                self.left_transition = None
                return True
            if which == self.right_transition:
                self.right_transition = None
                return True
            return False

        elif isinstance(which, basestring):
            if which == 'left':
                self.left_transition = None
                return True
            if which == 'right':
                self.right_transition = None
                return True

        return False


class BASE_EFFECT(BASE_TRACKITEM):
    category = None
    extra_info = {}

class BASE_TEXT(BASE_EFFECT):
    message = None
    extra_info = {}


class BASE_COMPOUND(BASE_TRACKITEM):
    source_in = None
    source_out = None
    head = None
    tail = None
    compound = None

    @ADD_PARENT_LINK
    def add_compound(self, compound):
        if isinstance(compound, BASE_TIMELINE):
            self.compound = compound
            return True
        return False


class BASE_CLIP(BASE_TRACKITEM):
    source_in = None
    source_out = None
    head = None
    tail = None
    media = None
    reel = None
    long_reel = None

    @ADD_MEDIA_LINK
    def link_media(self, media):
        if isinstance(media, BASE_MEDIA):
            self.media = media
            return True
        return False

    def unlink_media(self):
        if self.media:
            self.media.used.remove(self)
            self.media = None

    @property
    def resolved_source_in(self):
        # todo: handle speed
        return self.source_in - (self.target_in - self.left_transition.target_in) \
            if getattr(getattr(self, 'left_transition', None), 'target_in', None) \
            else self.source_in

    @property
    def resolved_source_out(self):
        # todo: handle speed
        return self.source_out + (self.right_transition.target_out - self.target_out) \
            if getattr(getattr(self, 'right_transition', None), 'target_out', None) \
            else self.source_out


class BASE_TRACK(BASE_SCHEMA):
    id = None
    category = None
    trackitems = None

    def __getitem__(self, track_name):
        return next((x for x in self.trackitems if x.name == track_name or x.uuid == track_name), None)

    @ADD_PARENT_LINK
    @ADD_LEFT_RIGHT_LINK
    def add_trackitem(self, trackitem):
        if isinstance(trackitem, (BASE_TRACKITEM, BASE_COMPOUND)):
            self.trackitems = self.trackitems if self.trackitems else []
            tc_list = [x.target_in for x in self.trackitems]
            insert_pos = bisect.bisect_right(tc_list, trackitem.target_in)
            self.trackitems.insert(insert_pos, trackitem)

    def delete_trackitem(self, trackitem):
        if isinstance(track, BASE_TRACKITEM):
            try:
                self.trackitems.remove(track)
                return True
            except:
                return False

        elif isinstance(track, basestring):
            delete_track = self[track]
            if delete_track:
                self.trackitems.remove(delete_track)
                return True
            else:
                return False

        return False


class VIDEO_TRACK(BASE_TRACK):
    category = 'video'


class AUDIO_TRACK(BASE_TRACK):
    category = 'audio'

class EFFECT_TRACK(BASE_TRACK):
    category = 'effect'


class BASE_TIMELINE(BASE_SCHEMA):
    tracks = None

    def __getitem__(self, track_name):
        return next((x for x in self.tracks if x.name == track_name or x.uuid == track_name), None)

    def unpack(self):
        if isinstance(self.parent, BASE_COMPOUND):
            # todo: unpack a compound timeline
            pass

    @ADD_PARENT_LINK
    def add_track(self, track):
        if isinstance(track, BASE_TRACK):
            self.tracks = self.tracks if self.tracks else []
            self.tracks.append(track)
            return True
        return False

    def delete_track(self, track):
        if isinstance(track, BASE_TRACK):
            try:
                self.tracks.remove(track)
                return True
            except:
                return False

        elif isinstance(track, basestring):
            delete_track = self[track]
            if delete_track:
                self.tracks.remove(delete_track)
                return True
            else:
                return False

        return False


if __name__ == '__main__':
    timeline = BASE_TIMELINE()
    track = BASE_TRACK(name='haha')
    # print isinstance(track, BASE_SCHEMA)
    # print track
    timeline.add_track(track)
    # print track

    for x in range(3):
        clip = BASE_CLIP(target_in=TIMECODE(x), target_out=TIMECODE(x * x))
        track.add_trackitem(clip)

    print track.trackitems[2].duration
    # print track.trackitems[1].left
    # print track.trackitems[1].right

    # print timeline['haha']
    #
    # timeline.delete_track('haha')
    # print timeline.all_tracks
