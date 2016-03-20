# coding=utf-8
# Copyright 2016 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json
from collections import OrderedDict

from .compat import *
from .property import Null, Property, Context, Marker, Proxy
from .type import TypeMeta


class Kind(Property):
    """
    :py:class:`Entity` 에 다형성(Polymorphism)을 제공하는 :py:class:`Property`.

    :py:class:`Kind` 를 제공하면 :py:class:`Entity` 는 다형성을 갖게 된다.
    다형성을 갖는 :py:class:`Entity` 를 :py:class:`Property` 로 사용하면,
    :py:class:`Entity` 자신 뿐 아니라 자식 클래스들의 값도 받아들에게 된다.
    :py:meth:`Entity.load` 역시 적절한 자식 클래스의 인스턴스를 만들게 된다.

    다형성을 갖는 :py:class:`Entity` 의 자식 클래스들은, :py:class:`Kind` 로 선언된 어트리뷰트와 같은 이름으로 ``kind`` 값을 제공해야 한다.
    이 값은 문자열, 숫자, :py:class:`tuple` 이 사용될 수 있다. 값이 제공되지 않거나 None 이면 추상(abstract) 클래스로 취급된다.
    추상 클래스의 인스턴스는 다형성을 갖는 :py:class:`Property` 에 값으로 사용할 수 없다.

    부모 클래스들까지 고려해서 :py:class:`Kind` 는 오직 한 번만 사용될 수 있다.

    :py:class:`Kind` 는 :py:class:`Entity` 에만 사용될 수 있다.

    최초에 :py:class:`Kind` 를 선언하는 클래스의 경우 인자로 ``kind`` 값을 제공할 수 있다. 제공하지 않으면 이 역시 추상 클래스가 된다.

    다형성을 최초로 선언한 클래스와 그의 자식 클래스들에서 ``kind`` 값은 중복되지 않아야 한다.
    같은 다형성 부모를 공유하지 않는 클래스들의 ``kind`` 값은 중복되어도 상관없다.

    ``kind`` 값은 :py:meth:`Entity.dump` 할 때 그대로 출력되기 때문에 serealization 을 고려해서 정의해야 한다.

    :py:class:`Kind` 는 읽기만 허락하는 :py:class:`Property` 다. 이 값은 인스턴스의 값이 아니라 클래스의 값으로 취급되고,
    이터레이터나 ``in`` 연산으로는 관찰할 수 없다.

    :py:class:`Property` 의 옵션중 ``name`` 과 ``ordered`` 만을 지원한다.

    Example:

        .. literalinclude:: /../tests/ex/kind.rst

    Since version 1.0.
    """

    def __init__(self, kind=None, required=True, ordered=None, name=None, **kwargs):
        if kind is not None and not isinstance(kind, (basestring_types, integer_types, tuple)):
            raise TypeError("'%s' is not valid kind value" % repr(kind))
        if required is not True:
            raise TypeError("context got an unexpected option 'required'")
        if kwargs:
            raise TypeError("context got an unexpected option '%s'" % kwargs.popitem()[0])
        kwargs = {}
        if ordered is True:
            kwargs['ordered'] = True
        if name is not None:
            kwargs['name'] = name
        super(Kind, self).__init__(required=True, **kwargs)
        self.kind = kind

    def __repr__(self):
        return super(Kind, self).__repr__(args=[repr(self.kind)])

    def __get__(self, instance, owner):
        return self.kind

    def __set__(self, instance, value):
        raise AttributeError("can’t set attribute")

    def __delete__(self, instance):
        pass

    def copy(self, kind):
        instance = Kind(kind, **self._pm_opts_.__dict__)
        if self._pm_order_ is not None:
            instance._pm_order_ = self._pm_order_
        return instance


class Selector(Property):
    """
    :py:class:`Entity` 의 옵션에 따라 형이 결정되는 :py:class:`Property`.

    데코레이터 문법을 사용해서 ``properties`` 로 제공한 :py:class:`Property` 들 중 하나를 선택하는 메쏘드를 제공한다.

    메쏘드는 ``[0, len(properties))`` 범위의 정수를 돌려주어야 한다.

    이 메쏘드는 다른 :py:class:`Property` 들을 참조할 수는 없으나 :py:class:`Entity` 의 옵션을 참조할 수는 있다.

    :py:class:`Property` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/selector.rst

    Since version 1.0.
    """
    _sm_args_ = []
    _select = None

    def __init__(self, *properties, **kwargs):
        super(Selector, self).__init__(**kwargs)
        for arg in properties:
            if not isinstance(arg, Property):
                raise TypeError('%s expects properties, but given %s' % (self.__class__.__name__, repr(arg)))
        self._sm_args_ = list(properties)

    def __call__(self, func):
        self._select = func
        return self

    def _bind_(self, key, owner):
        super(Selector, self)._bind_(key, owner)
        for arg in self._sm_args_:
            arg._bind_(key, owner)

    def __set__(self, instance, value):
        self.select(instance).__set__(instance, value)

    def select(self, instance):
        if self._select is None:
            raise NotImplementedError()
        index = self._select(instance)
        if index is None:
            raise TypeError()
        if index < 0 or index >= len(self._sm_args_):
            raise ValueError()
        return self._sm_args_[index]


