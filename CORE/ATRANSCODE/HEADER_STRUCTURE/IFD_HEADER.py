#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from struct import unpack_from, calcsize
import os
from pprint import pformat

IFD_TYPE_DICT = {1 : 'B',
                 2 : 's',
                 3 : 'H',
                 4 : 'I',
                 5 : '2I',
                 6 : 'b',
                 7 : 's',
                 8 : 'h',
                 9 : 'i',
                 10: '2i',
                 11: 'f',
                 12: 'd'}

IFD_TAG_DICT = {254  : 'NewSubfileType',
                255  : 'SubfileType',
                256  : 'ImageWidth',
                257  : 'ImageLength',
                258  : 'BitsPerSample',
                259  : 'Compression',
                262  : 'PhotometricInterpretation',
                263  : 'Threshholding',
                264  : 'CellWidth',
                265  : 'CellLength',
                266  : 'FillOrder',
                270  : 'ImageDescription',
                271  : 'Make',
                272  : 'Model',
                273  : 'StripOffsets',
                274  : 'Orientation',
                277  : 'SamplesPerPixel',
                278  : 'RowsPerStrip',
                279  : 'StripByteCounts',
                280  : 'MinSampleValue',
                281  : 'MaxSampleValue',
                282  : 'XResolution',
                283  : 'YResolution',
                284  : 'PlanarConfiguration',
                288  : 'FreeOffsets',
                289  : 'FreeByteCounts',
                290  : 'GrayResponseUnit',
                291  : 'GrayResponseCurve',
                296  : 'ResolutionUnit',
                305  : 'Software',
                306  : 'DateTime',
                315  : 'Artist',
                316  : 'HostComputer',
                320  : 'ColorMap',
                338  : 'ExtraSamples',
                33432: 'Copyright',

                # tiff extended tags
                269  : 'DocumentName',
                285  : 'PageName',
                286  : 'XPosition',
                287  : 'YPosition',
                292  : 'T4Options',
                293  : 'T6Options',
                297  : 'PageNumber',
                301  : 'TransferFunction',
                317  : 'Predictor',
                318  : 'WhitePoint',
                319  : 'PrimaryChromaticities',
                321  : 'HalftoneHints',
                322  : 'TileWidth',
                323  : 'TileLength',
                324  : 'TileOffsets',
                325  : 'TileByteCounts',
                326  : 'BadFaxLines',
                327  : 'CleanFaxData',
                328  : 'ConsecutiveBadFaxLines',
                330  : 'SubIFDs',
                332  : 'InkSet',
                333  : 'InkNames',
                334  : 'NumberOfInks',
                336  : 'DotRange',
                337  : 'TargetPrinter',
                339  : 'SampleFormat',
                340  : 'SMinSampleValue',
                341  : 'SMaxSampleValue',
                342  : 'TransferRange',
                343  : 'ClipPath',
                344  : 'XClipPathUnits',
                345  : 'YClipPathUnits',
                346  : 'Indexed',
                347  : 'JPEGTables',
                351  : 'OPIProxy',
                400  : 'GlobalParametersIFD',
                401  : 'ProfileType',
                402  : 'FaxProfile',
                403  : 'CodingMethods',
                404  : 'VersionYear',
                405  : 'ModeNumber',
                433  : 'Decode',
                434  : 'DefaultImageColor',
                512  : 'JPEGProc',
                513  : 'JPEGInterchangeFormat',
                514  : 'JPEGInterchangeFormatLength',
                515  : 'JPEGRestartInterval',
                517  : 'JPEGLosslessPredictors',
                518  : 'JPEGPointTransforms',
                519  : 'JPEGQTables',
                520  : 'JPEGDCTables',
                521  : 'JPEGACTables',
                529  : 'YCbCrCoefficients',
                530  : 'YCbCrSubSampling',
                531  : 'YCbCrPositioning',
                532  : 'ReferenceBlackWhite',
                559  : 'StripRowCounts',
                700  : 'XMP',
                32781: 'ImageID',
                34732: 'ImageLayer',

                # dng basic tags
                50706: 'DNGVersion',
                50707: 'DNGBackwardVersion',
                50708: 'UniqueCameraModel',
                50709: 'LocalizedCameraModel',
                50710: 'CFAPlaneColor',
                50711: 'CFALayout',
                50712: 'LinearizationTable',
                50713: 'BlackLevelRepeatDim',
                50714: 'BlackLevel',
                50715: 'BlackLevelDeltaH',
                50716: 'BlackLevelDeltaV',
                50717: 'WhiteLevel',
                50718: 'DefaultScale',
                50780: 'BestQualityScale',
                50719: 'DefaultCropOrigin',
                50720: 'DefaultCropSize',
                50778: 'CalibrationIlluminant1',
                50779: 'CalibrationIlluminant2',
                50721: 'ColorMatrix1',
                50722: 'ColorMatrix2',
                50723: 'CameraCalibration1',
                50724: 'CameraCalibration2',
                50725: 'ReductionMatrix1',
                50726: 'ReductionMatrix2',
                50727: 'AnalogBalance',
                50728: 'AsShotNeutral',
                50729: 'AsShotWhiteXY',
                50730: 'BaselineExposure',
                50731: 'BaselineNoise',
                50732: 'BaselineSharpness',
                50733: 'BayerGreenSplit',
                50734: 'LinearResponseLimit',
                50735: 'CameraSerialNumber',
                50736: 'LensInfo',
                50737: 'ChromaBlurRadius',
                50738: 'AntiAliasStrength',
                50739: 'ShadowScale',
                50740: 'DNGPrivateData',
                50741: 'MakerNoteSafety',
                50781: 'RawDataUniqueID',
                50827: 'OriginalRawFileName',
                50828: 'OriginalRawFileData',
                50829: 'ActiveArea',
                50830: 'MaskedAreas',
                50831: 'AsShotICCProfile',
                50832: 'AsShotPreProfileMatrix',
                50833: 'CurrentICCProfile',
                50834: 'CurrentPreProfileMatrix',

                # dng tags for 1.2.0.0
                50879: 'ColorimetricReference',
                50931: 'CameraCalibrationSignature',
                50932: 'ProfileCalibrationSignature',
                50933: 'ExtraCameraProfiles',
                50934: 'AsShotProfileName',
                50935: 'NoiseReductionApplied',
                50936: 'ProfileName',
                50937: 'ProfileHueSatMapDims',
                50938: 'ProfileHueSatMapData1',
                50939: 'ProfileHueSatMapData2',
                50940: 'ProfileToneCurve',
                50941: 'ProfileEmbedPolicy',
                50942: 'ProfileCopyright',
                50964: 'ForwardMatrix1',
                50965: 'ForwardMatrix2',
                50966: 'PreviewApplicationName',
                50967: 'PreviewApplicationVersion',
                50968: 'PreviewSettingsName',
                50969: 'PreviewSettingsDigest',
                50970: 'PreviewColorSpace',
                50971: 'PreviewDateTime',
                50972: 'RawImageDigest',
                50973: 'OriginalRawFileDigest',
                50974: 'SubTileBlockSize',
                50975: 'RowInterleaveFactor',
                50981: 'ProfileLookTableDims',
                50982: 'ProfileLookTableData',

                # dng tags for 1.3.0.0
                51008: 'OpcodeList1',
                51009: 'OpcodeList2',
                51022: 'OpcodeList3',
                51041: 'NoiseProfile',

                # dng tags for 1.3.0.0
                51125: 'DefaultUserCrop',
                51110: 'DefaultBlackRender',
                51109: 'BaselineExposureOffset',
                51108: 'ProfileLookTableEncoding',
                51107: 'ProfileHueSatMapEncoding',
                51089: 'OriginalDefaultFinalSize',
                51090: 'OriginalBestQualityFinalSize',
                51091: 'OriginalDefaultCropSize',
                51111: 'NewRawImageDigest',
                51112: 'RawToPreviewGain',
                51112: 'RawToPreviewGain',

                # BMCC private tags
                51043: 'TimeCode',
                51044: 'Fps',
                }


