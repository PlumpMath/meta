# coding=utf-8
# Copyright 2016 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import inspect
import itertools
import json
import sys
from collections import OrderedDict
from contextlib import contextmanager

from .compat import *
from .type import Type


class _Null(object):
    _instance = None

    def __repr__(self):
        return 'Null'

    def __bool__(self):
        return False

    __nonzero__ = __bool__


Null = _Null()


class Error(object):
    def __init__(self, path):
        value = path[-1]
        self.value = value.value
        self.exc_info = value.exc_info
        if len(path) > 1:
            self.location = '/' + '/'.join(map(str, path[:-1]))
        else:
            self.location = ''

    def __repr__(self):
        name = 'Error' if self.exc_info is None else self.exc_info[0].__name__
        return "%s(%s%s)" % (name, self.location, '?' if self.value is Null else '')


class Context(Type.Options):
    """Serialization 을 제어하는데 사용된다.

    :py:meth:`Entity.dump` 와 :py:meth:`Entity.load` 에 :py:class:`Context` 인스턴스를 제공하면 다음과 같은 효과가 있다.

    - :py:class:`Property` 에 제공한 ``codec`` 옵션이 활성화 된다.
    - ``view`` 옵션을 통해 :py:class:`Property` 들의 visibility 를 제어할 수 있다.
    - ``strict`` 옵션을 통해 :py:meth:`Entity.load` 에 적용되는 검사의 수준을 정할 수 있다.
    - serialization 과정에서 발생하는 에러에 관한 정보가 제공된다.

    :py:meth:`Entity.validate` 에도 :py:class:`Context` 인스턴스를 제공하면 에러 정보를 받을 수 있다.

    다음과 같은 옵션을 지정할 수 있다.

    max_errors
        1 보다 큰 값을 지정하면 지정한 수를 초과하지 않는한 에러가 발생해도 계속 진행한다. 발견된 에러의 목록은 ``errors`` 를 통해 제공된다.

        여러 에러가 발생한 경우 마지막 에러가 예외를 일으킨다.

        기본 값은 1.
    strict
        False 면 :py:class:`Entity` 에서 정의되지 않은 키를 만나도 에러를 발생시키지 않고 무시한다.

        기본 값은 False.
    view
        ``view`` 옵션이 지정된 :py:class:`Property` 들의 visibility 를 제어한다.

        지정되지 않으면 visibility 제어가 중단된다.

        줄 수 있는 값의 조건은 :py:class:`Property` 의 ``view`` 옵션과 동일하다.

        :py:class:`Context` 의 ``view`` 에 단일 값이 제공된 경우는 :py:class:`Property` 의 ``view`` 옵션 설명을 따른다.
        목록이 제공된 경우는 각 ``view`` 가 AND 로 연결된다. 즉 목록중 어느 하나라도 포함하지 않는 :py:class:`Property` 는 제외된다.

    Example:

        .. literalinclude:: /../tests/ex/context.rst

    Since version 1.0.
    """
    _cs_codecs_ = {}
    _cm_codecs_ = None
    _explicit_ = True
    view = None
    strict = False
    max_errors = 1

    def __init__(self, **kwargs):
        super(Context, self).__init__(**kwargs)
        self._compile_set('view')
        self.reset()

    def __repr__(self):
        if self.errors is None:
            args = None
        else:
            args = ['errors=%s' % repr(self.errors)]
        return super(Context, self).__repr__(args=args)

    @classmethod
    def set_global_codec(cls, name, codec):
        cls._cs_codecs_[name] = codec

    @classmethod
    def get_global_codec(cls, name):
        if name not in cls._cs_codecs_:
            raise LookupError('unknown codec: %s' % name)
        return cls._cs_codecs_[name]

    def set_codec(self, name, codec):
        """
        Context-local :py:class:`Codec` 을 등록한다.

        ``codec`` 으로 :py:class:`Codec` 의 인스턴스를 제공하면,
        :py:class:`Context` 별로 다른 :py:class:`Codec` 이 사용되도록 할 수 있다.
        """
        if self._cm_codecs_ is None:
            self._cm_codecs_ = {name: codec}
        else:
            self._cm_codecs_[name] = codec

    def get_codec(self, name):
        if self._cm_codecs_ is not None and name in self._cm_codecs_:
            return self._cm_codecs_[name]
        return self.get_global_codec(name)

    def reset(self):
        """
        인스턴스를 초기 상태로 되돌린다.

        옵션 값들은 영향을 받지 않고, ``errors`` 는 None 으로 초기화 된다.

        에러가 발생한 경우 인스턴스를 재사용하려면 먼저 이 메쏘드를 호출해주어야 한다.

        Since version 1.0.
        """
        self._markers = set()
        self._errtree = None
        self._errcnt = 0
        self._errors = None

    @property
    def errors(self):
        """
        에러 목록.

        에러가 발생하지 않으면 None.

        에러가 발생하면 다음과 같은 어트리뷰트를 갖는 에러 객체들의 목록이 제공된다. 에러가 발생한 순서는 보존된다.

        목록의 최대 길이는 :py:class:`Context` 의 ``max_errors`` 옵션으로 지정할 수 있다.

        exc_info
            예외가 발생한 경우 `(type, value, traceback)` 튜플을 제공한다. 그렇지 않은 경우 None.

            Since version 1.0.
        location
            에러를 일으킨 값의 위치를 가리키는 `JSON Pointer <https://tools.ietf.org/html/rfc6901>`_.

            :py:class:`dict` 나 :py:class:`Entity` 의 키에 문제가 있는 경우 ``location`` 은 키를 포함한다.

            사용되는 키는 입력을 기준으로 한다. 가령 ``name`` 옵션이 지정된 :py:class:`Property` 가 포함된 경우,
            :py:meth:`Entity.dump` 와 :py:meth:`Entity.validate` 에서는 어트리뷰트명이 사용되고,
            :py:meth:`Entity.load` 에서는 ``name`` 옵션으로 지정한 값이 사용된다.

            Since version 1.0.
        value
            에러를 일으킨 값.

            :py:data:`Null` 은 값이 없음을 나타낸다.

            ``location`` 이 :py:class:`dict` 나 :py:class:`Entity` 의 키를 가리키는 경우,
            ``value`` 가 :py:data:`Null` 이면 키에 문제가 있다는 뜻이고, 그렇지 않으면 값에 문제가 있다는 뜻이다.
            키에 문제가 있다는 뜻은, 있어야 할 키가 존재하지 않거나, 사용될 수 없는 키가 발견되었다는 것이다.

            Since version 1.0.

        Since version 1.0.
        """
        if self._errors is None:
            if self._errtree is not None:
                def walk(node):
                    if isinstance(node, Value):
                        yield [node]
                    else:
                        for key, val in node.items():
                            for x in walk(val):
                                if key is None:
                                    yield x
                                else:
                                    yield [key] + x

                self._errors = [Error(x) for x in walk(self._errtree)]
                # reset tree, but keep markers
                self._errtree = None
        return self._errors

    def _unknown_option(self, key):
        raise TypeError("context got an unexpected option '%s'" % key)

    def copy(self):
        ctx = Context()
        ctx.__dict__.update(self.__dict__)
        ctx.reset()
        ctx._markers = self._markers.copy()
        return ctx


