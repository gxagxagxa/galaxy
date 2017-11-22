#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from DB_BASE import *


# todo: data need size, atom



class USER(DB_BASE, HAS_BASIC, HAS_TIMESTAMP, HAS_EXTRA, HAS_THUMBNAIL):
    name = Column(String, index=True)

    @property
    def shared_views(self):
        return [x.view for x in self.view_permissions]


tag_atom_dependencies_table = Table('tag_atom_dependencies',
                                    DB_BASE.metadata,
                                    Column('tag_sid', String(50),
                                           ForeignKey('tag.sid'),
                                           primary_key=True),
                                    Column('atom_sid', String(50),
                                           ForeignKey('atom.sid'),
                                           primary_key=True))


class HAS_LINK(object):
    pass


class ATOM(DB_BASE, HAS_BASIC, HAS_TIMESTAMP, HAS_EXTRA, HAS_THUMBNAIL, HAS_LINK):
    is_empty = Column(Boolean, default=True)
    tags = relationship('TAG',
                        secondary=tag_atom_dependencies_table,
                        lazy='dynamic',
                        order_by='TAG.name',
                        innerjoin=True,
                        backref=backref('atoms', lazy='dynamic', order_by='ATOM.name', innerjoin=True))
    created_by_name = Column(String, index=True)
    created_by = relationship('USER',
                              primaryjoin='foreign(ATOM.created_by_name) == remote(USER.name)',
                              backref=backref('atoms', lazy='dynamic'))
    updated_by_name = Column(String, index=True)
    updated_by = relationship('USER',
                              primaryjoin='foreign(ATOM.updated_by_name) == remote(USER.name)')
    parent_sid = Column(String(50), index=True)
    parent = relationship('ATOM',
                          primaryjoin='foreign(ATOM.parent_sid) == remote(ATOM.sid)',
                          backref=backref('sub_atoms', order_by='ATOM.name', lazy='dynamic'))

    @property
    def items(self):
        return {'atom': self.sub_atoms,
                'raw' : self.raws,
                'data': self.datas,
                'link': self.links}


class LINK(DB_BASE, HAS_BASIC, HAS_TIMESTAMP, HAS_EXTRA, HAS_THUMBNAIL):
    parent_sid = Column(String, index=True)
    parent = relationship('ATOM',
                          primaryjoin='foreign(LINK.parent_sid) == remote(ATOM.sid)',
                          backref=backref('links', order_by='LINK.name', lazy='dynamic'))

    target_table = Column(String)
    target_sid = Column(String, index=True)

    # target = relationship('ATOM',
    #                       primaryjoin='foreign(LINK.target_sid) == remote(ATOM.sid)',
    #                       backref=backref('sources', order_by='LINK.name', lazy='dynamic'))

    @property
    def target(self):
        return getattr(self, 'target_{}'.format(self.target_table))

    @target.setter
    def target(self, value):
        self.target_table = value.__tablename__
        self.target_sid = value.sid

    @property
    def items(self):
        return self.target.items if isinstance(self.target, ATOM) else self.target


@listens_for(HAS_LINK, 'mapper_configured', propagate=True)
def setup_listener(mapper, _class):
    parent_type = _class.__name__.lower()
    _class.sources = relationship(LINK,
                                  primaryjoin=and_(_class.sid == foreign(remote(LINK.target_sid)),
                                                   LINK.target_table == parent_type),
                                  order_by=LINK.name,
                                  backref=backref('target_{0}'.format(parent_type),
                                                  primaryjoin=remote(_class.sid) == foreign(LINK.target_sid))
                                  )

    @listens_for(_class.sources, 'append')
    def append_sources(target, value, initiator):
        value.target_table = parent_type


class TAG(DB_BASE, HAS_BASIC, HAS_EXTRA, HAS_TIMESTAMP):
    name = Column(String, index=True)

    @property
    def children(self):
        return {'atom': self.atoms,
                'raw' : self.raws,
                'data': self.datas}


class TYPE(DB_BASE, HAS_BASIC, HAS_EXTRA, HAS_TIMESTAMP):
    name = Column(String, index=True)


class VENDOR(DB_BASE, HAS_BASIC, HAS_EXTRA, HAS_TIMESTAMP):
    name = Column(String, index=True)