class IFD(object):
    bit_order = ''
    start = None
    end = None
    tag = None
    type = None
    count = None
    value = []
    value_offset = -1
    indirect = False

    def __init__(self, f):
        self.bit_order = self.__class__.bit_order
        self.start = f.tell()
        self.end = self.start + 12
        self.value = []
        self._parse_ifd(f)

    def _parse_ifd(self, f):
        self.tag, self.type, self.count, = unpack_from(self.bit_order + 'HHI', f.read(calcsize('HHI')))
        self.tag_name = IFD_TAG_DICT.get(self.tag, 'unknown')
        self.type_format = IFD_TYPE_DICT.get(self.type, 'unknown')
        if self.count * calcsize(self.type_format) <= 4:
            if self.type_format == 's':
                self.type_format = str(self.count) + self.type_format
                self.count = 1
            for index in xrange(self.count):
                result = unpack_from(self.bit_order + self.type_format, f.read(calcsize(self.type_format)))
                self.value.append(result if len(result) > 1 else result[0])
        else:
            self.indirect = True
            self.value_offset = unpack_from(self.bit_order + 'I', f.read(4))[0]
            f.seek(self.value_offset)
            if self.type_format == 's':
                self.type_format = str(self.count) + self.type_format
                self.count = 1
            for index in xrange(self.count):
                result = unpack_from(self.bit_order + self.type_format, f.read(calcsize(self.type_format)))
                self.value.append(result if len(result) > 1 else result[0])

        f.seek(self.end)

    def __repr__(self):
        keys = ['start', 'end', 'tag', 'type_format', 'count', 'indirect', 'value_offset', 'value']
        return pformat([(x, getattr(self, x, None)) for x in keys]) + '\n'


class IFD_BASE(object):
    def __init__(self, f):
        self.file = f
        self._read_header(f)

    def _read_header(self, f):
        f.seek(0)
        self.endian = 'big' if unpack_from('2s', f.read(2))[0] == 'MM' else 'little'
        IFD.bit_order = '>' if self.endian == 'big' else '<'
        self.magic = unpack_from(IFD.bit_order + 'H', f.read(2))[0]
        if self.magic != 42:
            return None
        self.IFD_offset = unpack_from(IFD.bit_order + 'I', f.read(4))[0]

        f.seek(self.IFD_offset)
        self.IFD_count = unpack_from(IFD.bit_order + 'H', f.read(2))[0]
        for index in xrange(self.IFD_count):
            ifd = IFD(f)
            setattr(self, ifd.tag_name, ifd)

    def __repr__(self):
        return pformat(self.__dict__) + '\n'

    @classmethod
    def read_file(cls, f):
        return cls(f)