class Codec(object):
    """
    커스텀 코덱을 만들때 사용된다.

    코덱은 :py:meth:`Codec.register` 데코레이터로 이름이 부여되고,
    :py:class:`Property` 의 ``codec`` 옵션에 이 이름을 제공하면 serialization 과정에 코덱이 삽입되게 된다.

    :py:meth:`Entity.dump` 는 마지막에 :py:meth:`Codec.encode` 를 호출하고, :py:meth:`Entity.load` 는 처음에
    :py:meth:`Codec.decode` 를 호출한다.

    Example:

        .. literalinclude:: /../tests/ex/codec.rst

    Since version 1.0.
    """

    @staticmethod
    def register(name):
        def deco(cls):
            Context.set_global_codec(name, cls())

        return deco

    def encode(self, value, property, context):
        """
        :py:meth:`Entity.dump` 에서 실행되는 메쏘드.

        찻번째 코덱은 코덱이 없을 때 :py:meth:`Entity.dump` 가 돌려주는 값을 ``value`` 로 받는다.
        그 뒤의 코덱은 앞의 코덱이 :py:meth:`Codec.encode` 에서 돌려준 값을 받는다.

        ``property`` 는 :py:class:`Property` 인스턴스가 전달되고, ``context`` 로는 :py:class:`Context` 인스턴스나 None 이 전달된다.
        일반적인 코덱에서는 이 두 값을 참조할 필요는 없다.

        변환한 값을 돌려줘야 한다.

        커스텀 코덱은 이 메쏘드를 구현해야 한다. 기본 구현은 ``value`` 를 돌려준다.

        Since version 1.0.
        """
        return value

    def decode(self, value, property, context):
        """
        :py:meth:`Entity.load` 에서 실행되는 메쏘드.

        마지막 코덱은 코덱이 없을 때 :py:meth:`Entity.load` 가 돌려주는 값을 ``value`` 로 받는다.
        그 앞의 코덱은 뒤의 코덱이 :py:meth:`Codec.decode` 에서 돌려준 값을 받는다.

        ``property`` 는 :py:class:`Property` 인스턴스가 전달되고, ``context`` 로는 :py:class:`Context` 인스턴스나 None 이 전달된다.
        일반적인 코덱에서는 이 두 값을 참조할 필요는 없다.

        변환한 값을 돌려줘야 한다.

        커스텀 코덱은 이 메쏘드를 구현해야 한다. 기본 구현은 ``value`` 를 돌려준다.

        Since version 1.0.
        """
        return value


