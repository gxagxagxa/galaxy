#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from schema.BASE_SCHEMA import *
import re
from unipath import Path


class CMX3600_EDL(object):
    titleRegex = re.compile(r'^TITLE:\s+([\w\s]*)')
    fcpRegex = re.compile(r'^FCM:\s+([\w\s]*)')
    eventRegex = re.compile(
            r'(\d+)\s+([\w\.]+)\s+([\w\/]+)\s+(\w+)\s+(\d*)\s+(\d{1,2}:\d{1,2}:\d{1,2}[\:\;]\d{1,3})\s+(\d{1,2}:\d{1,2}:\d{1,2}[\:\;]\d{1,3})\s+(\d{1,2}:\d{1,2}:\d{1,2}[\:\;]\d{1,3})\s+(\d{1,2}:\d{1,2}:\d{1,2}[\:\;]\d{1,3})')
    auxRegex = re.compile(r'^\*')
    effectRegex = re.compile(r'^\* EFFECT NAME:\s+([\w\s]*)')
    fromClipNameRegex = re.compile(r'^\*\s?FROM CLIP NAME:\s+([\S ]*)')
    stillRegex = re.compile(r'^\*\s?FROM CLIP IS A STILL')
    problemRegex = re.compile(r'^\*\s?PROBLEM WITH EDIT:\s+([\w\s]*)')
    commentRegex = re.compile(r'^\*\s?COMMENT:\s+([\w\s]*)')
    filterRegex = re.compile(r'^\*\s?CLIP FILTER:\s+([\w\s]*)')
    toClipNameRegex = re.compile(r'^\*\s?TO CLIP NAME:\s+([\S ]*)')
    speedRegex = re.compile(r'M2\s+(\w+)\s+(\-?\d+\.\d+)\s+(\d{1,2}:\d{1,2}:\d{1,2}[\:\;]\d{1,3})')
    longReelRegex = re.compile(r'^FINAL CUT PRO REEL:\s+(\w+)\s+REPLACED BY:\s+(\w+)')

    def __init__(self, file_path, fps):
        super(CMX3600_EDL, self).__init__()
        self.fps = FRAMERATE(fps)
        if file_path:
            self.filename = Path(file_path)
            self.timeline = BASE_TIMELINE(fps=self.fps, target_in=TIMECODE(0, fps=self.fps))
            self.timeline.add_track(VIDEO_TRACK(target_in=TIMECODE(0, fps=self.fps)))
            self.parse()

    def parse(self):
        edl_list = None
        try:
            with open(self.filename, 'r') as edl_file:
                edl_list = edl_file.readlines()
                edl_list = map(str.strip, edl_list)
        except Exception as e:
            raise e

        if not edl_list:
            return None

        edl_track = self.timeline.tracks[0]
        for index, content in enumerate(edl_list):
            # print content
            if self.eventRegex.match(content):
                event_values = self.eventRegex.match(content).groups()
                new_clip = BASE_CLIP(reel=event_values[1],
                                     source_in=TIMECODE(event_values[5], fps=self.fps),
                                     source_out=TIMECODE(event_values[6], fps=self.fps),
                                     target_in=TIMECODE(event_values[7], fps=self.fps),
                                     target_out=TIMECODE(event_values[8], fps=self.fps),
                                     speed=[],
                                     note=[])
                edl_track.add_trackitem(new_clip)

                if event_values[4]:
                    trans = BASE_TRANSITION(category='dissolve',
                                            target_in=TIMECODE(event_values[7], fps=self.fps),
                                            target_out=TIMECODE(event_values[7], fps=self.fps)
                                                       + int(event_values[4]))
                    new_clip.target_in = new_clip.target_in + trans.duration.framecount() / 2
                    new_clip.source_in = new_clip.source_in + trans.duration.framecount() / 2
                    new_clip.add_transition(trans, 'left')

                    trans2 = BASE_TRANSITION(category='dissolve',
                                             target_in=TIMECODE(event_values[7], fps=self.fps),
                                             target_out=TIMECODE(event_values[7], fps=self.fps)
                                                        + int(event_values[4]))
                    new_clip.left.target_out = new_clip.left.target_out + trans2.duration.framecount() / 2
                    new_clip.left.source_out = new_clip.left.source_out + trans2.duration.framecount() / 2
                    new_clip.left.add_transition(trans2, 'right')
                    continue

            from_clip_match = self.fromClipNameRegex.match(content)
            if from_clip_match:
                from_index = -2 if edl_track.trackitems[-1].left_transition else -1
                edl_track.trackitems[from_index].name = from_clip_match.groups()[-1]
                continue

            to_clip_match = self.toClipNameRegex.match(content)
            if to_clip_match:
                edl_track.trackitems[-1].name = to_clip_match.groups()[-1]
                continue

            still_match = self.stillRegex.match(content)
            if still_match:
                edl_track.trackitems[-1].speed = 0.0
                continue

            comment_match = self.commentRegex.match(content)
            if comment_match:
                edl_track.trackitems[-1].add_note(BASE_NTOE(name=comment_match.groups()[-1],
                                                            note=comment_match.groups()[-1]))
                continue

            speed_match = self.speedRegex.match(content)
            if speed_match:
                # print '-------------'
                # print new_clip.speed
                speedvalues = speed_match.groups()
                if edl_track.trackitems[-1].left_transition:
                    match_index = -2 \
                        if edl_track.trackitems[-2].reel == speedvalues[0] \
                           and len(edl_track.trackitems[-2].speed) == 0 \
                        else -1

                    edl_track.trackitems[match_index].speed.append(
                            (TIMECODE(speedvalues[-1], fps=self.fps),
                             float(speedvalues[1]) / self.fps))
                else:
                    edl_track.trackitems[-1].speed.append((TIMECODE(speedvalues[-1], fps=self.fps),
                                                           float(speedvalues[1]) / self.fps))
                continue

            long_match = self.longReelRegex.match(content)
            if long_match:
                longvalues = long_match.groups()
                if edl_track.trackitems[-1].left_transition:
                    match_index = -2 if edl_track.trackitems[-2].reel == longvalues[0] else -1
                    edl_track.trackitems[match_index].long_reel = longvalues[0]
                else:
                    edl_track.trackitems[-1].long_reel = longvalues[0]
                continue

    @classmethod
    def read_from_file(cls, file_path, fps=24.0):
        return cls(file_path, fps)

    def write_to_file(self, file_path, title=None, fps=24.0):
        edl_string = 'TITLE: {}\nFCM: NON-FROP FRAME\n'.format(str(uuid1()))
        content_string = ''
        total = len(self.timeline.tracks[0].trackitems)
        start_index = 1
        for index, x in enumerate(self.timeline.tracks[0].trackitems):
            if x.left_transition:
                part_string = '{event:04d}  {reel}  {video}  {cut}  {src_in}  {src_out}  {dst_in}  {dst_out}\n'
                content_string += part_string.format(event=start_index,
                                                     reel=x.left.reel if x.left.reel else 'AUX',
                                                     video='V',
                                                     cut='C',
                                                     src_in=x.left.source_in.timecode() if not x.left.left_transition else (
                                                         x.left.source_out - x.left.right_transition.duration / 2).timecode(),
                                                     src_out=(
                                                         x.left.source_out - x.left.right_transition.duration / 2).timecode(),
                                                     dst_in=(
                                                         x.left.offset + x.left.target_in).timecode() if not x.left.left_transition else (
                                                         x.left.target_out + x.left.offset - x.left.right_transition.duration / 2).timecode(),
                                                     dst_out=(
                                                         x.left.target_out - x.left.right_transition.duration / 2 + x.left.offset).timecode())

                part_string = '{event:04d}  {reel}  {video}  {cut}  {dis:03d}  {src_in}  {src_out}  {dst_in}  {dst_out}\n'
                content_string += part_string.format(event=start_index,
                                                     reel=x.reel if x.reel else 'AUX',
                                                     video='V',
                                                     cut='D',
                                                     dis=x.left_transition.duration.framecount(),
                                                     src_in=x.resolved_source_in.timecode(),
                                                     src_out=(
                                                         x.resolved_source_out).timecode() if not x.right_transition else (
                                                         x.resolved_source_out - x.right_transition.duration).timecode(),
                                                     dst_in=(x.resolved_target_in + x.offset).timecode(),
                                                     dst_out=(
                                                         x.resolved_target_out + x.offset).timecode() if not x.right_transition else (
                                                         x.right_transition.target_in + x.offset).timecode()
                                                     )

                content_string += 'M2  {reel}  {dur:05.1f}  {start}\n' \
                    .format(reel=x.left.reel if x.left.reel else 'AUX',
                            dur=x.left.speed[0][1] * x.left.fps,
                            start=x.left.source_in.timecode() if not x.left.left_transition else (
                                x.left.source_out - x.left.right_transition.duration / 2).timecode()) \
                    if x.left.speed else ''
                content_string += 'M2  {reel}  {dur:05.1f}  {start}\n' \
                    .format(reel=x.reel if x.reel else 'AUX',
                            dur=x.speed[0][1] * x.fps,
                            start=x.resolved_source_in.timecode()) \
                    if x.speed else ''
                content_string += '* FROM CLIP NAME:  {}\n'.format(x.left.name) \
                    if x.left.name else ''
                content_string += '* TO CLIP NAME:  {}\n\n'.format(x.name) if x.name else ''
                start_index += 1


            elif x.left_transition is None and x.right_transition is None:
                part_string = '{event:04d}  {reel}  {video}  {cut}  {src_in}  {src_out}  {dst_in}  {dst_out}\n'
                content_string += part_string.format(event=start_index,
                                                     reel=x.reel if x.reel else 'AUX',
                                                     video='V',
                                                     cut='C',
                                                     src_in=x.source_in.timecode(),
                                                     src_out=(x.source_out).timecode(),
                                                     dst_in=(x.target_in + x.offset).timecode(),
                                                     dst_out=(x.target_out + x.offset).timecode())

                content_string += 'M2  {reel}  {dur:05.1f}  {start}\n' \
                    .format(reel=x.reel if x.reel else 'AUX',
                            dur=x.speed[0][1] * x.fps,
                            start=x.source_in.timecode()) \
                    if x.speed else ''
                content_string += '* FROM CLIP NAME:  {}\n\n'.format(x.name) if x.name else ''
                start_index += 1

        with open(file_path, 'w') as edl_file:
            edl_file.write(edl_string + content_string)


if __name__ == '__main__':
    from pprint import pprint

    # print TIMECODE(95.5, fps=24.0)
    edl = CMX3600_EDL.read_from_file('/Users/guoxiaoao/Desktop/EDL_TEST/Sequence 1/Video 2.edl')

    print edl.timeline.tracks[0].trackitems


    # edl.write_to_file('/Users/guoxiaoao/Desktop/EDL_TEST/fafafafa22.edl')
    # for x in edl.timeline.tracks[0].trackitems:
    #     # print x.name, x.reel, x.target_in, x.target_out
    #     print x.left_transition
    #     print x.right_transition
    #     print '========'