class Composite(Property):
    _cs_fields_ = {}  # {key: property}
    _cs_kind_key_ = None
    _cs_kind_ns_ = None  # {kind: entity-class}

    class MetaOptions(Property.MetaOptions):
        freeze = False

    @classmethod
    def _repr_(cls):
        return super(Composite, cls)._repr_(args=['%s=%s' % (k, repr(v)) for k, v in cls._cs_fields_.items()])

    @staticmethod
    def _init_(cls, attrs, options):
        Property._init_(cls, attrs, options)

        kind_key = cls._cs_kind_key_

        # bind properties
        fields = cls._cs_fields_.copy()
        ordered = []
        for key, value in attrs.items():
            if isinstance(value, Property):
                if isinstance(value, Kind):
                    if kind_key is not None:
                        raise TypeError('multiple Kind not allowed')
                    kind_key = key
                value._bind_(key, cls)
                fields[key] = value
                if value._pm_order_ is not None:
                    ordered.append((value._pm_order_, key))

        if kind_key != cls._cs_kind_key_:
            cls._cs_kind_key_ = kind_key
            cls._cs_kind_ns_ = {}
        elif kind_key is not None:
            kind = attrs.get(kind_key)
            if kind is not None:
                if kind in cls._cs_kind_ns_:
                    raise TypeError(
                        "%s '%s' was already registered by %s" % (
                            kind_key, repr(kind), cls._cs_kind_ns_[kind].__name__))
                cls._cs_kind_ns_[kind] = cls
            fields[kind_key] = attrs[kind_key] = fields[kind_key].copy(kind)

        if ordered:
            # TODO: cleanup
            ordered.sort()
            oitems = []
            uitems = []
            items = list(cls._cs_fields_.items())
            for i, (k, v) in enumerate(items):
                if v._pm_order_ is not None:
                    oitems.append((k, v))
                else:
                    uitems = items[i:]
                    break
            attrcopy = attrs.copy()
            for _, k in ordered:
                oitems.append((k, attrcopy.pop(k)))
            uitems.extend([(k, v) for k, v in attrcopy.items() if isinstance(v, Property)])
            fields = OrderedDict(oitems)
            fields.update(uitems)

        cls._cs_fields_ = fields

    #
    # dynamic class generation
    #
    @classmethod
    def define_subclass(cls, name, attrs):
        """
        :py:class:`Entity` 를 명령방식(Imperative)으로 구성한다.

        ``class`` 키워드를 사용하여 선언적으로 :py:class:`Entity` 를 정의하는 방법과는 별도로,
        :py:class:`Property` 들을 기술한 :py:class:`dict` 로 :py:class:`Entity` 클래스를 생성하는 방법을 제공한다.

        ``name`` 으로는 클래스의 이름을, ``attrs`` 로는 어트리뷰트를 :py:class:`dict` 로 제공한다.

        이 메쏘드는 @classmethod 다. 호출되는 클래스를 계승하는 자식 클래스가 만들어진다.

        다음 두 :py:class:`Entity` ``Declarative`` 와 ``Imperative`` 는 동일하다.

            .. literalinclude:: /../tests/ex/entity_define_subclass.py

        Since version 1.0.
        """
        return TypeMeta(name, (cls,), attrs)

    #
    # property reference resolution
    #

    @classmethod
    def _resolve_(cls, key, property):
        if not isinstance(cls._cs_fields_[key], Proxy):
            raise TypeError('unauthorized')
        cls._cs_fields_[key] = property

    #
    # freeze option support
    #

    def __setattr__(self, name, value):
        if hasattr(self.__class__, name):
            if name in self._cs_fields_:
                self._cs_fields_[name].__set__(self, value)
            else:
                self.__dict__[name] = value
        elif self._ts_opts_.freeze:
            raise AttributeError(name)
        else:
            self.__dict__[name] = value

    #
    # validation
    #

    def _validate_(self, context):
        """
        :py:class:`Property` 들 간의 상호 관계를 검사한다.

        :py:class:`Property` 들 간의 상호 관계 검사는 :py:class:`Property` 의 ``validate`` 옵션으로 구현하기가 어렵다.
        이 메쏘드를 구현하는 것이 훨씬 수월한 작업이다.

        모든 :py:class:`Property` 들의 검사가 완료되고, 문제가 없을 때만 호출된다.
        때문에 :py:class:`Property` 들 간의 상호 관계만 조사하면 된다.

        하지만 ``view``, ``only``, ``exclude`` 옵션들을 사용할 경우는 꽤 복잡해질 수 있다. 다음과 같은 원칙이 도움이 될 수 있다.

        1. ``required`` :py:class:`Property` 들은 그냥 검사한다.
        2. 그 외의 :py:class:`Property` 들은 :py:meth:`Entity.get_if_visible` 로 값을 얻어서 None 이 아닌 경우만 검사한다.

        문제가 있으면 False, 그렇지 않으면 True 를 돌려준다.

        Example

            .. literalinclude:: /../tests/ex/entity__validate_.rst

        Since version 1.0.
        """
        return True

    def validate(self, context=None):
        """nullity 와 property 간의 관계만을 검사한다. null 이 아닌 property 들의 값은 이미 검사가 완료되었다."""
        if not self._validate_(context):
            raise ValueError()

    #
    # serialization
    #

    def dump(self, value=Null, context=None):
        """
        :py:class:`Entity` 를 JSON Serializable 로 변환한다.

        JSON serializable 은 다음 형들로만 구성되는 값이다.

        - :py:class:`str`, :py:class:`bytes` (Python 2 의 경우는 unicode 포함)
        - 모든 정수형과 :py:class:`bool`
        - :py:class:`float`
        - 문자열 키를 사용하는 :py:class:`dict` 와 :py:class:`collections.OrderedDict`
        - :py:class:`tuple` 과 :py:class:`list`

        값이 없는 :py:class:`Property` 는 출력하지 않고, :py:data:`Null` 은 None 을 출력한다.

        ``context`` 로 :py:class:`Context` 인스턴스를 제공하면 여러 변화를 줄 수 있다.

        ``ordered`` 옵션에 따라 :py:class:`dict` 또는 :py:class:`collections.OrderedDict` 를 돌려준다.

        Example

            .. literalinclude:: /../tests/ex/entity_dump.rst

        Since version 1.0.
        """
        if context is None and isinstance(value, Context):
            context = value
            value = Null
        return super(Composite, self).dump(self if value is Null else value, context)

    #
    # equality
    #

    def __ne__(self, other):
        return not self.__eq__(other)

    #
    # stringification
    #

    def __unicode__(self):
        return json.dumps(self.dump(), ensure_ascii=False, separators=(',', ':'))

    def __bytes__(self):
        return self.__unicode__().encode('utf-8')

    __str__ = __bytes__ if PY2 else __unicode__


