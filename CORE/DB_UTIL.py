#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from DB_CONNECT import *


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

    # m_filter = {'and': [{'or': ['data;name;like;A001', 'tag;name;in;sky']}]}
    # m_filter = {'and': ['data;name;like;%C002%']}
    #
    # kk =  repr(DB_UTIL.advanced_filter(sess(), 'tag', m_filter))
    # print kk
    # print DB_UTIL.advanced_filter(sess(), 'tag', m_filter).all()

    vv1 = sess().query(VIEW).first()
    print vv1.items.get('search').all()[0].items
