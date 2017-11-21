#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import hiero.core as hcore
import hiero.ui as hui
from schema.BASE_SCHEMA import *


class HIERO_TRACK(object):
    def __init__(self, sequence):
        super(HIERO_TRACK, self).__init__()
        if sequence:
            self.sequence = sequence
            self.timeline = None
            self.files = {}
            self.parse()

    def _parse_transition(self, hiero_transition):
        transition = BASE_TRANSITION()
        transition.target_in = TIMECODE(float(hiero_transition.timelineIn()), fps=self.timeline.fps)
        transition.target_out = TIMECODE(float(hiero_transition.timelineOut() + 1), fps=self.timeline.fps)
        return transition

    def _parse_media(self, hiero_clip):
        if self.files.get(hiero_clip.mediaSource().fileinfos()[0].filename(), None):
            return self.files.get(hiero_clip.mediaSource().fileinfos()[0].filename(), None)

        media = BASE_MEDIA()
        media.name = hiero_clip.name()
        media.fps = FRAMERATE(float(hiero_clip.mediaSource().metadata().dict().get('foundry.source.framerate',
                                                                                        hiero_clip.framerate().toFloat())))
        media.reel = hiero_clip.mediaSource().metadata().dict().get('foundry.source.reelID', None)
        media.filename = hiero_clip.mediaSource().fileinfos()[0].filename()
        media.source_in = TIMECODE(hiero_clip.mediaSource().metadata().dict().get('foundry.source.startTC', None),
                                        fps=media.fps)
        media.source_out = TIMECODE(
                float(hiero_clip.mediaSource().metadata().dict().get('foundry.source.duration', None)),
                fps=media.fps) + media.source_in
        return media

    def _parse_trackitem(self, hiero_trackitem):
        trackitem = BASE_CLIP(speed=[])
        trackitem.name = hiero_trackitem.name()
        trackitem.reel = hiero_trackitem.source().mediaSource().metadata().dict().get('foundry.source.reelID', None)
        trackitem.source_in = TIMECODE(float(hiero_trackitem.sourceIn()), fps=self.timeline.fps)
        trackitem.source_out = TIMECODE(float(hiero_trackitem.sourceOut() + 1), fps=self.timeline.fps)
        trackitem.target_in = TIMECODE(float(hiero_trackitem.timelineIn()), fps=self.timeline.fps)
        trackitem.target_out = TIMECODE(float(hiero_trackitem.timelineOut() + 1), fps=self.timeline.fps)

        if hiero_trackitem.inTransition():
            trackitem.add_transition(self._parse_transition(hiero_trackitem.inTransition()), 'left')
        if hiero_trackitem.outTransition():
            trackitem.add_transition(self._parse_transition(hiero_trackitem.outTransition()), 'right')

        if not hiero_trackitem.source().mediaSource().isOffline():
            trackitem.link_media(self._parse_media(hiero_trackitem.source()))
            trackitem.source_in = trackitem.media.source_in + trackitem.source_in
            trackitem.source_out = trackitem.media.source_in + trackitem.source_out

        if hiero_trackitem.playbackSpeed() != 1.0:
            trackitem.speed.append((trackitem.source_in, float(hiero_trackitem.playbackSpeed())))

        return trackitem

    def _parse_effect(self, hiero_effect):
        effect = None
        if hiero_effect.node().Class() == 'Text2':
            effect = BASE_TEXT()
        else:
            effect = BASE_EFFECT(extra_info={})

        effect.name = hiero_effect.name()
        effect.target_in = TIMECODE(float(hiero_effect.timelineIn()), fps=self.timeline.fps)
        effect.target_out = TIMECODE(float(hiero_effect.timelineOut() + 1), fps=self.timeline.fps)
        effect.source_in = TIMECODE(240.0, fps=self.timeline.fps)
        effect.source_out = effect.source_in + effect.duration
        if isinstance(effect, BASE_TEXT):
            node = hiero_effect.node()
            effect.message = node['message'].value()

        return effect

    def _parse_track(self, hiero_track, clip_track=True):
        videotrack = VIDEO_TRACK()
        videotrack.name = hiero_track.name() if clip_track else 'effect_track'
        videotrack.fps = self.timeline.fps
        videotrack.target_in = TIMECODE(0, fps=videotrack.fps)

        if clip_track:
            for trackitem in hiero_track.items():
                videotrack.add_trackitem(self._parse_trackitem(trackitem))
        else:
            for effect in hiero_track:
                print effect
                videotrack.add_trackitem(self._parse_effect(effect))

        return videotrack

    def parse(self):
        self.timeline = BASE_TIMELINE()
        self.timeline.name = self.sequence.name()
        self.timeline.fps = FRAMERATE(self.sequence.framerate().toFloat())
        self.timeline.target_in = TIMECODE(float(self.sequence.timecodeStart()), fps=self.timeline.fps)

        for track in self.sequence.videoTracks():
            if track.items():
                self.timeline.add_track(self._parse_track(track))
            if track.subTrackItems():
                for sub_track in track.subTrackItems():
                    self.timeline.add_track(self._parse_track(sub_track, clip_track=False))

    def _hiero_trackitem(self, clip, h_trackitem):
        print clip.source_in.framecount(), h_trackitem.source().sourceIn()
        h_trackitem.setSourceIn(clip.source_in.framecount() - h_trackitem.source().sourceIn())
        h_trackitem.setSourceOut(clip.source_out.framecount() - h_trackitem.source().sourceIn() - 1)
        h_trackitem.setTimelineIn(clip.target_in.framecount())
        h_trackitem.setTimelineOut(clip.target_out.framecount() - 1)

    def _hiero_mediasource(self, trackitem):
        if trackitem.media:
            media = trackitem.media
            # print 'find file'
            # print media.source_out , media.source_in, media.duration
            h_mediasource = \
                hcore.MediaSource.createOfflineVideoMediaSource(
                        APATH(media.filename).to_pattern() if media.filename else 'no_name',
                        media.source_in.framecount(),
                        media.duration.framecount(),
                        hcore.TimeBase(media.fps),
                        media.source_in.framecount()
                )
        else:
            h_mediasource = \
                hcore.MediaSource.createOfflineVideoMediaSource(
                        trackitem.name if trackitem.name else 'no_name',
                        trackitem.source_in.framecount(),
                        (trackitem.source_out - trackitem.source_in).framecount(),
                        hcore.TimeBase(trackitem.fps),
                        trackitem.source_in.framecount()
                )
        # print h_mediasource
        return h_mediasource

    def _hiero_clip(self, trackitem):
        # if trackitem.media:
        #     print trackitem.source_in, trackitem.source_out, trackitem.media.source_in
        #
        #     clip_in = (trackitem.source_in - trackitem.media.source_in).framecount()
        #     clip_out = (trackitem.source_out - trackitem.media.source_in).framecount() - 1
        #     h_clip = hcore.Clip(self._hiero_mediasource(trackitem), clip_in, clip_out)
        # else:
        h_clip = hcore.Clip(self._hiero_mediasource(trackitem))
        return h_clip

    def _hiero_transition(self, track, h_track):
        if not h_track.items():
            return

        for index, trackitem in enumerate(track.trackitems):
            if trackitem.left_transition and not trackitem.left:
                h_transition = hcore.Transition.createFadeInTransition(h_track.items()[index],
                                                                       trackitem.left_transition.duration.framecount())
                h_track.addTransition(h_transition)

            if trackitem.right_transition and \
                    getattr(getattr(trackitem, 'right'), 'left_transition', None) and \
                            trackitem.right_transition.target_in == trackitem.right.left_transition.target_in and \
                            trackitem.right_transition.target_out == trackitem.right.left_transition.target_out:
                h_transition = \
                    hcore.Transition.createDissolveTransition(h_track.items()[index],
                                                              h_track.items()[index + 1],
                                                              (trackitem.right_transition.duration / 2).framecount(),
                                                              (trackitem.right_transition.duration / 2).framecount(),
                                                              )
                h_track.addTransition(h_transition)

            if trackitem.right_transition and not trackitem.right:
                h_transition = hcore.Transition.createFadeOutTransition(h_track.items()[index],
                                                                        trackitem.right_transition.duration.framecount())
                h_track.addTransition(h_transition)

    def _hiero_text_effect(self, effect, h_track):
        h_effect = h_track.createEffect('Text2',
                                        timelineIn=effect.target_in.framecount(),
                                        timelineOut=effect.target_out.framecount() - 1)
        h_node = h_effect.node()
        h_node['message'].setValue(effect.message.encode('utf-8') if effect.message else '')
        return h_effect

    def _hiero_video_track(self, track):
        h_track = hcore.VideoTrack(track.name if track.name else '')

        for trackitem in track.trackitems:
            #     if isinstance(trackitem, BASE_CLIP):
            #         h_trackitem = h_track.createTrackItem(trackitem.name)
            #         h_trackitem.setSource(self._hiero_clip(trackitem))
            #         self._hiero_trackitem(trackitem, h_trackitem)
            #         h_track.addItem(h_trackitem)

            if isinstance(trackitem, BASE_TEXT):
                h_effect = self._hiero_text_effect(trackitem, h_track)

        # self._hiero_transition(track, h_track)
        return h_track

    def _hiero_sequence(self, timeline):
        h_project = hcore.projects()[-1]
        h_root_bin = h_project.clipsBin()

        h_sequence = hcore.Sequence(timeline.name if timeline.name else 'untitled')
        h_sequence.setFramerate(timeline.fps)
        h_sequence.setTimecodeStart(timeline.target_in.framecount())

        for track in timeline.tracks:
            h_sequence.addTrack(self._hiero_video_track(track))

        h_root_bin.addItem(hcore.BinItem(h_sequence))
        return h_sequence

    def write_to_timeline(self):
        return self._hiero_sequence(self.timeline)

    @classmethod
    def read_from_timeline(cls, sequence=None):
        return cls(sequence if sequence else hui.activeSequence())


if __name__ == '__main__':
    test = HIERO_TRACK.read_from_timeline()
    # print test.timeline.tracks[0].trackitems[0]

    import MORE_CORE.MORE_TIMELINE.FCP7_XML as F7

    reload(F7)

    haha = F7.FCP7_XML(None)
    haha.timeline = test.timeline
    haha.write_to_file('/Users/guoxiaoao/Desktop/EDL_TEST/from_self_generate.xml')