class Entity(Composite):
    """
    여러 :py:class:`Property` 들의 조합으로 만들어지는 값을 표현하는 :py:class:`Property`.

    :py:class:`Entity` 는 :py:class:`Property` 들을 클래스 어트리뷰트로 갖는다.
    이렇게 정의된 :py:class:`Entity` 역시 :py:class:`Property` 가 되어 다른 :py:class:`Entity` 를 정의할 때 사용할 수 있다.

    :py:func:`getattr`, :py:func:`setattr`, :py:func:`delattr` 로 :py:class:`Property` 들의 값에 접근할 수 있다.

    대부분의 :py:class:`Property` 들이 자기 자신이 아닌 별도의 클래스를 값으로 갖는 반면 :py:class:`Entity` 는 스스로 값이 된다.
    따라서 :py:class:`Property` 용도뿐만 아니라 독립적인 사용이 가능하다. 이를 위해 어트리뷰트를 통한 접근과는 별도로,
    :py:class:`dict` 가 제공하는 인터페이스의 대부분을 제공하고, 그 동작도 유사하도록 유지한다.
    하지만 :py:class:`dict` 와는 다음과 같은 차이점이 있다.

        인스턴스를 생성할 때 키워드 옵션은 :py:class:`Property` 옵션으로만 해석된다. ``other`` 인자는 동일하게 해석된다.

        :py:class:`Property` 어트리뷰트에 대한 ``[key]`` 연산은 :py:exc:`KeyError` 예외를 발생시키지 않고 None 을 돌려준다.

        ``[key]`` 연산과 :py:meth:`Entity.get` 은 :py:class:`Property` 의 ``default`` 옵션이 있을 경우 :py:class:`Entity` 를 수정할 수 있다.
        (:py:class:`dict` 인터페이스는 아니지만 :py:meth:`Entity.dump` 역시 같은 효과가 있다.) 다른 인터페이스는 이런 효과가 없다.
        이 때문에 ``in`` 검사가 False 임에도 불구하고 :py:meth:`Entity.get` 하면 None 이 아닌 값이 올 수 있다.

        ``[key]``, :py:meth:`Entity.update` 로 값을 수정하려는 경우 None 은 삭제의 의미로 받아들여진다.
        :py:meth:`Entity.dump` 에서 None 이 출력되도록 하려면 :py:data:`Null` 을 주어야 한다.
        또한 :py:class:`Property` 의 ``required`` 옵션이 True 인 경우 :py:exc:`ValueError` 예외가 발생할 수 있다.
        반면 ``del``, :py:meth:`Entity.clear`, :py:meth:`Entity.pop`, :py:meth:`Entity.popitem` 은 ``required`` 옵션에 영향을
        받지 않는다.

        :py:meth:`Entity.keys`, :py:meth:`Entity.items`, :py:meth:`Entity.values` 는 dictionary view 가 아니라 이터레이터를 제공한다.
        향후 버전에서는 바뀔 수 있다.

        :py:func:`str` 은 JSON 을 돌려준다.

    다음과 같은 값을 받아들여 자신과 같은 형의 인스턴스로 변환한다.

    - 자신 또는 자신의 서브클래스의 인스턴스.(서브클새스는 다형성이 지원되는 경우에만 받아들인다.)
    - :py:class:`dict`

    :py:meth:`Entity.dump` 할 때 :py:class:`dict` 를 출력한다.

    :py:class:`Property` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    exclude
        :py:class:`Property` 어트리뷰트의 이름이나 그 목록을 제공하면 serialization 과정에서 해당 :py:class:`Property` 들이 정의되지
        않은 것처럼 취급한다.
    only
        :py:class:`Property` 어트리뷰트의 이름이나 그 목록을 제공하면 serialization 과정에서 지정한 것들 외의 모든 :py:class:`Property`
        들이 정의되지 않은 것처럼 취급한다. ``exclude`` 에 포함된 이름이 있으면 역시 제거된다.

        ``exclude`` 와 ``only`` 옵션의 기능응 ``view`` 옵션과 중첩되는 부분이 있다.
        하지만 ``view`` 와는 달리 두 옵션은 :py:class:`Context` 의 설정에 영향받지 않기 때문에,
        문맥과 무관한 :py:class:`Entity` 의 구조적 특성을 표현할 때 사용된다.

        주의해야할 점은 :py:meth:`Entity.load` 로 인스턴스가 만들어질 때 이 옵션을 물려받는다는 것이다.
        이 인스턴스의 다른 :py:class:`Property` 들을 설정한 후 :py:meth:`Entity.dump` 해도 출력되지 않는다.
        이 동작이 문제가 될 경우 회피하는 간단한 방법은 이 인스턴스를 인자로 사용해서 다른 인스턴스를 하나 만드는 것이다.

        ``only`` 와 ``exclude`` 는 ``required=True`` 인 :py:class:`Property` 를 제거할 수 없다.

            .. literalinclude:: /../tests/ex/entity_only.rst

    :py:class:`Entity` 는 다음과 같은 개념들을 지원한다.

    계승(Inheritance)
        :py:class:`Entity` 를 정의할 때 베이스 클래스로 이미 정의한 :py:class:`Entity` 를 사용할 수 있다.
        이 때 베이스 :py:class:`Entity` 의 모든 :py:class:`Property` 들은 계승된다.
        베이스 :py:class:`Entity` 가 사용한 것과 같은 이름의 어트리뷰트를 정의하면 베이스 :py:class:`Entity` 의 어트리뷰트는 가려진다.
    다형성(Polymorphism)
        특별한 선언이 없으면 다형성은 지원되지 않는다. 즉 :py:class:`Entity` 를 :py:class:`Property` 로 사용할 때 그 자식 클래스의 인스턴스는 받아들이지 않는다.

        :py:class:`Kind` 를 포함하는 :py:class:`Entity` 는 다형성이 지원된다. 그 자식 클래스의 인스턴스 역시 받아들이며,
        :py:meth:`Entity.dump` 와 :py:meth:`Entity.load` 역시 자식 클래스가 적용된다.

    인스턴스를 생성할 때 제공하는 키워드 옵션들을 통해 :py:class:`Property` 옵션을 지정할 수 있는데, 엔티니는 이를 인스턴스 옵션이라고 부른다.
    :py:class:`Entity` 클래스 자체에 적용되는 옵션들이 따로 관리되는데, 이를 클래스 옵션이라고 부르고, 인스턴스 옵션과는 상관 관계가 없다.
    클래스 옵션은 ``Meta`` 이름의 내부 클래스를 사용해서 제공한다. 옵션을 클래스 어트리뷰트로 제공하면 된다.
    ``Meta`` 로 지정되는 옵션들은 계승되지 않는다. 다음과 같은 클래스 옵션들을 제공한다.

    freeze
        False 면 :py:class:`Entity` 인스턴스에 :py:func:`setattr` 할 경우,
        :py:class:`Property` 로 정의되지 않은 어트리뷰트에 대해서는 관여하지 않는다.

        True 면 클래스 어트리뷰트로 정의되지 않은 경우 :py:exc:`AttributeError` 예외를 일으킨다.

        디버깅을 지원하기 위한 기능이다.

            .. literalinclude:: /../tests/ex/entity_freeze.rst

        기본 값은 False 다.

    Example:

        .. literalinclude:: /../tests/ex/entity.rst

    Since version 1.0.
    """
    _es_names_ = None  # {property._pm_opts_.name : key}
    _em_data_ = None  # {name: property-value}

    class Options(Property.Options):
        only = None
        exclude = None

        def __init__(self, **kwargs):
            super(Entity.Options, self).__init__(**kwargs)
            if (self.only is not None or self.exclude is not None) and not isinstance(self.only, frozenset):
                if self.exclude is not None:
                    if self.only is None:
                        self.only = set(self._es_fields.keys())
                    elif isinstance(self.only, (list, tuple)):
                        self.only = set(self.only)
                    else:
                        self.only = {self.only}
                    for x in (self.exclude if isinstance(self.exclude, (list, tuple)) else [self.exclude]):
                        self.only.discard(x)
                    del self.exclude

                self._compile_set('only')

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('Entity expected at most 1 arguments, got %d' % len(args))
        super(Entity, self).__init__(**kwargs)
        self._em_data_ = {}
        self.update(*args)

    def __repr__(self, args=None, opts=None):
        data = ['%s=%s' % (k, 'Null' if v is Null else repr(v)) for k, v in self.items()]
        if data:
            if args is None:
                args = ['dict(%s)' % ', '.join(data)]
        return super(Entity, self).__repr__(args=args, opts=opts)

    def _copy_(self, *args, **kwargs):
        # __init__ 를 override 하는 클래스의 경우 copy 역시 override 한 후, _copy_ 에 __init__ 인자를 전달해야 한다.
        kwargs.update(self._pm_opts_.__dict__)
        instance = self.__class__(*args, **kwargs)
        instance._em_data_.update(self._em_data_)
        return instance

    @staticmethod
    def _init_(cls, attrs, options):
        Composite._init_(cls, attrs, options)

        # TODO: optimize
        names = {}
        fields = cls._cs_fields_
        for k, p in fields.items():
            name = p._pm_opts_.get('name', k)
            if name in names:
                key = names[name]
                raise AttributeError('name %s was already registered by attribute %s' % (name, key))
            names[name] = k

        cls._es_names_ = names

    #
    # property protocol
    #

    def _get_(self, name):
        if name not in self._em_data_:
            if name == self._cs_kind_key_:
                return self._cs_fields_[name].kind
            default = self._cs_fields_[name]._pm_opts_.default
            if default is not None:
                if callable(default):
                    default = default()
                setattr(self, name, default)
        return self._em_data_.get(name)

    def _set_(self, name, value):
        if value is None:
            self._em_data_.pop(name, None)
        else:
            self._em_data_[name] = value

    def _delete_(self, name):
        self._em_data_.pop(name, None)

    #
    # visibility check
    #

    def is_visible(self, key, context, instance=None):

        if instance is None:
            instance = self

        property = instance._cs_fields_.get(key)
        if property is None:
            return False
        if property._pm_opts_.required:
            return True
        only = self._pm_opts_.only
        if only and key not in only:
            return False
        return property._isvisible_(context)

    def get_if_visible(self, key, context):
        """
        키가 현재 문맥에서 노출되는 경우 값을 돌려준다.

        노출되지 않거나 그 값이 :py:data:`Null` 이면 None 을 돌려준다.

        Since version 1.0.
        """
        if not self.is_visible(key, context):
            return None
        value = self.get(key)
        return None if value is Null else value

    #
    # validation
    #

    def validate(self, context=None):
        """
        :py:class:`Entity` 를 검사한다.

        :py:class:`Entity` 를 구성하는 :py:class:`Property` 들 중 값이 존재하는 것들은 :py:meth:`Entity.load` 단계에서 검사되었다.
        :py:meth:`Entity.load` 가 끝났을 때 검사되지 않은 것은 ``required`` 옵션과,
        :py:meth:`Entity._validate_` 를 통해 확인되는 :py:class:`Property` 들 간의 상호 관계다.

        :py:meth:`Entity.validate` 는 이 나머지 검사를 수행한다. 문제가 있으면 :py:exc:`ValueError` 예외를 발생시킨다.

        Example

            .. literalinclude:: /../tests/ex/entity_validate.rst

        Since version 1.0.
        """

        def validate(node, context):
            with Marker(context, node) as marker:
                for name, property in node._cs_fields_.items():
                    if name == self._cs_kind_key_:
                        continue
                    value = node._get_(name)  # default 옵션이 동작한다.
                    with marker.cursor(name, value):
                        if value is None or value is Null:
                            if property._pm_opts_.required:
                                raise ValueError()
                        elif isinstance(property, Entity):
                            if not marker.isvisited(value):
                                validate(value, marker.context)
                        elif isinstance(property, Union):
                            # TODO: move abstraction to Composite
                            value.validate(marker.context)
                if not node._validate_(marker.context):
                    raise ValueError()

        validate(self, context)

    #
    # serialization
    #

    def _prepare_dump_(self, value, context):
        with Marker(context, value) as marker:
            dumps = []
            for key in value._cs_fields_:
                if self.is_visible(key, marker.context, value):
                    val = value._get_(key)
                    if val is not None:
                        with marker.cursor(key, val):
                            property = value._cs_fields_[key]
                            name = property._pm_opts_.get('name', key)
                            if val is Null:
                                val = None
                            elif key != value._cs_kind_key_:
                                if isinstance(property, Selector):
                                    val = property.select(self).dump(val, marker.context)
                                else:
                                    val = property.dump(val, marker.context)
                            dumps.append((key, property, name, val))
            return dumps

    def _dump_(self, value, context):
        encoded = type(value._cs_fields_)()
        for key, property, name, val in self._prepare_dump_(value, context):
            encoded[name] = val
        return encoded

    def _prepare_load(self, value, context):
        if self._cs_kind_key_ is None:
            klass = self.__class__
        else:
            kind_name = self._cs_fields_[self._cs_kind_key_]._pm_opts_.get('name', self._cs_kind_key_)
            klass = self._cs_kind_ns_.get(value.get(kind_name))
            if klass is None or not issubclass(klass, self.__class__):
                raise ValueError()
        instance = klass(**self._pm_opts_.__dict__)
        fields = {}
        for key in instance._cs_fields_:
            if self.is_visible(key, context, instance):
                property = instance._cs_fields_[key]
                name = property._pm_opts_.get('name', key)
                fields[name] = (key, property)
        return instance, fields

    def _load_(self, value, context):
        if self._cs_kind_key_ is None:
            if type(value) is self.__class__:
                return value
        else:
            if isinstance(value, self.__class__) and getattr(value, self._cs_kind_key_) is not None:
                return value
        if not isinstance(value, dict):
            raise ValueError()

        instance, fields = self._prepare_load(value, context)

        with Marker(context, value) as marker:
            for name, val in value.items():
                with marker.cursor(name, Null):
                    if name not in fields:
                        if marker.context.strict:
                            raise ValueError()
                        continue
                    key, property = fields[name]
                    if key == instance._cs_kind_key_:
                        continue
                with marker.cursor(name, val):
                    if isinstance(property, Selector):
                        val = property.select(self).load(val, marker.context)
                    else:
                        val = property.load(val, marker.context)
                    if val is None:
                        val = Null
                    instance[key] = val
            return instance

    #
    # patch
    #

    def __xor__(self, other):
        instance = self.copy()
        instance ^= other
        return instance

    def __ixor__(self, other):
        if not isinstance(other, Entity):
            raise TypeError()
        for k, v in other.items():
            if k in self:
                if v == self[k]:
                    delattr(self, k)
            else:
                self._em_data_[k] = Null
        return self

    def patch(self, delta, delete=True, inplace=False):
        """
        다른 :py:class:`Entity` 나 :py:class:`dict` 의 값들로 :py:class:`Entity` 를 수정한다.

        :py:meth:`Entity.update` 와 유사하지만 다음과 같은 차이가 있다.

        - ``inplace`` 가 False 면 ``self`` 를 수정하지 않고 사본을 만든다.
        - :py:data:`Null` 은 None 으로 변환된다.
        - 값이 None 일 경우 ``delete`` 가 True 면 required :py:class:`Property` 도 예외를 일으키지 않는다.

        수정된 결과를 돌려준다. ``inplace`` 가 True 면 ``self`` 를 돌려준다.

        :py:class:`Entity` 는 ``^`` 와 ``^=`` 연산자를 지원한다.
        ``x1 ^ x2`` 는 ``x2`` 를 어떻게 :py:meth:`Entity.patch` 하면 ``x1`` 이 만들어지느냐고 묻는 것이다.
        수정하거나 추가해야할 값들이 제공되고, 삭제해야할 값들이 :py:data:`Null` 로 제공된다. 공통 부분은 빠진다.

        항상 다음과 같은 관계가 성립한다::

            x2.patch(x1 ^ x2) == x1

        HTTP PATCH 메쏘드를 지원하기 위한 기능이다. 보통 클라이언트는 ``^`` 연산자를 사용하고,
        서버는 :py:meth:`Entity.patch` 를 사용한다.

        Example

            .. literalinclude:: /../tests/ex/entity_patch.rst

        Since version 1.0.
        """
        if inplace:
            instance = self
        else:
            instance = self.copy()
        for k, v in delta.items():
            if v is None or v is Null:
                if delete:
                    delattr(instance, k)
                else:
                    setattr(instance, k, None)
            else:
                setattr(instance, k, v)
        return instance

    #
    # dict interface
    #

    def __getitem__(self, key):
        key = make_key(key)
        if key not in self._cs_fields_:
            raise KeyError()
        return self._em_data_.get(key)

    def __setitem__(self, key, value):
        key = make_key(key)
        if key not in self._cs_fields_:
            raise KeyError()
        self._cs_fields_[key].__set__(self, value)

    def __delitem__(self, key):
        key = make_key(key)
        if key not in self._cs_fields_:
            raise KeyError()
        self._em_data_.pop(key, None)

    def keys(self):
        """
        :py:meth:`dict.keys` 와 동일한 기능.

        이터레이터를 제공한다.

        Since version 1.0.
        """
        # TODO: return view object in PY2 and support reversed()
        if isinstance(self._cs_fields_, OrderedDict):
            def keys():
                for key in self._cs_fields_:
                    if key in self._em_data_:
                        yield key

            return keys()
        else:
            return self._em_data_.iterkeys() if PY2 else self._em_data_.keys()

    def items(self):
        """
        :py:meth:`dict.items` 와 동일한 기능.

        이터레이터를 제공한다.

        Since version 1.0.
        """
        # TODO: return view object in PY2 and support reversed()
        if isinstance(self._cs_fields_, OrderedDict):
            def items():
                for key in self._cs_fields_:
                    val = self._em_data_.get(key)
                    if val is not None:
                        yield key, val

            return items()
        else:
            return self._em_data_.iteritems() if PY2 else self._em_data_.items()

    def values(self):
        """
        :py:meth:`dict.values` 와 동일한 기능.

        이터레이터를 제공한다.

        Since version 1.0.
        """
        # TODO: return view object in PY2 and support reversed()
        if isinstance(self._cs_fields_, OrderedDict):
            def values():
                for key in self._cs_fields_:
                    val = self._em_data_.get(key)
                    if val is not None:
                        yield val

            return values()
        else:
            return self._em_data_.itervalues() if PY2 else self._em_data_.values()

    def __iter__(self):
        return iter(self._em_data_)

    def __contains__(self, key):
        return key in self._em_data_

    def clear(self):
        """
        :py:meth:`dict.clear` 와 동일한 기능.

        Since version 1.0.
        """
        self._em_data_.clear()

    def setdefault(self, key, default=None):
        """
        :py:meth:`dict.setdefault` 와 동일한 기능.

        Since version 1.0.
        """
        if default is not None and key not in self._em_data_:
            self[key] = default
        return self._em_data_.get(key)

    def pop(self, key, *args):
        """
        :py:meth:`dict.pop` 과 동일한 기능.

        Since version 1.0.
        """
        return self._em_data_.pop(key, *args)

    def popitem(self):
        """
        :py:meth:`dict.popitem` 과 동일한 기능.

        Since version 1.0.
        """
        # ordered 인 경우도 OrderedDict 처럼 동작하지는 않는다.
        # entity 는 fully ordered 가 아니기 때문이기도 하고, set 순서를 지키는 것이 아니라 선언 순서를 지킨다는 점에서 OrderedDict 와는 다르다.
        return self._em_data_.popitem()

    def update(self, *args, **kwargs):
        """
        :py:meth:`dict.update` 와 동일한 기능.

        Since version 1.0.
        """
        if len(args) > 1:
            raise TypeError('update expected at most 1 arguments, got %d' % len(args))
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, (dict, Entity)):
                for k, v in arg.items():
                    self[k] = v
            elif hasattr(arg, 'keys'):
                for k in arg.keys():
                    self[k] = arg[k]
            else:
                for k, v in arg:
                    self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def get(self, key, *args, **kwargs):
        """
        :py:meth:`dict.get` 과 동일한 기능.

        Since version 1.0.
        """
        has_default = False
        default = None
        if args:
            if len(args) != 1 or kwargs:
                raise TypeError()
            has_default = True
            default = args[0]
        elif kwargs:
            if 'default' not in kwargs or len(kwargs) != 1:
                raise TypeError()
            has_default = True
            default = kwargs['default']
        if has_default:
            return self._em_data_.get(key, default)
        else:
            return self._get_(key)

    def __len__(self):
        return len(self._em_data_)

    def __bool__(self):
        return bool(self._em_data_)

    __nonzero__ = __bool__

    def copy(self):
        """
        :py:meth:`dict.copy` 와 동일한 기능.

        Since version 1.0.
        """
        return self._copy_()

    #
    # rich comparison
    #

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self._em_data_ == other._em_data_
        else:
            return self._em_data_ == other

    def __gt__(self, other):
        if isinstance(other, Entity):
            return self._em_data_ > other._em_data_
        else:
            return self._em_data_ > other

    def __lt__(self, other):
        if isinstance(other, Entity):
            return self._em_data_ < other._em_data_
        else:
            return self._em_data_ < other

    def __ge__(self, other):
        if isinstance(other, Entity):
            return self._em_data_ >= other._em_data_
        else:
            return self._em_data_ >= other

    def __le__(self, other):
        if isinstance(other, Entity):
            return self._em_data_ <= other._em_data_
        else:
            return self._em_data_ <= other


