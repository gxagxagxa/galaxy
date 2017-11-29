#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from DB_CONNECT import *
from itertools import chain
from collections import deque


class DB_UTIL(object):
    @classmethod
    def refresh(cls, orm_or_list):
        session = sess()
        if isinstance(orm_or_list, (list, tuple)):
            return [session.query(x.__class__).filter(x.__class__.sid == x.sid).one() if isinstance(x, DB_BASE) else x
                    for x in orm_or_list]
        else:
            return session.query(orm_or_list.__class__).filter(orm_or_list.__class__.sid == orm_or_list.sid).one()

    @classmethod
    def hierarchy(cls, orm, posix=False):
        result = [orm]
        up = orm
        while up:
            up = up.parent
            if up:
                result.append(up)
            else:
                break

        if posix:
            return '/' + '/'.join([x.name for x in result[-2::-1]])
        else:
            return result[-2::-1]

    @classmethod
    def goto(cls, posix_path, relative_orm=None):
        if posix_path == '/':
            return [DB_UTIL.get_root()]

        if posix_path.startswith('/'):
            root = DB_UTIL.get_root()
        else:
            if relative_orm:
                root = relative_orm
            else:
                raise Exception('using relative posix path, without giving relative orm')

        result = [root]
        component = posix_path.strip('/').split('/')

        current = root
        for item in component:
            if item == '..':
                current = current.parent

            if item == '.':
                pass

            current = next((x for x in DB_UTIL.traverse(current) if x.name == item), None)
            if current is None:
                result = None
                break

            result.append(current)

        return result

    @classmethod
    def get_root(cls):
        session = sess()
        return session.query(ATOM).filter(ATOM.name == ROOT_ATOM_NAME).one()

    @classmethod
    def file_size(cls, orm):
        total = 0
        for x in DB_UTIL.walk(orm, solve_link=False):
            if isinstance(x, (DATA, RAW)):
                total += x.file_size
        return total

    @staticmethod
    def copy_atom(orm, parent_orm):
        if orm.session is None:
            orm = DB_UTIL.refresh(orm)
        result = ATOM(name=orm.name, parent=parent_orm,
                      extra_info=orm.extra_info, debug_info=orm.debug_info,
                      thumbnail_base64=orm.thumbnail_base64,
                      tags=orm.tags)
        sess().add(result)
        return result

    @staticmethod
    def copy_link(orm, parent_orm):
        if orm.session is None:
            orm = DB_UTIL.refresh(orm)
        result = LINK(name=orm.name, parent=parent_orm,
                      target=parent_orm.target,
                      extra_info=orm.extra_info, debug_info=orm.debug_info,
                      thumbnail_base64=orm.thumbnail_base64)
        sess().add(result)
        return result

    @staticmethod
    def copy_meta(orm, parent_orm):
        if orm.session is None:
            orm = DB_UTIL.refresh(orm)
        result = META(name=orm.name, parent=parent_orm,
                      disk_full_path=orm.disk_full_path,
                      cam_clue=orm.cam_clue,
                      vfx_seq_clue=orm.vfx_seq_clue,
                      vfx_shot_clue=orm.vfx_shot_clue,
                      scene_clue=orm.scene_clue,
                      shot_clue=orm.shot_clue,
                      take_clue=orm.take_clue,
                      extra_info=orm.extra_info, debug_info=orm.debug_info)
        sess().add(result)
        return result

    @staticmethod
    def copy_data(orm, parent_orm):
        if orm.session is None:
            orm = DB_UTIL.refresh(orm)
        result = DATA(name=orm.name, parent=parent_orm,
                      disk_full_path=orm.disk_full_path,
                      cam_clue=orm.cam_clue,
                      vfx_seq_clue=orm.vfx_seq_clue,
                      vfx_shot_clue=orm.vfx_shot_clue,
                      scene_clue=orm.scene_clue,
                      shot_clue=orm.shot_clue,
                      take_clue=orm.take_clue,
                      type_name=orm.type_name,
                      vendor_name=orm.vendor_name,
                      extra_info=orm.extra_info, debug_info=orm.debug_info,
                      thumbnail_base64=orm.thumbnail_base64,
                      file_hash=orm.file_hash,
                      file_size=orm.file_size)
        sess().add(result)
        result.tags = orm.tags
        result.metas = [DB_UTIL.copy_meta(x, result) for x in orm.metas]
        return result

    @staticmethod
    def copy_raw(orm, parent_orm):
        if orm.session is None:
            orm = DB_UTIL.refresh(orm)
        result = RAW(name=orm.name, parent=parent_orm,
                     disk_full_path=orm.disk_full_path,
                     cam_clue=orm.cam_clue,
                     vfx_seq_clue=orm.vfx_seq_clue,
                     vfx_shot_clue=orm.vfx_shot_clue,
                     scene_clue=orm.scene_clue,
                     shot_clue=orm.shot_clue,
                     take_clue=orm.take_clue,
                     reel=orm.reel,
                     in_tc=orm.in_tc,
                     out_tc=orm.out_tc,
                     project_fps=orm.project_fps,
                     fps=orm.fps,
                     extra_info=orm.extra_info, debug_info=orm.debug_info,
                     thumbnail_base64=orm.thumbnail_base64,
                     file_hash=orm.file_hash,
                     file_size=orm.file_size)
        sess().add(result)
        result.tags = orm.tags
        result.metas = [DB_UTIL.copy_meta(x, result) for x in orm.metas]
        return result

    @classmethod
    def deep_copy(cls, from_orm, to_orm):
        result = deque()
        stack = deque()
        stack.append(from_orm)
        first_time = True
        ret = None

        while stack:
            current = stack.popleft()
            new_parent = result.popleft() if len(result) else to_orm
            if first_time:
                func = getattr(DB_UTIL, 'copy_{}'.format(from_orm.__tablename__), None)
                ret = func(current, new_parent)
                new_parent = ret
                first_time = False

            for x in DB_UTIL.traverse(current, solve_link=False):
                func = getattr(DB_UTIL, 'copy_{}'.format(x.__tablename__), None)
                temp = func(x, new_parent)
                result.append(temp)
                stack.append(x)

        return ret

    @classmethod
    def make_atoms(cls, posix_path, parents=True):
        component = posix_path.strip('/').split('/')
        root = DB_UTIL.get_root()
        result = [root]
        current = root

        for item in component:
            up = current
            current = next((x for x in DB_UTIL.traverse(current) if x.name == item), None)
            if current is None:
                if parents:
                    current = ATOM(name=item, parent=up)
                    sess().add(current)
                else:
                    result = None
                    break

            result.append(current)

        return result

    @classmethod
    def walk(cls, orm, solve_link=True):
        stack = deque()
        stack.append(orm)
        while stack:
            current = stack.popleft()
            yield current
            # print DB_UTIL.traverse(current)
            for x in DB_UTIL.traverse(current, solve_link=solve_link):
                stack.append(x)

    @classmethod
    def traverse(cls, orm, recursive=False, solve_link=True):
        def non_recursive_traverse(orm, solve_link=True):
            if (not solve_link) and isinstance(orm, LINK):
                return []

            if isinstance(orm, (ATOM, LINK, TAG, VIEW)):
                return chain(*[value for value in orm.items.values()])
            elif isinstance(orm, (DATA, RAW)):
                return []

        def recursive_traverse(orm, result=None, solve_link=True):
            if result is None:
                result = {'current' : orm,
                          'children': []}

            now_dict = result
            if isinstance(orm, (ATOM, LINK)):
                for x in non_recursive_traverse(orm, solve_link=solve_link):
                    # print now_dict['current'].name, x.name
                    now_dict['children'].append({'current': x, 'children': []})
                    resolve_atom = x.target if isinstance(x, LINK) else x
                    recursive_traverse(resolve_atom, result=now_dict['children'][-1])

            elif isinstance(orm, (DATA, RAW)):
                now_dict['children'].append({'current': orm, 'children': []})

            return result

        if recursive:
            return recursive_traverse(orm, solve_link=solve_link)
        else:
            return non_recursive_traverse(orm, solve_link=solve_link)

    @classmethod
    def advanced_filter(cls, model_class_name, m_filter, sql_expr=None):
        session = sess()
        model_class = globals()[model_class_name.upper()]
        logic_switch = {'and': and_,
                        'or' : or_}
        multi_switch = {'data': {'tag' : 'tags',
                                 'atom': 'atoms'},
                        'tag' : {'data': 'datas',
                                 'raw' : 'raws'},
                        'raw' : {'data': 'datas',
                                 'tag' : 'tags'}}

        sql_expr = sql_expr if sql_expr else session.query(model_class)

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
                                                    multi_switch.get(model_class_name).get(mclass_name)).any(
                                        col.in_(exp_value.split(',')))
                        else:
                            try:
                                attr = filter(lambda e: hasattr(col, e.format(op)),
                                              ['{}', '{}_', '__{}__'])[0].format(op)
                            except Exception as e:
                                raise e
                            if exp_value == 'null':
                                exp_value = None

                            if mclass is model_class:
                                component = getattr(col, attr)(exp_value)
                            else:
                                component = getattr(model_class,
                                                    multi_switch.get(model_class_name).get(mclass_name)).any(
                                        getattr(col, attr)(exp_value))

                    param.append(component)

                return logic(*param)

        filter_func = traverse_filter(m_filter)
        return sql_expr.filter(filter_func)


if __name__ == '__main__':
    # from collections import OrderedDict
    from pprint import pprint

    # m_filter = {'and': [{'or': ['data;name;like;A001', 'tag;name;in;sky']}]}
    # m_filter = {'and': ['data;name;like;%C002%']}
    #
    # kk =  repr(DB_UTIL.advanced_filter(sess(), 'tag', m_filter))
    # print kk
    # print DB_UTIL.advanced_filter(sess(), 'tag', m_filter).all()

    a1 = sess().query(ATOM).get('8e4b930f-cf6a-11e7-99b3-0cc47a73af8f')
    # d1 = DATA(name='ppp', parent=data1)

    # l1 = LINK(name=data1.name, parent=DB_UTIL.get_root(), target=data1)
    # sess().commit()

    # for x in  DB_UTIL.traverse(data1, solve_link=False):
    #     print x

    aa = DB_UTIL.goto('/1/2/3/4/5')
    print aa[-1]

    # time.sleep(20)
