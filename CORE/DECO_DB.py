#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from functools import wraps


def DECO_SINGLETON(*args, **kwargs):
    '''
    用于单一实例化。只要在声明class 之前使用@DECO_SINGLETON() 就可以保证
    只要用户参数相同，那么永远返回的都是内存中同一个实例化对象。
    大多用于数据库连接，类似最好只有一个对象的场景
    :param args: 任意
    :param kwargs: 任意
    :return: 声明class 的实例化对象
    '''

    def wrapper_first(cls):
        '''
        实际的封装函数
        :param cls: 被装饰的class
        :return: 实例化对象
        '''

        @wraps(cls)
        def wrapper(*l_args, **l_kwargs):
            if not hasattr(cls, "singleton_instances"):
                cls.singleton_instances = [{'args'    : (l_args, l_kwargs),
                                            'instance': cls(*l_args, **l_kwargs)}]

            if (l_args, l_kwargs) not in [x['args'] for x in cls.singleton_instances]:
                cls.singleton_instances.append({'args'    : (l_args, l_kwargs),
                                                'instance': cls(*l_args, **l_kwargs)})
            # print cls.instances
            index = [x['args'] for x in cls.singleton_instances].index((l_args, l_kwargs))
            return cls.singleton_instances[index]['instance']

        return wrapper

    return wrapper_first


class DECO_LAZY(object):
    '''
    惰性求值的装饰器。
    在任意函数之前使用，就可以保证第二次调用的时候不再计算。
    被装饰的函数最好不要有参数。
    '''

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