class Union(Composite):
    """
    여러 :py:class:`Property` 들 중 어느 한가지 값을 표현하는 :py:class:`Property`.

    :py:class:`Union` 을 정의하는 방법은 :py:class:`Entity` 와 동일하다.
    하지만 항상 정의된 :py:class:`Property` 들 중 어느 하나만 실제로 값을 갖게 되고, 나머지는 모두 None 이 된다.

    :py:meth:`Union.dump` 할 때 값이 있는 :py:class:`Property` 의 값이 그대로 출력된다.
    값을 갖는 :py:class:`Property` 가 없다면 None 이 출력된다.
    따라서 어트리뷰트의 이름은 출력에 영향을 주지 않고, :py:class:`Property` 의 ``name`` 옵션 역시 아무런 효과가 없다.

    어트리뷰트의 이름은 :py:data:`Context.errors` 에도 등장하지 않는다.
    에러 보고라는 측면에서 볼 때 :py:class:`Union` 은 구조가 없는 객체로 취급되기 때문에,
    :py:class:`Union` 을 구성하는 :py:class:`Property` 가 아무리 복잡한 구조를 가진다 하더라도 단일 에러로 취급되며 내부 구조를
    :py:data:`Context.errors` 에 노출하지 않는다.

    :py:meth:`Union.load` 할 때는 값이 어떤 :py:class:`Property` 에 해당하는지 차례대로 조사해서,
    첫번째 매치를 만나면 해당 :py:class:`Property` 의 어트리뷰트에 값을 부여한다.
    매치를 발견할 수 없으면 :py:exc:`ValueError` 예외를 발생시킨다.

    :py:class:`Property` 의 ``ordered`` 옵션은 이 순서에 영향을 준다. 앞선 :py:class:`Property` 가 먼저 검사된다.
    ``ordered`` 가 정의되지 않을 경우 순서는 임의로 결정되며, 매번 달라질 수 있다.
    때문에 값이 여러 :py:class:`Property` 들과 매치가 일어날 수 있다면 ``ordered`` 를 지정해 주는 것이 안전하다.

    :py:class:`Property` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/union.rst

    Since version 1.0.
    """
    _um_key_ = None
    _um_val_ = None

    def __repr__(self, args=None, opts=None):
        if self._um_key_ is not None:
            if args is None:
                args = []
            args.append('%s=%s' % (self._um_key_, repr(self._um_val_)))
        return super(Union, self).__repr__(args=args, opts=opts)

    #
    # property protocol
    #

    def _get_(self, name):
        return self._um_val_ if name == self._um_key_ else None

    def _set_(self, name, value):
        if value is None:
            self._um_key_ = self._um_val_ = None
        else:
            self._um_key_ = name
            self._um_val_ = value

    def _delete_(self, name):
        self._um_key_ = self._um_val_ = None

    #
    # current status
    #

    def get_key(self):
        """
        값이 있는 경우 해당 키를 돌려준다. 없으면 None.

        Since version 1.0.
        """
        return self._um_key_

    def get_value(self):
        """
        값을 돌려준다. 없으면 None.

        Since version 1.0.
        """
        return self._um_val_

    def get_item(self):
        """
        키와 값을 :py:class:`tuple` 로 돌려준다. 없으면 (None, None)

        Since version 1.0.
        """
        return self._um_key_, self._um_val_

    #
    # validation
    #

    def validate(self, context=None):
        """
        :py:class:`Union` 의 값을 검사한다.

        값이 없으면 :py:exc:`ValueError` 예외를 발생시킨다.

        Since version 1.0.
        """

        if isinstance(self._um_val_, Composite):
            self._um_val_.validate()
        elif self._um_val_ is None:
            raise ValueError()

    #
    # serialization
    #

    def _dump_(self, value, context):
        if value._um_key_ is None:
            return None
        property = self._cs_fields_[value._um_key_]
        return property.dump(value._um_val_, context)

    def _load_(self, value, context):
        if isinstance(value, self.__class__):
            return value
        instance = self.__class__(**self._pm_opts_.__dict__)
        for key, p in self._cs_fields_.items():
            if p._isvisible_(context):
                try:
                    ctx = None if context is None else context.copy()
                    val = p.load(value, ctx)
                    instance._set_(key, val)
                    return instance
                except:
                    pass
        raise ValueError()

    #
    # equality
    #

    def __eq__(self, other):
        return self._um_val_ == (other._um_val_ if isinstance(other, Union) else other)


__all__ = [
    'Kind',
    'Entity',
    'Selector',
    'Union',
]