def codec(name, *args, **kwargs):
    """
    옵션이 적용된 코덱을 돌려준다.

    ``name`` 은 코덱의 이름이고, 뒤로 인자를 줄 수 있다.

    Example

        .. literalinclude:: /../tests/ex/codec_func.rst

    Since version 1.0.
    """
    return Context.get_global_codec(name).__class__(*args, **kwargs)


@Codec.register('json')
class JsonCodec(Codec):
    def __init__(self, sort_keys=False):
        self.sort_keys = sort_keys

    def encode(self, value, property, context):
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=self.sort_keys)

    def decode(self, value, property, context):
        return json.loads(value)


class Value(object):
    def __init__(self, value, exc_info):
        self.value = value
        self.exc_info = exc_info


class CursorExit(Exception): pass


class Marker(object):
    pending = None
    exc_info = None

    def __init__(self, context, value, check=True):
        self._check = check
        self.value = value
        if context is not None:
            if check:
                if id(value) in context._markers:
                    raise OverflowError()
            self.context = context
        else:
            self.context = Context()
            self.context._explicit_ = False

    def isvisited(self, value):
        return self.context is not None and id(value) in self.context._markers

    def __enter__(self):
        if self._check:
            self.context._markers.add(id(self.value))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._check:
            self.context._markers.remove(id(self.value))
        if exc_type is None:
            if self.pending:
                self.context._errtree = self.pending
                throw_exc_info(self.exc_info)
        elif exc_type is CursorExit:
            self.context._errtree = self.pending
            throw_exc_info(self.exc_info)
        else:
            if self.context._errtree is None:
                val = Value(self.value, (exc_type, exc_val, exc_tb))
                self.context._errcnt += 1
                if self.pending:
                    self.pending[None] = val
                    self.context._errtree = self.pending
                else:
                    self.context._errtree = val
            else:
                if self.pending:
                    self.context._errtree = self.pending

    @contextmanager
    def cursor(self, key, value):
        try:
            yield
        except:
            if self.pending is None:
                self.pending = OrderedDict()
            if self.context._errtree is None:
                self.pending[key] = Value(value, sys.exc_info())
                self.context._errcnt += 1
            else:
                self.pending[key] = self.context._errtree
                self.context._errtree = None
            self.exc_info = sys.exc_info()
            if self.context._errcnt >= self.context.max_errors:
                raise CursorExit()


class Tuplizer(object):
    def __init__(self, cls, repeat):
        self.cls = cls
        self.repeat = repeat

    def __call__(self, *args, **kwargs):
        return Tuple(self.cls(*args, **kwargs), repeat=self.repeat)


