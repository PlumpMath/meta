# coding=utf-8
# Copyright 2016 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import inspect


class TypeMeta(type):
    def __init__(cls, name, bases, attrs):
        meta = attrs.get(cls.MetaOptions._metaoptions)
        if meta:
            options = dict(filter(lambda x: not x[0].startswith('_'), inspect.getmembers(meta)))
        else:
            options = {}
        options = cls.MetaOptions(**options)
        cls._init_(cls, attrs, options)

    def __repr__(cls):
        return cls._repr_()

    def __getitem__(cls, item):
        return cls._getitem_(item)


class TypeBase(object):
    _ts_opts_ = None

    class Options(object):
        def __init__(self, **kwargs):
            for key in kwargs:
                if hasattr(self, key) and not key.startswith('_'):
                    setattr(self, key, kwargs[key])
                else:
                    self._unknown_option(key)

        def __repr__(self, args=None, opts=None):
            if args is None:
                args = []
            args.extend('%s=%s' % (k, repr(v)) for k, v in self.__dict__.items() if not k.startswith('_'))
            if opts is not None:
                args.extend(opts)
            return '%s(%s)' % (self.__class__.__name__, ', '.join(args))

        def get(self, key, default=None):
            value = getattr(self, key, default)
            return default if value is None else value

        def _unknown_option(self, key):
            pass

        def _compile_set(self, name):
            value = getattr(self, name)
            if value is not None and not isinstance(value, frozenset):
                if isinstance(value, (list, tuple)):
                    if value:
                        setattr(self, name, frozenset(value))
                elif not isinstance(value, frozenset):
                    setattr(self, name, frozenset([value]))

    class MetaOptions(Options):
        _metaoptions = 'Meta'  # name of Meta class

        def _unknown_option(self, key):
            raise TypeError("class %s got an unexpected member '%s'" % (self._metaoptions, key))

    @staticmethod
    def _init_(cls, attrs, options):
        """
        클래스 초기화.

        클래스가 만들어질 때 한번 호출된다.

        @param attrs: 클래스에서 정의된 attribute 들을 담고 있는 dict.
        @param options: 클래스 옵션들. MetaOptions 의 인스턴스다.
        @return: None or typename
        """
        type.__init__(cls, cls.__name__, cls.__bases__, attrs)
        cls._ts_opts_ = options

    @classmethod
    def _repr_(cls, args=None):
        metas = ['%s=%s' % (k, repr(v)) for k, v in cls._ts_opts_.__dict__.items()]
        if metas:
            meta = '.Meta(%s)' % ', '.join(metas)
        else:
            meta = ''
        if args is None:
            args = []
        return 'class %s.%s(%s)%s at 0x%x' % (cls.__module__, cls.__name__, ', '.join(args), meta, id(cls))

    @classmethod
    def _getitem_(cls, item):
        raise TypeError("'%s' object has no attribute '_getitem_'" % cls.__name__)

    def get_class_options(self):
        """
        ``Meta`` 내부 클래스로 제공된 옵션들.

        :py:class:`Entity.MetaOptions` 의 인스턴스다. 옵션은 같은 이름의 인스턴스 어트리뷰트로 제공된다.

        Since version 1.0.
        """
        return self._ts_opts_


Type = TypeMeta('Type', (TypeBase,), {})

__all__ = [
]
