#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.dialects import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.event import *
from uuid import uuid1
import time
from datetime import date as pydate
import os
import getpass
from pprint import pformat
from DECO_DB import *

from sqlalchemy.ext.horizontal_shard import *

try:
    from PySide.QtGui import QImage
    from PySide.QtCore import QByteArray, QBuffer
except Exception as e:
    raise e

CURRENT_USER_NAME = os.environ.get('DB_USER_NAME', None) or getpass.getuser()
ROOT_ATOM_NAME = '.!0x5f3759df_this_is_a_magic_number_used_for_telling_which_atom_is_the_root' \
                 '_and_should_not_be_used_by_user'


@as_declarative()
class DB_BASE(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @property
    def session(self):
        return object_session(self)

    def __repr__(self, indent=4, width=80, depth=None):
        return str('<{0}> '.format(self.__tablename__) + \
                   pformat({c.name: getattr(self, c.name, None) for c in self.__table__.columns}) + '\n\n')


class HAS_BASIC(object):
    # id = Column(BigInteger, primary_key=True, index=True)
    sid = Column(String(50), primary_key=True, index=True, default=lambda: str(uuid1()))
    name = Column(String, default='')
    label = Column(String, default='')
    active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)


class HAS_TIMESTAMP(object):
    date_created_time = Column(Date, default=pydate.today())
    date_updated_time = Column(Date, onupdate=pydate.today())

    @declared_attr
    def db_created_time(cls):
        return deferred(Column(DateTime(timezone=False), default=func.now()))

    @declared_attr
    def db_updated_time(cls):
        return deferred(Column(DateTime(timezone=False), onupdate=func.now()))


class HAS_EXTRA(object):
    @declared_attr
    def extra_info(cls):
        return deferred(Column(String))

    @declared_attr
    def debug_info(cls):
        return deferred(Column(String))


class HAS_FILE(object):
    disk_full_path = Column(String)

    @property
    def full_path(self):
        result = eval(getattr(self, 'disk_full_path', ''))
        return result

    @full_path.setter
    def full_path(self, abs_file_list):
        abs_file_list = abs_file_list if isinstance(abs_file_list, (list, tuple)) else [abs_file_list]
        abs_file_list.sort()
        self.disk_full_path = str(abs_file_list)


class HAS_CLUE(object):
    cam_clue = Column(String)
    vfx_seq_clue = Column(String)
    vfx_shot_clue = Column(String)
    scene_clue = Column(String)
    shot_clue = Column(String)
    take_clue = Column(String)


class HAS_THUMBNAIL(object):
    @declared_attr
    def thumbnail_base64(cls):
        return deferred(Column(String))

    @property
    def thumbnail(self):
        ba = QByteArray.fromBase64(str(self.thumbnail_base64))
        return QImage.fromData(ba, 'JPG')

    @thumbnail.setter
    def thumbnail(self, base64_string_or_qimage):
        if isinstance(base64_string_or_qimage, str):
            self.thumbnail_base64 = base64_string_or_qimage
        else:
            ba = QByteArray()
            buffer = QBuffer(ba)
            base64_string_or_qimage.save(buffer, 'JPG', 80)
            self.thumbnail_base64 = ba.toBase64().data()


@listens_for(DB_BASE, 'before_insert', propagate=True)
def insert_base_link(mapper, connection, target):
    # print '========== before insert ==========='
    # print target
    if target.label is None:
        target.label = target.name

    if hasattr(target, 'created_by_name'):
        target.created_by_name = CURRENT_USER_NAME


@listens_for(DB_BASE, 'before_update', propagate=True)
def update_base_link(mapper, connection, target):
    # print '========== before insert ==========='
    # print target
    if hasattr(target, 'updated_by_name'):
        target.updated_by_name = CURRENT_USER_NAME