tag_raw_dependencies_table = Table('tag_raw_dependencies',
                                   DB_BASE.metadata,
                                   Column('tag_sid', String(50),
                                          ForeignKey('tag.sid'),
                                          primary_key=True),
                                   Column('raw_sid', String(50),
                                          ForeignKey('raw.sid'),
                                          primary_key=True))

raw_atom_dependencies_table = Table('raw_atom_dependencies',
                                    DB_BASE.metadata,
                                    Column('atom_sid', String(50),
                                           ForeignKey('atom.sid'),
                                           primary_key=True),
                                    Column('raw_sid', String(50),
                                           ForeignKey('raw.sid'),
                                           primary_key=True))


class RAW(DB_BASE, HAS_BASIC, HAS_EXTRA, HAS_TIMESTAMP, HAS_CLUE, HAS_THUMBNAIL, HAS_SIZE, HAS_LINK):
    atoms = relationship('ATOM',
                         secondary=raw_atom_dependencies_table,
                         innerjoin=True,
                         lazy='dynamic',
                         order_by='ATOM.name',
                         backref=backref('raws', order_by='RAW.name', innerjoin=True, lazy='dynamic'))
    name = Column(String, index=True)
    reel = Column(String)
    in_tc = Column(String)
    out_tc = Column(String)
    project_fps = Column(Float, default=24.0)
    fps = Column(Float, default=24.0)
    tags = relationship('TAG',
                        secondary=tag_raw_dependencies_table,
                        lazy='dynamic',
                        order_by='TAG.name',
                        innerjoin=True,
                        backref=backref('raws', lazy='dynamic', order_by='RAW.name', innerjoin=True))

    created_by_name = Column(String, index=True)
    created_by = relationship('USER',
                              primaryjoin='foreign(RAW.created_by_name) == remote(USER.name)',
                              backref=backref('raws', lazy='dynamic'))
    updated_by_name = Column(String, index=True)
    updated_by = relationship('USER',
                              primaryjoin='foreign(RAW.updated_by_name) == remote(USER.name)')


data_atom_dependencies_table = Table('data_atom_dependencies',
                                     DB_BASE.metadata,
                                     Column('atom_sid', String(50),
                                            ForeignKey('atom.sid'),
                                            primary_key=True),
                                     Column('data_sid', String(50),
                                            ForeignKey('data.sid'),
                                            primary_key=True))

tag_data_dependencies_table = Table('tag_data_dependencies',
                                    DB_BASE.metadata,
                                    Column('tag_sid', String(50),
                                           ForeignKey('tag.sid'),
                                           primary_key=True),
                                    Column('data_sid', String(50),
                                           ForeignKey('data.sid'),
                                           primary_key=True))


class DATA(DB_BASE, HAS_BASIC, HAS_EXTRA, HAS_TIMESTAMP, HAS_FILE, HAS_CLUE, HAS_THUMBNAIL, HAS_SIZE, HAS_LINK):
    atoms = relationship('ATOM',
                         secondary=data_atom_dependencies_table,
                         innerjoin=True,
                         lazy='dynamic',
                         order_by='ATOM.name',
                         backref=backref('datas', order_by='DATA.name', innerjoin=True, lazy='dynamic'))

    tags = relationship('TAG',
                        secondary=tag_data_dependencies_table,
                        lazy='dynamic',
                        innerjoin=True,
                        order_by='TAG.name',
                        backref=backref('datas', order_by='DATA.name', lazy='dynamic', innerjoin=True))

    type_name = Column(String, index=True)
    type = relationship('TYPE',
                        primaryjoin='foreign(DATA.type_name) == remote(TYPE.name)',
                        backref=backref('datas', order_by='DATA.name', lazy='dynamic'))

    vendor_name = Column(String, index=True)
    vendor = relationship('VENDOR',
                          primaryjoin='foreign(DATA.vendor_name) == remote(VENDOR.name)',
                          backref=backref('datas', order_by='DATA.name', lazy='dynamic'))

    created_by_name = Column(String, index=True)
    created_by = relationship('USER',
                              primaryjoin='foreign(DATA.created_by_name) == remote(USER.name)',
                              backref=backref('datas', order_by='DATA.name', lazy='dynamic'))
    updated_by_name = Column(String, index=True)
    updated_by = relationship('USER',
                              primaryjoin='foreign(DATA.updated_by_name) == remote(USER.name)')

    @property
    def similar(self):
        result = {}
        result['raw'] = self.session.query(RAW).filter(or_(self.cam_clue == RAW.cam_clue,
                                                           self.vfx_seq_clue == RAW.vfx_seq_clue,
                                                           self.vfx_shot_clue == RAW.vfx_shot_clue,
                                                           self.scene_clue == RAW.scene_clue,
                                                           self.shot_clue == RAW.shot_clue,
                                                           self.take_clue == RAW.take_clue))
        result['data'] = self.session.query(DATA).filter(or_(self.cam_clue == DATA.cam_clue,
                                                             self.vfx_seq_clue == DATA.vfx_seq_clue,
                                                             self.vfx_shot_clue == DATA.vfx_shot_clue,
                                                             self.scene_clue == DATA.scene_clue,
                                                             self.shot_clue == DATA.shot_clue,
                                                             self.take_clue == DATA.take_clue))
        return result