class Property(Type):
    """
    :py:class:`Entity`, :py:class:`Union`, :py:class:`Tuple` 의 member 속성을 정의한다.

    이 클래스는 추상 클래스이기 때문에 :py:class:`Entity` 에 직접 사용될 수는 없다. 새로운 :py:class:`Property` 를 정의하고자할 때 베이스 클래스로 사용된다.

    :py:class:`Property` 인스턴스를 만들 때 제공되는 키워드 옵션을 통해 다음과 같은 공통 속성들을 지정할 수 있다.

    required
        True 면 값이 정의되지 않을 수도 :py:class:`Null` 이 올 수도 없다는 뜻이다.

        False 면 값이 정의되지 않을 수도 있고, :py:class:`Entity` 의 경우는 :py:class:`Null` 이 올 수도 있다는 뜻이다.

        마찬가지로 :py:class:`Tuple` 에 사용되는 :py:class:`Property` 에서는 이 옵션이 해당 위치에 None 이 올 수 있느냐를 결정한다.

        :py:class:`Union` 을 정의하는데 사용되는 :py:class:`Property` 는 이 옵션이 무시된다.

        기본값은 False.

            .. literalinclude:: /../tests/ex/property_required.rst

    default
        값이 정의되지 않았을 때 기본 값으로 사용할 값을 준다. callable 을 주면 ``default()`` 를 사용한다.

        ``default`` 는 값이 정의되지 않은 상태에 있는 :py:class:`Property` 를 읽으려 할 때 참조되어 :py:class:`Property` 에 값을 부여한다.
        이후에는 값이 정의된 상태가 되기 때문에 ``default`` 는 다시 참조되지 않는다.

        ``default`` 로 값을 줄 경우 항상 그 값이 그대로 사용된다는 점에 유의해야 한다.
        ``default=meta.DateTime.now()`` 는 아마도 기대한 결과를 주지 않을 것이다.
        ``default=meta.DateTime.now`` 가 올바른 사용법이다.
        값이 mutable 한 경우도 역시 위험하다. 모두 같은 값이 제공되게 되는데 어느 한 곳에서 수정하면 모두 영향을 받기 때문이다.
        이런 경우 callable 을 사용해서 매번 다른 인스턴스를 제공하는 것이 좋다. 가령 ``default=[]`` 보다는 ``default=list`` 가 안전하다.

        ``required=True`` 와 ``default`` 가 같이 사용되면, ``required`` 의 의미를 살짝 완화시키는 효과를 준다.
        :py:meth:`Entity.validate` 할 때 ``default`` 를 사용하게 되는데, 결과적으로 입력 데이터에 값이 생략되어 있어도 통과하게 된다는 뜻이다.

        :py:meth:`Entity.dump` 와 :py:meth:`Entity.validate` 는 이 값을 참조한다.

        :py:class:`Entity` 의 :py:class:`dict` 인터페이스는 :py:meth:`Entity.__getitem__` 와 :py:meth:`Entity.get` 을 제외하고는 ``default`` 를 참조하지 않는다.

        :py:class:`Union` 을 정의하는데 사용되는 :py:class:`Property` 는 이 옵션이 무시된다.

            .. literalinclude:: /../tests/ex/property_default.rst

    validate
        :py:class:`Property` 가 갖고 있는 특성에 더해, 값의 범위를 더 제한하고자 할 때 callable 을 전달할 수 있다.
        False 를 돌려주면 :py:exc:`ValueError` 예외를 일으킨다.

            .. literalinclude:: /../tests/ex/property_validate.rst

    view
        :py:class:`Context` 를 통해 :py:class:`Property` 의 visibility 를 제어할 때 사용된다.

        :py:class:`set` 에 들어갈 수 있는 값을 줄 수 있는데, 단일 값이나 목록이 모두 가능하다.

        :py:class:`Context` 가 지정한 값이 포함되어 있으면 visible 하다.
        :py:class:`Context` 가 없거나, :py:class:`Context` 에서 특별한 값을 지정하지 않아도 visible 하다.

        visible 하지 않을 경우 :py:class:`Property` 가 정의되지 않은 것처럼 동작한다.

        ``required`` 가 True 면 사용할 수 없다.

            .. literalinclude:: /../tests/ex/property_view.rst

    name
        Serialization 에서 사용되는 이름을 변경할 때 사용한다.

        :py:class:`Property` 가 :py:class:`Entity` 에 사용될 경우, serialization 은 이름을 필요로 한다.
        보통 이 이름은 :py:class:`Property` 가 연결된 어트리뷰트의 이름이다. 하지만 어트리뷰트의 이름으로 사용하기 곤란한 두가지 경우가 있다.

        - 파이썬의 문법이 어트리뷰트 이름으로 허락하지 않는 경우.
        - :py:class:`Entity` 의 멤버 이름과 충돌할 경우.

        두 가지 경우 모두 어트리뷰트의 이름을 바꾸고, ``name`` 을 지정하면 된다.

        :py:class:`Entity` 이외에서 사용되는 :py:class:`Property` 는 이 옵션이 무시된다.

            .. literalinclude:: /../tests/ex/property_name.rst

    codec
        Serialization 에서 사용되는 코덱을 지정한다.

        코덱의 이름이나 이름의 목록을 줄 수 있다. 코덱에 제공할 옵션이 필요하면 :py:func:`codec` 을 사용할 수 있다.

        목록이 제공되는 경우 :py:meth:`Entity.dump` 는 마지막에 정방향으로, :py:meth:`Entity.load` 는 처음에 역방향으로 적용된다.

        코덱은 :py:meth:`Entity.dump` 나 :py:meth:`Entity.load` 에 :py:class:`Context` 를 제공하는 경우에만 작동하고,
        그 외의 경우는 무시된다. 따라서 serialization 이라는 제한된 용도로만 사용되어야 한다.

        코덱은 다음과 같거나 유사한 목적에 사용될 수 있다.

        - Serialization 을 외부 형식과 상호 변환할 때.
        - 특정 값을 암호/복호화 할 때.

        사용자는 :py:class:`Codec` 을 사용해서 커스텀 코덱을 등록할 수 있다. 미리 정의되어 있어 등록 절차 없이 사용할 수 있는 코덱은 다음과 같다.

        json
            JSON 문자열로 변환한다.

            다음과 같은 옵션을 제공한다.

            sort_keys
                :py:class:`dict` 의 키를 정렬한다. :py:class:`Property` 의 ``ordered`` 옵션이 무시되게 된다.

                기본 값은 False.

                .. literalinclude:: /../tests/ex/property_codec_json.rst

    ordered
        :py:class:`Entity` 와 :py:class:`Union` 정의에 사용되는 :py:class:`Property` 에 순서를 부여하기 위해 사용된다.

        :py:class:`Entity` 에 ``ordered`` 가 True 인 :py:class:`Property` 가 포함되면 :py:meth:`Entity.dump` 는
        :py:class:`collections.OrderedDict` 를 돌려준다. 순서는 ``ordered`` 가 True 인 :py:class:`Property` 가 선언 순서대로 앞에 오고,
        나머지 가 순서 없이 뒤를 따른다. 이 순서를 따질 때는 베이스 클래스에서 정의된 :py:class:`Property` 까지 함께 고려된다.

        :py:class:`collections.OrderedDict` 를 고려할지여부는 사용자에게 달려있다. 내장된 ``json`` 코덱은 :py:meth:`Entity.dump` 시에
        :py:class:`collections.OrderedDict` 순서를 유지한다.

        :py:meth:`Union.load` 에서는 이 순서가 :py:class:`Property` 우선 순위를 결정한다.
        순서상 앞의 :py:class:`Property` 에서 매치가 발생하면 뒤에오는 :py:class:`Property` 는 검사하지 않는다.

        기본값은 False 다.

            .. literalinclude:: /../tests/ex/property_ordered.rst

    Since version 1.0.
    """
    _ps_count_ = itertools.count()
    _pm_opts_ = None
    _pm_key_ = None
    _pm_order_ = None

    class MetaOptions(Type.MetaOptions):
        _options = 'Options'  # name of Options class

    class Options(Type.Options):
        required = False
        view = None
        default = None  # callable
        name = None
        validate = None
        codec = None

        def __init__(self, **kwargs):
            super(Property.Options, self).__init__(**kwargs)
            if self.view is not None:
                if self.required:
                    raise TypeError('view option cannot be used with required property.')
                self._compile_set('view')
            if self.name is not None:
                key = make_key(self.name)
                if self.name is not key:
                    self.name = key
            if self.codec is not None:
                if not isinstance(self.codec, (tuple, list)):
                    self.codec = (self.codec,)

        def _unknown_option(self, key):
            raise TypeError("property got an unexpected option '%s'" % key)

    def __init__(self, ordered=None, **kwargs):
        self._pm_opts_ = getattr(self, self.MetaOptions._options)(**kwargs)
        if ordered:
            self._pm_order_ = next(self._ps_count_)

    def __repr__(self, args=None, opts=None):
        if args is None:
            args = []
        xargs = []
        if self._pm_order_ is not None:
            xargs.append('ordered=True')
        xargs.extend('%s=%s' % (k, repr(v)) for k, v in self._pm_opts_.__dict__.items())
        if opts is not None:
            xargs.extend(opts)
        return '%s(%s)' % (self.__class__.__name__, ', '.join(args + sorted(xargs)))

    #
    # ordered property
    #

    def is_ordered(self):
        """
        ``ordered`` 옵션이 True 로 제공되면 True.

        Since version 1.0.
        """
        return self._pm_order_ is not None

    #
    # constructor options
    #

    def get_options(self):
        """
        인스턴스를 만들 때 제공된 옵션들.

        :py:class:`Property.Options` 의 인스턴스다. 옵션은 같은 이름의 인스턴스 어트리뷰트로 제공된다.

        Since version 1.0.
        """
        return self._pm_opts_

    def apply_options(self, ordered=None, **kwargs):
        """
        이미 생성된 :py:class:`Property` 의 옵션을 업데이트한다.

        ``self`` 를 돌려준다.

        인스턴스를 만들 때 옵션을 주기가 곤란한 경우 사용된다.

            .. literalinclude:: /../tests/ex/property_apply_options.rst

        Since version 1.0.
        """
        opts = getattr(self, self.MetaOptions._options)(**kwargs)
        self._pm_opts_.__dict__.update(opts.__dict__)
        if ordered:
            self._pm_order_ = next(self._ps_count_)
        return self

    #
    # name binding
    #

    def _bind_(self, key, owner):
        """

        @param key: attribute name or index
        @param owner: entity class or container instance
        @return: None
        """
        if self._pm_key_ is not None and self._pm_key_ != key:
            raise AttributeError('multiple binding')
        self._pm_key_ = key

    #
    # property protocol
    #

    def _resolve_name_(self, instance):
        # owner 가 name binding 을 지원하지 않는 경우.
        for key, val in inspect.getmembers(instance.__class__, inspect.isdatadescriptor):
            if val is self:
                self._bind_(key, instance.__class__)
                return key
        return None

    def __get__(self, instance, owner):
        if instance is not None:
            name = self._pm_key_ or self._resolve_name_(instance)
            if name is not None:
                return instance._get_(name)
        return self

    def __set__(self, instance, value):
        name = self._pm_key_ or self._resolve_name_(instance)
        if name is not None:
            if value is not Null:
                value = self.load(value, None)
            elif self._pm_opts_.required:
                raise ValueError()
            instance._set_(self._pm_key_, value)

    def __delete__(self, instance):
        name = self._pm_key_ or self._resolve_name_(instance)
        if name is not None:
            instance._delete_(self._pm_key_)

    #
    # serialization & validation
    #

    def _dump_(self, value, context):
        """
        :py:class:`Property` 의 값을 JSON serializable 로 변환한다.

        `Property` 의 값은 :py:meth:`Property._load_` 가 정의한다.

        :py:class:`Property` 의 기본 옵션들은 신경쓰지 않아도 되지만, 새로 정의한 옵션들이 있다면 여기에서 고려해야 한다.

        새로운 :py:class:`Property` 를 정의할 때는 이 메쏘드를 반드시 구현해야 한다. 기본 구현은
        :py:exc:`ValueError` 예외를 발생시킨다.

        :param value: :py:class:`Property` 값. None 이나 :py:data:`Null` 이 올 수 없다.
        :param context: :py:class:`Context` 의 인스턴스 또는 None.
        :return: JSON serializable.

        Since version 1.0.
        """
        raise ValueError()

    def _load_(self, value, context):
        """
        JSON serializable 을 :py:class:`Property` 의 값으로 변환한다.

        :py:class:`Property` 의 값은 크게 두가지 유형이 있다.

        - 다른 클래스의 인스턴스를 값으로 사용하는 경우. 파이썬의 내장 형을 사용하는 것도 이 유형에 해당한다.
        - :py:class:`Property` 클래스 자체를 값으로 사용하는 경우.

        어느 경우건 여기에서 결정되며, 새로운 인스턴스를 만들어 돌려줘야 한다. ``self`` 를 돌려주는 것은 금지된다.

        :py:class:`Property` 의 기본 옵션들은 신경쓰지 않아도 되지만, 새로 정의한 옵션들이 있다면 여기에서 고려해야 한다.

        새로운 :py:class:`Property` 를 정의할 때는 이 메쏘드를 반드시 구현해야 한다. 기본 구현은
        :py:exc:`ValueError` 예외를 발생시킨다.

        :param value: JSON serializable. None 이 올 수 없다.
        :param context: :py:class:`Context` 의 인스턴스 또는 None.
        :return: :py:class:`Property` 값. None 을 줄 수 없다.

        Since version 1.0.
        """
        raise ValueError()

    def dump(self, value, context=None):
        if value is None:
            return None
        value = self._dump_(value, context)
        if context is not None and context._explicit_ and self._pm_opts_.codec is not None:
            for name_or_codec in self._pm_opts_.codec:
                if isinstance(name_or_codec, Codec):
                    codec = name_or_codec
                else:
                    codec = context.get_codec(name_or_codec)
                value = codec.encode(value, self, context)
        return value

    def load(self, value, context=None):
        with Marker(context, value, check=False) as marker:
            if value is None:
                if self._pm_opts_.required:
                    raise ValueError()
                return None
            if context is not None and context._explicit_ and self._pm_opts_.codec is not None:
                for name_or_codec in reversed(self._pm_opts_.codec):
                    if isinstance(name_or_codec, Codec):
                        codec = name_or_codec
                    else:
                        codec = marker.context.get_codec(name_or_codec)
                    value = codec.decode(value, self, marker.context)
            value = self._load_(value, marker.context)
            if self._pm_opts_.validate is not None:
                if not self._pm_opts_.validate(value):
                    raise ValueError()
            return value

    #
    # visibility control
    #

    def _isvisible_(self, context):
        if context is not None:
            view = self._pm_opts_.view
            if view is not None:
                if context.view is not None:
                    return view.issuperset(context.view)
        return True

    #
    # tuplization
    #

    @classmethod
    def _getitem_(cls, item):
        return Tuplizer(cls, item)


