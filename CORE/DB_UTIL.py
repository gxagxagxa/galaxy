#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from DB_CONNECT import *
from itertools import chain


class DB_UTIL(object):
    @classmethod
    def refresh(cls, session, orm_or_list):
        if isinstance(orm_or_list, (list, tuple)):
            return [session.query(x.__class__).filter(x.__class__.sid == x.sid).one() if isinstance(x, DB_BASE) else x
                    for x in orm_or_list]
        else:
            return session.query(orm_or_list.__class__).filter(orm_or_list.__class__.sid == orm_or_list.sid).one()

    @classmethod
    def hierarchy(cls, session, orm, posix=False):
        pass

    @classmethod
    def get_root(cls, session):
        return session.query(ATOM).filter(ATOM.name == ROOT_ATOM_NAME).one()

    @classmethod
    def file_size(cls, session, orm):
        def recursive_calculate(orm, result=None):
            if result is None:
                result = []

            if isinstance(orm, (ATOM, VIEW)):
                for x in DB_UTIL.traverse(session, orm):
                    # print now_dict['current'].name, x.name
                    resolve_atom = x.target if isinstance(x, VIEW) else x
                    recursive_calculate(resolve_atom, result=result)

            elif isinstance(orm, (DATA, RAW)):
                result.append(orm.file_size)

            return result

        if isinstance(orm, (DATA, RAW)):
            return orm.file_size
        else:
            return sum(recursive_calculate(orm))

    @classmethod
    def traverse(cls, session, orm, recursive=False):
        def non_recursive_traverse(orm, result=None):
            if isinstance(orm, (ATOM, VIEW)):
                return chain(*[value for value in orm.items.values()])

        def recursive_traverse(orm, result=None):
            if result is None:
                result = {'current' : orm,
                          'children': []}

            now_dict = result
            if isinstance(orm, (ATOM, VIEW)):
                for x in non_recursive_traverse(orm):
                    # print now_dict['current'].name, x.name
                    now_dict['children'].append({'current': x, 'children': []})
                    resolve_atom = x.target if isinstance(x, VIEW) else x
                    recursive_traverse(resolve_atom, result=now_dict['children'][-1])

            elif isinstance(orm, (DATA, RAW)):
                now_dict['children'].append({'current': orm, 'children': []})

            return result

        if isinstance(orm, (DATA, RAW)):
            return None

        if recursive:
            return recursive_traverse(orm)
        else:
            return non_recursive_traverse(orm)

    @classmethod
    def advanced_filter(cls, session, model_class_name, m_filter, sql_expr=None):
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

    ss = sess()
    root = DB_UTIL.get_root(ss)
    # print root
    # print DB_UTIL.traverse(ss, root, recursive=True)
    aa = DB_UTIL.traverse(ss, root, recursive=True)

    print [x['current'].name for x in aa['children'][0]['children']]
    # print x.name