class META(DB_BASE, HAS_BASIC, HAS_EXTRA, HAS_TIMESTAMP, HAS_FILE, HAS_CLUE):
    data_sid = Column(String(50), index=True)
    data = relationship('DATA',
                        primaryjoin='foreign(META.data_sid) == remote(DATA.sid)',
                        backref=backref('metas', order_by='META.name', lazy='dynamic'))
    raw_sid = Column(String(50), index=True)
    raw = relationship('RAW',
                       primaryjoin='foreign(META.raw_sid) == remote(RAW.sid)',
                       backref=backref('metas', order_by='META.name', lazy='dynamic'))
    created_by_name = Column(String, index=True)
    created_by = relationship('USER',
                              primaryjoin='foreign(META.created_by_name) == remote(USER.name)',
                              backref=backref('metas', order_by='META.name', lazy='dynamic'))
    updated_by_name = Column(String, index=True)
    updated_by = relationship('USER',
                              primaryjoin='foreign(META.updated_by_name) == remote(USER.name)')


class VIEW_PERMISSION(DB_BASE, HAS_BASIC):
    view_sid = Column(String(50), index=True)
    shared_user_name = Column(String, index=True)
    shared_user = relationship('USER',
                               primaryjoin='foreign(VIEW_PERMISSION.shared_user_name) == remote(USER.name)',
                               backref=backref('view_permissions', lazy='dynamic', order_by='VIEW_PERMISSION.name'))
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)


view_data_dependencies_table = Table('view_data_dependencies',
                                     DB_BASE.metadata,
                                     Column('view_sid', String(50),
                                            ForeignKey('view.sid'),
                                            primary_key=True),
                                     Column('data_sid', String(50),
                                            ForeignKey('data.sid'),
                                            primary_key=True))

view_atom_dependencies_table = Table('view_atom_dependencies',
                                     DB_BASE.metadata,
                                     Column('view_sid', String(50),
                                            ForeignKey('view.sid'),
                                            primary_key=True),
                                     Column('atom_sid', String(50),
                                            ForeignKey('atom.sid'),
                                            primary_key=True))

view_raw_dependencies_table = Table('view_raw_dependencies',
                                    DB_BASE.metadata,
                                    Column('view_sid', String(50),
                                           ForeignKey('view.sid'),
                                           primary_key=True),
                                    Column('raw_sid', String(50),
                                           ForeignKey('raw.sid'),
                                           primary_key=True))

view_search_dependencies_table = Table('view_search_dependencies',
                                       DB_BASE.metadata,
                                       Column('view_sid', String(50),
                                              ForeignKey('view.sid'),
                                              primary_key=True),
                                       Column('search_sid', String(50),
                                              ForeignKey('search.sid'),
                                              primary_key=True))