class Container(Property):
    _cm_args_ = []

    def __init__(self, *properties, **kwargs):
        super(Container, self).__init__(**kwargs)
        for i, arg in enumerate(properties):
            if not isinstance(arg, Property):
                raise TypeError('%s expects properties, but given %s' % (self.__class__.__name__, repr(arg)))
            arg._bind_(i, self)
        self._cm_args_ = list(properties)

    def __repr__(self, args=None, opts=None):
        if args is None:
            args = []
        args.extend(repr(arg) for arg in self._cm_args_)
        return super(Container, self).__repr__(args=args, opts=opts)

    def get_components(self):
        return self._cm_args_

    #
    # property reference resolution
    #

    def _resolve_(self, key, resolved):
        if not isinstance(self._cm_args_[key], Proxy):
            raise TypeError('unauthorized')
        self._cm_args_[key] = resolved


class Proxy(Property):
    def __init__(self, factory, args, kwargs):
        opts = {}
        for key in ('required', 'view', 'ordered'):
            if key in kwargs:
                opts[key] = kwargs[key]
        super(Proxy, self).__init__(**opts)
        self.factory = factory
        if factory is not self._resolve():
            # Factory.__call__ 이 호출되었다는 뜻이기 때문에, 이 시점에 클래스가 정의될 가능성은 없다.
            raise RuntimeError('@declare supports module level classes only.')
        self.args = args
        self.kwargs = kwargs
        self.owner = None

    def _resolve(self):
        if self.factory.frame is None:
            module = sys.modules.get(self.factory.klass.__module__)
            return getattr(module, self.factory.klass.__name__, None)
        else:
            return self.factory.frame.f_locals.get(self.factory.klass.__name__)

    def resolve(self):
        klass = self._resolve()
        if klass is not self.factory and issubclass(klass, Property):
            if self.owner is not None:
                property = klass(*self.args, **self.kwargs)
                self.owner._resolve_(self._pm_key_, property)
                property._bind_(self._pm_key_, self.owner)
                return property
        raise ReferenceError('unresolved class %s.%s' % (self.factory.klass.__module__, self.factory.klass.__name__))

    def __set__(self, instance, value):
        property = self.resolve()
        property.__set__(instance, value)

    def load(self, serialized, context=None):
        property = self.resolve()
        return property.load(serialized, context)

    def dump(self, value, context=None):
        property = self.resolve()
        return property.dump(value, context)

    def _bind_(self, key, owner):
        super(Proxy, self)._bind_(key, owner)
        self.owner = owner
        self.kwargs.update(self._pm_opts_.__dict__)


