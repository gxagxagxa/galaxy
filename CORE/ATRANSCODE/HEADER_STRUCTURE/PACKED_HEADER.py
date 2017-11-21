#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from struct import unpack_from, calcsize
from pprint import pformat

NULL = '\x00'

EXR_TYPE = {'box2i'         : [{'xMin': '<i'},
                               {'yMin': '<i'},
                               {'xMax': '<i'},
                               {'yMax': '<i'}, ],
            'box2f'         : [{'xMin': '<f'},
                               {'yMin': '<f'},
                               {'xMax': '<f'},
                               {'yMax': '<f'}, ],
            'channel'       : [{'name': '<{}s'},
                               {'pixel_type': '<i'},
                               {'pLinear': '<B'},
                               {'reserved': '<3s'},
                               {'xSampling': '<i'},
                               {'ySampling': '<i'},
                               ],
            'chlist'        : [{'channel': 'nested'}],
            'chromaticities': [{'redX': '<f'},
                               {'redY': '<f'},
                               {'greenX': '<f'},
                               {'greenY': '<f'},
                               {'blueX': '<f'},
                               {'bluey': '<f'},
                               {'whiteX': '<f'},
                               {'whiteY': '<f'}, ],
            'compression'   : '<B',
            'envmap'        : '<B',
            'keycode'       : [{'filmMfcCode': '<i'},
                               {'filmType': '<i'},
                               {'prefix': '<i'},
                               {'count': '<i'},
                               {'perfOffset': '<i'},
                               {'perfsPerFrame': '<i'},
                               {'perfsPerCount': '<i'}, ],
            'lineOrder'     : '<B',
            'm33f'          : [{'a1': '<f'},
                               {'a2': '<f'},
                               {'a3': '<f'},
                               {'a4': '<f'},
                               {'a5': '<f'},
                               {'a6': '<f'},
                               {'a7': '<f'},
                               {'a8': '<f'},
                               {'a9': '<f'}, ],
            'm44f'          : [{'a1': '<f'},
                               {'a2': '<f'},
                               {'a3': '<f'},
                               {'a4': '<f'},
                               {'a5': '<f'},
                               {'a6': '<f'},
                               {'a7': '<f'},
                               {'a8': '<f'},
                               {'a9': '<f'},
                               {'a10': '<f'},
                               {'a11': '<f'},
                               {'a12': '<f'},
                               {'a13': '<f'},
                               {'a14': '<f'},
                               {'a15': '<f'},
                               {'a16': '<f'}, ],
            'rational'      : [{'a1': '<i'},
                               {'a2': '<i'}, ],
            'timecode'      : [{'timeAndFlags': '<i'},
                               {'userData': '<i'}, ],
            'v2i'           : [{'x': '<i'},
                               {'y': '<i'}, ],
            'v3i'           : [{'x': '<i'},
                               {'y': '<i'},
                               {'z': '<i'}, ],
            'v2f'           : [{'x': '<f'},
                               {'y': '<f'}, ],
            'v3f'           : [{'x': '<f'},
                               {'y': '<f'},
                               {'z': '<f'}, ],
            'tiledesc'      : [{'tile_width': '<I'},
                               {'tile_height': '<I'},
                               {'mode': '<B'}],

            'unsigned char' : '<B',
            'short'         : '<h',
            'unsigned short': '<H',
            'int'           : '<i',
            'unsigned int'  : '<I',
            'unsigned long' : '<Q',
            'half'          : '<H',
            'float'         : '<f',
            'double'        : '<d',
            'string'        : '<{}s'
            }


def _read_until_null(f):
    if isinstance(f, file):
        start = f.tell()
        temp_array = bytearray()
        while True:
            read_byte = f.read(1)
            if read_byte == NULL:
                break
            temp_array.append(read_byte)
        if temp_array:
            return buffer(temp_array), f.tell() - start - 1
        else:
            return 'BREAK', 0

    else:
        start = 0
        temp_array = bytearray()
        while start < len(f):
            read_byte = f[start: start + 1]
            if read_byte == NULL:
                break
            temp_array.append(read_byte)
            start += 1
        if temp_array:
            return buffer(temp_array), start
        else:
            return 'BREAK', 0


class ATTRIBUTE_NESTED(object):
    def __init__(self):
        super(ATTRIBUTE_NESTED, self).__init__()

    def __repr__(self):
        return pformat(self.__dict__) + '\n'


class ATTRIBUTE_BASE(object):
    def __init__(self, f):
        self.name = None
        self.type = None
        self.size = None
        self.value = None

    def __repr__(self):
        return '<{}> '.format(self.name) + pformat(self.__dict__) + '\n'


class PACKED_BASE(object):
    def __init__(self, f):
        self.file = f
        self.magic, = unpack_from('<I', f.read(calcsize('<I')))
        if self.magic == 20000630:
            self.version, = unpack_from('<B', f.read(calcsize('<B')))
            self.flags = unpack_from('<3s', f.read(calcsize('<3s')))
            self._parse_file(f)
        else:
            raise Exception('not a exr file!')

    def _parse_file(self, f):
        while True:
            result, length = _read_until_null(f)
            if result == 'BREAK':
                break

            new_attribute = ATTRIBUTE_BASE(f)
            new_attribute.name, = unpack_from('<{}s'.format(length), result)
            setattr(self, new_attribute.name, new_attribute)
            result, length = _read_until_null(f)
            new_attribute.type, = unpack_from('<{}s'.format(length), result)
            new_attribute.size, = unpack_from('<I', f.read(calcsize('<I')))

            _value = f.read(new_attribute.size)
            _format = EXR_TYPE[new_attribute.type]
            self._nested_attribute(_format, _value, 0, new_attribute.size, new_attribute)

    def _nested_attribute(self, format, data, current, size, parent):
        _current = current
        nested_attribute = ATTRIBUTE_NESTED()

        if isinstance(format, list):
            for item in format:
                _key, _value = item.keys()[0], item.values()[0]
                # print 'this is ', _key, _value
                if '{}' in _value:
                    _result, length = _read_until_null(data[_current:])
                    _result, = unpack_from(_value.format(length), data[_current: _current + length])
                    setattr(nested_attribute, _key, _result)
                    _current = _current + length + 1
                    continue

                if _value == 'nested':
                    _current += self._nested_attribute(EXR_TYPE[_key], data, _current, size, nested_attribute)

                else:
                    _result, = unpack_from(_value, data[_current: _current + calcsize(_value)])
                    setattr(nested_attribute, _key, _result)
                    _current += calcsize(_value)

            if _current < size - 1:
                _current = self._nested_attribute(format, data, _current, size, parent)
                setattr(parent, nested_attribute.name, nested_attribute)

            else:
                if isinstance(parent, ATTRIBUTE_NESTED):
                    setattr(parent, nested_attribute.name, nested_attribute)
                else:
                    setattr(parent, 'value', nested_attribute)

        else:
            if '{}' in format:
                _result, length = _read_until_null(data)
                _result, = unpack_from(format.format(length), data)
                setattr(parent, 'value', _result)
            else:
                _result, = unpack_from(format, data)
                setattr(parent, 'value', _result)

        return _current

    def _basic_attribute(self, format, data, size):
        return unpack_from(format.format(size), data)

    def __repr__(self):
        return pformat(self.__dict__) + '\n'

    @classmethod
    def read_file(cls, f):
        return cls(f)
