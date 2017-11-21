#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import lxml.etree as et
from schema.BASE_SCHEMA import *
import urllib
import urlparse


class FCP7_XML(object):
    def __init__(self, file_path):
        super(FCP7_XML, self).__init__()
        self.filename = file_path
        if file_path:
            self.timeline = None
            self.files = {}
            self.parse()

    def _parse_file(self, element):
        if element.get('id') in self.files.keys():
            return self.files[element.get('id')]

        new_file = BASE_MEDIA()
        new_file.ref_id = element.get('id')
        new_file.name = getattr(element.find('./name'), 'text', None)
        new_file.filename = getattr(element.find('./pathurl'), 'text', None)
        new_file.filename = urllib.url2pathname(
                urlparse.urlparse(new_file.filename).path) if new_file.filename else None
        new_file.fps = FRAMERATE(getattr(element.find('./rate/timebase'), 'text', self.fps))
        new_file.source_in = TIMECODE(getattr(element.find('./timecode/string'), 'text', '01:00:00:00'),
                                           fps=new_file.fps)
        new_file.source_out = new_file.source_in + TIMECODE(int(getattr(element.find('./duration'), 'text', '0')),
                                                                 fps=new_file.fps)
        new_file.reel = getattr(element.find('./timecode/reel/name'), 'text', None)

        self.files[new_file.ref_id] = new_file
        return new_file

    def _parse_transition(self, element):
        new_trans = BASE_TRANSITION()
        new_trans.fps = FRAMERATE(getattr(element.find('./rate/timebase'), 'text', self.fps))
        new_trans.target_in = TIMECODE(int(element.find('./start').text), fps=new_trans.fps)
        new_trans.target_out = TIMECODE(int(element.find('./end').text), fps=new_trans.fps)
        new_trans.category = getattr(element.find('./effect/effectcategory'), 'text', 'dissolve')
        new_trans.align = getattr(element.find('./alignment'), 'text', 'center')
        return new_trans

    def _parse_clip(self, element):
        new_clip = BASE_CLIP(speed=[], note=[])
        new_clip.name = element.find('./name').text
        new_clip.fps = FRAMERATE(float(element.find('./rate/timebase').text))
        offset_in = TIMECODE(int(element.find('./in').text), fps=new_clip.fps)
        offset_out = TIMECODE(int(element.find('./out').text), fps=new_clip.fps)

        new_clip.target_in = TIMECODE(int(element.find('./start').text), fps=self.fps)
        if new_clip.target_in < 0:
            new_trans = self._parse_transition(element.getprevious())
            new_clip.add_transition(new_trans, 'left')
            if new_trans.align == 'center':
                new_clip.target_in = new_trans.target_in + new_trans.duration.framecount() / 2
                offset_in = offset_in + new_trans.duration.framecount() / 2
            else:
                new_clip.target_in = new_trans.target_in

        new_clip.target_out = TIMECODE(int(element.find('./end').text), fps=self.fps)
        if new_clip.target_out < 0:
            new_trans = self._parse_transition(element.getnext())
            new_clip.add_transition(new_trans, 'right')
            if new_trans.align == 'center':
                new_clip.target_out = new_trans.target_out - new_trans.duration.framecount() / 2
                offset_out = offset_out - new_trans.duration.framecount() / 2
            else:
                new_clip.target_out = new_trans.target_out
        else:
            new_clip.target_out = new_clip.target_out

        # print new_clip.target_in, new_clip.target_out
        new_file = None
        if element.find('./file') is not None:
            new_file = self._parse_file(element.find('./file'))
            new_clip.link_media(new_file)

        retime = next((x for x in element.findall('./filter') if x.find('./effect/effectid').text == 'timeremap'), None)
        if retime is not None:
            speed = next(
                    (x for x in retime.findall('./effect/parameter') if x.find('./parameterid').text == 'graphdict'),
                    None)
            if speed is not None:
                new_clip.speed.append(
                        (TIMECODE(int(speed.find('./keyframe/when').text),
                                       fps=new_file.fps if new_file else self.fps) + (
                             new_file.source_in if new_file else 0),
                         (float(speed.find('./keyframe').getnext().find('./value').text) - float(
                                 speed.find('./keyframe/value').text)) / (
                             float(speed.find('./keyframe').getnext().find('./when').text) - float(
                                     speed.find('./keyframe/when').text))))

                new_clip.source_in = offset_in * new_clip.speed[0][1] + (new_file.source_in if new_file else 0)
                new_clip.source_out = (offset_out - offset_in) * new_clip.speed[0][1] + new_clip.source_in
        else:
            new_clip.source_in = offset_in + (new_file.source_in if new_file else 0)
            new_clip.source_out = offset_out + (new_file.source_in if new_file else 0)

        return new_clip

    def _parse_effect(self, element):
        category = getattr(element.find('./effect/effectcategory'), 'text', None)
        if category == 'Text':
            new_effect = BASE_TEXT(extra_info={})
        else:
            new_effect = BASE_EFFECT(extra_info={})

        new_effect.name = getattr(element.find('./name'), 'text', None)
        new_effect.category = category
        new_effect.fps = FRAMERATE(getattr(element.find('./rate/timebase'), 'text', self.fps))
        new_effect.source_in = TIMECODE(int(element.find('./in').text), fps=new_effect.fps)
        new_effect.source_out = TIMECODE(int(element.find('./out').text), fps=new_effect.fps)

        new_effect.target_in = TIMECODE(int(element.find('./start').text), fps=self.fps)
        if new_effect.target_in < 0:
            new_trans = self._parse_transition(element.getprevious())
            new_effect.add_transition(new_trans, 'left')
            if new_trans.align == 'center':
                new_effect.target_in = new_trans.target_in + new_trans.duration.framecount() / 2
                new_effect.source_in = new_effect.source_in + new_trans.duration.framecount() / 2
            else:
                new_effect.target_in = new_trans.target_in

        new_effect.target_out = TIMECODE(int(element.find('./end').text), fps=self.fps)
        if new_effect.target_out < 0:
            new_trans = self._parse_transition(element.getnext())
            new_effect.add_transition(new_trans, 'right')
            if new_trans.align == 'center':
                new_effect.target_out = new_trans.target_out - new_trans.duration.framecount() / 2
                new_effect.source_out = new_effect.source_out - new_trans.duration.framecount() / 2
            else:
                new_effect.target_out = new_trans.target_out
        else:
            new_effect.target_out = new_effect.target_out

        if new_effect.category == 'Text':
            text_message = next((x for x in element.findall('./effect/parameter') if x.find('./name').text == 'Text'),
                                None)
            if text_message is not None:
                new_effect.message = getattr(text_message.find('./value'), 'text', None)

        return new_effect

    def parse(self):
        xml_tree = et.parse(self.filename)
        root = xml_tree.getroot()
        self.fps = FRAMERATE(float(root.find('./sequence/rate/timebase').text))
        self.timeline = BASE_TIMELINE(name=root.find('./sequence/name').text,
                                      fps=self.fps,
                                      target_in=TIMECODE(root.find('./sequence/timecode/string').text,
                                                              fps=self.fps))
        # print self.timeline
        for track in root.findall('./sequence/media/video/track'):
            new_track = VIDEO_TRACK(target_in=TIMECODE(0, fps=self.fps))
            self.timeline.add_track(new_track)
            for item in track:
                if item.tag == 'clipitem':
                    new_clip = self._parse_clip(item)
                    new_track.add_trackitem(new_clip)

                if item.tag == 'generatoritem':
                    new_effect = self._parse_effect(item)
                    new_track.add_trackitem(new_effect)

    @classmethod
    def read_from_file(cls, file_path):
        return cls(file_path)

    def _xml_track(self, track):
        element = et.Element('track')
        return element

    def _xml_rate(self, framerate):
        element = et.Element('rate')
        et.SubElement(element, 'ntsc').text = 'FALSE'
        et.SubElement(element, 'timebase').text = str(int(framerate) if framerate.is_integer() else round(framerate, 2))
        return element

    def _xml_timecode(self, framerate, timecode, reel=None):
        element = et.Element('timecode')
        element.append(self._xml_rate(framerate))
        et.SubElement(element, 'string').text = timecode.timecode()
        et.SubElement(element, 'frame').text = str(timecode.framecount())
        et.SubElement(element, 'source').text = 'source'
        et.SubElement(element, 'displayformat').text = 'NDF'
        if reel:
            reel_element = et.SubElement(element, 'reel')
            et.SubElement(reel_element, 'name').text = reel
        return element

    def _xml_codec(self, name=None):
        name = name if name else 'Apple ProRes 422'
        codec = et.Element('codec')
        et.SubElement(codec, 'name').text = name
        appspecificdata = et.SubElement(codec, 'appspecificdata')
        et.SubElement(appspecificdata, 'appname').text = 'Final Cut Pro'
        et.SubElement(appspecificdata, 'appmanufacturer').text = 'Apple Inc.'
        et.SubElement(appspecificdata, 'appversion').text = '7.0'
        data = et.SubElement(appspecificdata, 'data')
        qtcodec = et.SubElement(data, 'qtcodec')
        et.SubElement(qtcodec, 'codecname').text = 'Apple ProRes 422'
        et.SubElement(qtcodec, 'codectypename').text = 'Apple ProRes 422 (HQ)'
        et.SubElement(qtcodec, 'codectypecode').text = 'apch'
        et.SubElement(qtcodec, 'codecvendorcode').text = 'appl'
        et.SubElement(qtcodec, 'spatialquality').text = '1023'
        et.SubElement(qtcodec, 'temporalquality').text = '0'
        et.SubElement(qtcodec, 'keyframerate').text = '0'
        et.SubElement(qtcodec, 'datarate').text = '0'
        return codec

    def _xml_appspecificdata(self):
        appspecificdata = et.Element('appspecificdata')
        et.SubElement(appspecificdata, 'appname').text = 'Final Cut Pro'
        et.SubElement(appspecificdata, 'appmanufacturer').text = 'Apple Inc.'
        et.SubElement(appspecificdata, 'appversion').text = '7.0'
        data = et.SubElement(appspecificdata, 'data')
        fcpimageprocessing = et.SubElement(data, 'fcpimageprocessing')
        et.SubElement(fcpimageprocessing, 'useyuv').text = 'TRUE'
        et.SubElement(fcpimageprocessing, 'usesuperwhite').text = 'TRUE'
        et.SubElement(fcpimageprocessing, 'rendermode').text = 'Float10BPP'
        return appspecificdata

    def _xml_format(self):
        format_element = et.Element('format')
        samplecharacteristics = et.SubElement(format_element, 'samplecharacteristics')
        et.SubElement(samplecharacteristics, 'width').text = '1920'
        et.SubElement(samplecharacteristics, 'height').text = '1080'
        et.SubElement(samplecharacteristics, 'anamorphic').text = 'FALSE'
        et.SubElement(samplecharacteristics, 'pixelaspectratio').text = 'Square'
        et.SubElement(samplecharacteristics, 'fielddominance').text = 'none'
        samplecharacteristics.append(self._xml_rate(self.timeline.fps))
        et.SubElement(samplecharacteristics, 'colordepth').text = '24'
        samplecharacteristics.append(self._xml_codec())
        format_element.append(self._xml_appspecificdata())
        return format_element

    def _xml_file(self, media):
        file_element = et.Element('file', id=media.uuid)
        et.SubElement(file_element, 'name').text = media.name
        if media.filename:
            et.SubElement(file_element, 'pathurl').text = urlparse.urljoin('file:', urllib.pathname2url(media.filename))
        file_element.append(self._xml_rate(media.fps if media.fps else self.timeline.fps))
        et.SubElement(file_element, 'duration').text = str(media.duration.framecount())
        file_element.append(self._xml_timecode(media.source_in.fps, media.source_in, reel=media.reel))

        return file_element

    def _xml_parameter(self, id, name, valuemin=None, valuemax=None, value=None):
        parameter = et.Element('parameter')
        et.SubElement(parameter, 'parameterid').text = id
        et.SubElement(parameter, 'name').text = name
        if valuemin:
            et.SubElement(parameter, 'valuemin').text = valuemin
        if valuemax:
            et.SubElement(parameter, 'valuemax').text = valuemax
        if value:
            et.SubElement(parameter, 'value').text = value

        return parameter

    def _xml_speed_filter(self, speed):
        filter_element = et.Element('filter')
        effect_element = et.SubElement(filter_element, 'effect')
        et.SubElement(effect_element, 'name').text = 'Time Remap'
        et.SubElement(effect_element, 'effectid').text = 'timeremap'
        et.SubElement(effect_element, 'effectcategory').text = 'motion'
        et.SubElement(effect_element, 'effecttype').text = 'motion'
        et.SubElement(effect_element, 'mediatype').text = 'video'

        effect_element.append(self._xml_parameter('speed', 'speed',
                                                  valuemin='-10000',
                                                  valuemax='10000',
                                                  value=str(int(round(speed[1] * 100, 0)))))
        effect_element.append(self._xml_parameter('reverse', 'reverse', value='TRUE' if speed[1] < 0 else 'FALSE'))
        return filter_element

    def _xml_text_effect(self, string, font=None, font_size=36, effect_id='Text'):
        effect_element = et.Element('effect')
        et.SubElement(effect_element, 'name').text = 'Text'
        et.SubElement(effect_element, 'effectid').text = effect_id
        et.SubElement(effect_element, 'effectcategory').text = 'Text'
        et.SubElement(effect_element, 'effectcategory').text = 'Text'
        et.SubElement(effect_element, 'effecttype').text = 'generator'
        et.SubElement(effect_element, 'mediatype').text = 'video'
        effect_element.append(self._xml_parameter('str', 'Text', value=string))
        if font:
            effect_element.append(self._xml_parameter('fontname', 'Font', value=str(font)))

        effect_element.append(self._xml_parameter('fontsize', 'Size',
                                                  valuemin='0', valuemax='1000', value=str(font_size)))
        return effect_element

    def _xml_generatoritem(self, text):
        generatoritem = et.Element('generatoritem', id=text.uuid)
        et.SubElement(generatoritem, 'name').text = text.message if text.message else 'Text'
        et.SubElement(generatoritem, 'duration').text = str((text.duration * 2).framecount())
        generatoritem.append(self._xml_rate(text.fps))
        et.SubElement(generatoritem, 'in').text = str(text.source_in.framecount())
        et.SubElement(generatoritem, 'out').text = str(text.source_out.framecount())
        et.SubElement(generatoritem, 'start').text = '-1' if text.left_transition else str(text.target_in.framecount())
        et.SubElement(generatoritem, 'end').text = '-1' if text.right_transition else str(text.target_out.framecount())
        et.SubElement(generatoritem, 'anamorphic').text = 'FALSE'
        et.SubElement(generatoritem, 'alphatype').text = 'black'
        et.SubElement(generatoritem, 'enable').text = 'true'
        generatoritem.append(self._xml_text_effect(text.message))
        return generatoritem

    def _xml_transitionitem(self, transition):
        transitionitem = et.Element('transitionitem')
        transitionitem.append(self._xml_rate(transition.fps))
        et.SubElement(transitionitem, 'start').text = str(transition.target_in.framecount())
        et.SubElement(transitionitem, 'end').text = str(transition.target_out.framecount())
        et.SubElement(transitionitem, 'alignment').text = 'center'
        effect_element = et.SubElement(transitionitem, 'effect')
        et.SubElement(effect_element, 'name').text = 'Cross Dissolve'
        et.SubElement(effect_element, 'effectid').text = 'Cross Dissolve'
        et.SubElement(effect_element, 'effectcategory').text = 'Dissolve'
        et.SubElement(effect_element, 'effecttype').text = 'transition'
        et.SubElement(effect_element, 'mediatype').text = 'video'
        et.SubElement(effect_element, 'wipecode').text = '0'
        et.SubElement(effect_element, 'wipeaccuracy').text = '100'
        et.SubElement(effect_element, 'startratio').text = '0'
        et.SubElement(effect_element, 'endratio').text = '1'
        et.SubElement(effect_element, 'reverse').text = 'FALSE'

        return transitionitem

    def _xml_clipitem(self, clip):
        clipitem = et.Element('clipitem', id=clip.uuid)
        et.SubElement(clipitem, 'name').text = clip.name
        if getattr(clip, 'media', None):
            xml_in = clip.source_in - clip.media.source_in
            duration = clip.media.duration
            if clip.speed:
                xml_in = (clip.source_in - clip.speed[0][0]) / clip.speed[0][1]
                duration = duration / clip.speed[0][1]

        else:
            xml_in = clip.source_in
            duration = clip.source_out

        et.SubElement(clipitem, 'duration').text = str(duration.framecount())
        clipitem.append(self._xml_rate(clip.media.fps if clip.media else self.timeline.fps))

        et.SubElement(clipitem, 'in').text = str(xml_in.framecount())
        et.SubElement(clipitem, 'out').text = str((xml_in + clip.duration).framecount())
        et.SubElement(clipitem, 'start').text = '-1' if clip.left_transition else str(clip.target_in.framecount())
        et.SubElement(clipitem, 'end').text = '-1' if clip.right_transition else str(clip.target_out.framecount())
        et.SubElement(clipitem, 'pixelaspectratio').text = 'Square'
        et.SubElement(clipitem, 'enabled').text = 'TRUE'
        et.SubElement(clipitem, 'anamorphic').text = 'FALSE'
        et.SubElement(clipitem, 'alphatype').text = 'none'
        if clip.media:
            clipitem.append(self._xml_file(clip.media))

        if clip.speed:
            clipitem.append(self._xml_speed_filter(clip.speed[0]))

        return clipitem

    def _xml_sequence(self, timeline):
        sequence = et.Element('sequence', id=timeline.name if timeline.name else timeline.uuid)
        et.SubElement(sequence, 'uuid').text = timeline.uuid
        et.SubElement(sequence, 'updatebehavior').text = 'add'
        et.SubElement(sequence, 'name').text = timeline.name if timeline.name else 'untitled'
        et.SubElement(sequence, 'duration').text = '-1'
        sequence.append(self._xml_rate(self.timeline.fps))
        sequence.append(self._xml_timecode(self.timeline.fps, self.timeline.target_in))
        et.SubElement(sequence, 'in').text = '-1'
        et.SubElement(sequence, 'out').text = '-1'
        media_element = et.SubElement(sequence, 'media')
        video_element = et.SubElement(media_element, 'video')
        video_element.append(self._xml_format())

        for track in timeline.tracks:
            track_element = et.SubElement(video_element, 'track')
            for clip in track.trackitems:
                if isinstance(clip, BASE_CLIP):
                    clipitem = self._xml_clipitem(clip)
                if isinstance(clip, BASE_TEXT):
                    clipitem = self._xml_generatoritem(clip)
                track_element.append(clipitem)
                if clip.left_transition:
                    if getattr(clip.left, 'right_transition', None) and \
                                    clip.left.right_transition.target_in == clip.left_transition.target_in and \
                                    clip.left.right_transition.target_out == clip.left_transition.target_out:
                        pass
                    else:
                        track_element.getparent().insert(-1, self._xml_transitionitem(clip.left_transition))

                if clip.right_transition:
                    track_element.append(self._xml_transitionitem(clip.right_transition))

        return sequence

    def write_to_file(self, file_path):
        xml_doc_type = '<!DOCTYPE xmeml>'

        root = et.Element('xmeml', attrib={'version': '5'})
        root.append(self._xml_sequence(self.timeline))

        with open(file_path, 'w') as xml_file:
            xml_file.write(et.tostring(root,
                                       pretty_print=True,
                                       xml_declaration=True,
                                       doctype=xml_doc_type,
                                       encoding='utf-8'))


if __name__ == '__main__':
    test = FCP7_XML.read_from_file('/Volumes/BACKUP/TEST_Footage/edit_file/cross_fade.xml')
    trackitem =  test.timeline.tracks[0].trackitems[0]
    print trackitem
    print trackitem.media.source_in, trackitem.media.source_out, trackitem.media.duration
    # print test.timeline.tracks[0].trackitems
    # test.write_to_file('')

    # import CMX3600_EDL
    #
    # ee = CMX3600_EDL.CMX3600_EDL(None, 24.0)
    # ee.timeline = test.timeline
    # ee.write_to_file('/Users/guoxiaoao/Desktop/EDL_TEST/fafafafa.edl')