def declare(property):
    class Factory(object):
        def __init__(self, klass, frame=None):
            self.klass = klass
            self.frame = frame

        def __call__(self, *args, **kwargs):
            return Proxy(self, args, kwargs)

        def __getitem__(self, item):
            return Tuplizer(self, item)

    try:
        frame = sys._getframe(1)
    except:
        frame = None
    return Factory(property, frame)


class Tuple(Container):
    """
    정해진 형태를 갖는 :py:class:`tuple` 을 표현하는 :py:class:`Property`.

    ``properties`` 로 제공한 :py:class:`Property` 의 목록과 일치하는 형태의 :py:class:`tuple` 이나 :py:class:`list` 를 받아들이고,
    :py:class:`tuple` 로 변환한다.

    ``properties`` 올 수 있는 :py:class:`Property` 에 제약은 없다. 때문에 임의의 깊이로 중첩할 수 있다.

    :py:class:`tuple` 이 None 을 포함할 수 있느냐는 ``properties`` 로 제공된 :py:class:`Property` 들의 ``required`` 옵션이 결정한다.

    :py:meth:`Entity.dump` 할 때 :py:class:`list` 를 출력한다.

    :py:class:`Property` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    repeat
        반복을 지정하는데 사용된다. 사용할 수 있는 값은 다음과 같다.

        - 정수나 그 목록
        - :py:class:`slice`
        - :py:data:`Ellipsis`

        모두 ``properties`` 로 지정된 단위가 몇번 등장할 수 있는지를 지정한다. :py:data:`Ellipsis` 는 길이 제약이 없다는 뜻이고, 정수나 그 목록은
        지정한 횟수로 제한한다는 뜻이고, :py:class:`slice` 는 범위를 표현한다.

        기본 값은 1.

    모든 :py:class:`Property` 는 클래스에 ``[]`` 연산자를 적용해서 고정 혹은 가변 길이 homogeneous :py:class:`Tuple` 로 변환할 수 있다.
    ``P[...]()`` 은 ``Tuple(P(), repeat=...)`` 과 같은 표현이다. 이 표현의 장점은 :py:class:`slice` 를 간편하게 제공할 수 있다는 것이고,
    단점은 ``repeat`` 외에는 :py:class:`Tuple` 에 제공할 옵션을 지정할 수 없다는 것이다.
    필요할 경우는 :py:meth:`Property.apply_options` 를 사용할 수 있는데, :py:class:`Tuple` 을 직접적으로 사용하는 것이 분명할 경우가 많다.


    Example

        .. literalinclude:: /../tests/ex/tuple.rst

    Since version 1.0.
    """

    class Options(Container.Options):
        repeat = None

        def __init__(self, **kwargs):
            super(Tuple.Options, self).__init__(**kwargs)
            repeat = self.repeat
            if repeat is not None:
                self.repeat = self._normalize_repeat(self.repeat)

        def _normalize_repeat(self, repeat):
            if isinstance(repeat, frozenset):
                return repeat
            elif isinstance(repeat, slice):
                # ensure step > 0 and start is not None
                start, stop, step = repeat.start, repeat.stop, repeat.step
                if step == 0:
                    return slice(0, 0, 1)
                elif step is None:
                    step = 1
                if start is None:
                    start = 0
                if step < 0:
                    if stop is None:
                        stop = -1
                    start, stop, step = stop - step + (stop - start) % step, start - step, -step
                return slice(start, stop, step)
            elif repeat is Ellipsis:
                return slice(0, None, 1)
            elif isinstance(repeat, integer_types):
                return slice(repeat, repeat + 1, 1)
            else:
                return frozenset(repeat)

    def _dump_(self, value, context):
        with Marker(context, value) as marker:
            spec = self.get_components()
            unit = len(spec)
            visible = [p._isvisible_(marker.context) for p in spec]
            encoded = []
            for i, val in enumerate(value):
                with marker.cursor(i, val):
                    j = i % unit
                    if visible[j]:
                        property = spec[j]
                        encoded.append(property.dump(val, marker.context))
                    else:
                        encoded.append(None)
            return encoded

    def _check_length_(self, value, repeat):
        unit = len(self.get_components())
        length = len(value)
        if unit == 0:
            if length != 0:
                raise ValueError('length mismatch')
            return 0
        n, r = divmod(length, unit)
        if r != 0:
            raise ValueError('length mismatch')
        if repeat is None:
            if length != unit:
                raise ValueError('length mismatch')
        else:
            if isinstance(repeat, slice):
                if n < repeat.start or (n - repeat.start) % repeat.step != 0:
                    raise ValueError('length mismatch')
                if repeat.stop is not None and n >= repeat.stop:
                    raise ValueError()
            else:
                if n not in repeat:
                    raise ValueError()
        return n

    def _load_(self, value, context):
        with Marker(context, value) as marker:
            if not isinstance(value, (tuple, list)):
                raise ValueError()
            n = self._check_length_(value, self._pm_opts_.repeat)
            if n == 0:
                return tuple(value)
            decoded = []

            spec = self.get_components()
            unit = len(spec)
            visible = [p._isvisible_(marker.context) for p in spec]
            for i, val in enumerate(value):
                with marker.cursor(i, val):
                    j = i % unit
                    if visible[j]:
                        property = spec[j]
                        if val is None:
                            default = property._pm_opts_.default
                            if default is not None:
                                if callable(default):
                                    default = default()
                                val = default
                        decoded.append(property.load(val, marker.context))
                    else:
                        if val is not None:
                            raise ValueError()
                        decoded.append(None)
            return tuple(decoded)


__all__ = [
    'Null',
    'Context',
    'Codec',
    'Marker',
    'Property',
    'Tuple',
    'codec',
    'declare',
]
