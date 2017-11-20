#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from struct import unpack_from, calcsize
from pprint import *


class STRUCTURE_NESTED_FIELD(object):
    def __init__(self, name, structure_type, offset):
        self.name = name
        self.type = structure_type
        self.offset = offset

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            nested_data = instance._buffer[self.offset: self.offset + self.type.structure_size]
            result = self.type(nested_data)
            setattr(instance, self.name, result)
            return result


class STRUCTURE_FIELD(object):
    def __init__(self, format, offset):
        self.format = format
        self.offset = offset

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            _order = instance.__class__._bit_order
            if _order == 'no_change':
                pass
            elif _order == 'big':
                if self.format.startswith(('<', '>', '!', '@')):
                    self.format = '>' + self.format[1:]
                else:
                    self.format = '>' + self.format
            elif _order == 'little':
                if self.format.startswith(('<', '>', '!', '@')):
                    self.format = '<' + self.format[1:]
                else:
                    self.format = '<' + self.format

            result = unpack_from(self.format, instance._buffer, self.offset)
            return result[0] if len(result) == 1 else result


class STRUCTURE_META(type):
    def __init__(self, cls, base, cls_dict):
        fields = getattr(self, '_fields', [])
        byte_order = ''
        offset = 0

        for field_format, field_name in fields:
            if isinstance(field_format, STRUCTURE_META):
                setattr(self, field_name, STRUCTURE_NESTED_FIELD(field_name, field_format, offset))
                offset += field_format.structure_size
            else:
                if field_format.startswith(('<', '>', '!', '@')):
                    byte_order = field_format[0]
                    field_format = field_format[1:]

                field_format = byte_order + field_format
                setattr(self, field_name, STRUCTURE_FIELD(field_format, offset))
                offset += calcsize(field_format)

        setattr(self, 'structure_size', offset)


class STRUCTURE_BASE(object):
    __metaclass__ = STRUCTURE_META
    _bit_order = 'no_change'

    def __init__(self, data):
        self._buffer = memoryview(data)

    @classmethod
    def read_file(cls, f):
        cls.file = f
        return cls(f.read(cls.structure_size))

    @property
    def children(self):
        return [x[-1] for x in self._fields]

    def __repr__(self):
        return pformat([(x[-1], getattr(self, x[-1], None)) for x in self._fields]) + '\n'