class VIEW(DB_BASE, HAS_BASIC, HAS_EXTRA, HAS_TIMESTAMP):
    created_by_name = Column(String, index=True)
    created_by = relationship('USER',
                              primaryjoin='foreign(VIEW.created_by_name) == remote(USER.name)',
                              backref=backref('views', order_by='VIEW.name', lazy='dynamic'))
    updated_by_name = Column(String, index=True)
    updated_by = relationship('USER',
                              primaryjoin='foreign(VIEW.updated_by_name) == remote(USER.name)')
    permissions = relationship('VIEW_PERMISSION',
                               primaryjoin='remote(foreign(VIEW_PERMISSION.view_sid)) == VIEW.sid',
                               lazy='dynamic',
                               backref=backref('view'))

    @property
    def shares(self):
        return {x.shared_user_name: x for x in self.permissions}

    datas = relationship('DATA',
                         secondary=view_data_dependencies_table,
                         lazy='dynamic',
                         innerjoin=True,
                         order_by='DATA.name',
                         backref=backref('views', lazy='dynamic', innerjoin=True, order_by='VIEW.name'))
    atoms = relationship('ATOM',
                         secondary=view_atom_dependencies_table,
                         lazy='dynamic',
                         innerjoin=True,
                         order_by='ATOM.name',
                         backref=backref('views', lazy='dynamic', innerjoin=True, order_by='VIEW.name'))
    raws = relationship('RAW',
                        secondary=view_raw_dependencies_table,
                        lazy='dynamic',
                        innerjoin=True,
                        order_by='RAW.name',
                        backref=backref('views', lazy='dynamic', innerjoin=True, order_by='VIEW.name'))
    searches = relationship('SEARCH',
                            secondary=view_search_dependencies_table,
                            lazy='dynamic',
                            innerjoin=True,
                            order_by='SEARCH.name',
                            backref=backref('views', lazy='dynamic', innerjoin=True, order_by='VIEW.name'))

    @property
    def owner(self):
        return self.created_by

    @DECO_LAZY
    def items(self):
        return {'search': self.searches,
                'atom'  : self.atoms,
                'raw'   : self.raws,
                'data'  : self.datas}


class SEARCH(DB_BASE, HAS_BASIC, HAS_EXTRA, HAS_TIMESTAMP):
    search_target = Column(String)
    search_param = Column(String)

    created_by_name = Column(String, index=True)
    created_by = relationship('USER',
                              primaryjoin='foreign(SEARCH.created_by_name) == remote(USER.name)',
                              backref=backref('searches', order_by='SEARCH.name', lazy='dynamic'))
    updated_by_name = Column(String, index=True)
    updated_by = relationship('USER',
                              primaryjoin='foreign(SEARCH.updated_by_name) == remote(USER.name)')

    @property
    def condition(self):
        return self.search_target, eval(str(self.search_param))

    @DECO_LAZY
    def items(self):
        model_class = globals()[self.search_target.upper()]
        logic_switch = {'and': and_,
                        'or' : or_}
        multi_switch = {'data': {'tag' : 'tags',
                                 'atom': 'atoms'},
                        'tag' : {'data': 'datas',
                                 'raw' : 'raws'},
                        'raw' : {'data': 'datas',
                                 'tag' : 'tags'}}

        sql_expr = self.session.query(model_class)

        def traverse_filter(raw_filter):
            for key, value in raw_filter.items():
                logic = logic_switch[key]
                param = []
                for sub in value:
                    if isinstance(sub, dict):
                        component = traverse_filter(sub)
                    else:
                        mclass_name, col_name, op, exp_value = sub.split(';', 4)
                        mclass = globals()[mclass_name.upper()]
                        col = getattr(mclass, col_name, None)
                        if op == 'in':
                            if mclass is model_class:
                                component = col.in_(exp_value.split(','))
                            else:
                                component = getattr(model_class,
                                                    multi_switch.get(self.search_target).get(mclass_name)).any(
                                        col.in_(exp_value.split(',')))
                        else:
                            try:
                                attr = filter(lambda e: hasattr(col, e.format(op)),
                                              ['{}', '{}_', '__{}__']
                                              )[0].format(op)
                            except Exception as e:
                                raise e
                            if exp_value == 'null':
                                exp_value = None

                            if mclass is model_class:
                                component = getattr(col, attr)(exp_value)
                            else:
                                component = getattr(model_class,
                                                    multi_switch.get(self.search_target).get(mclass_name)).any(
                                        getattr(col, attr)(exp_value))

                    param.append(component)

                return logic(*param)

        filter_func = traverse_filter(eval(str(self.search_param)))
        return sql_expr.filter(filter_func)
