flowdas.meta package
====================

.. py:currentmodule:: flowdas.meta

모든 예제는 다음과 같은 선언이 있다고 가정한다.::

    # coding=utf-8
    from flowdas import meta
    from pprint import pprint

Constants
---------

Null
^^^^

.. py:data:: Null
:annotation:

        두 가지 특별한 목적을 위해 사용되는 상수.

        - :py:class:`Entity` 에서 property 의 값이 null 임을 표현한다. 값이 없음을 표현하는 None 과 구분된다.
    - :py:class:`Context` 가 제공하는 에러 정보의 ``value`` 값에 사용되어, 값이 없음을 표현한다.

    Example

        .. literalinclude:: /../tests/ex/null.rst

    Since version 1.0.

Functions
---------

codec
^^^^^

.. autofunction:: codec

declare
^^^^^^^

.. py:decorator:: declare

    아직 정의되지 않은 :py:class:`Entity` 를 미리 선언하는데 사용되는 클래스 데코레이터.

    보통 순환 구조를 갖는 :py:class:`Entity` 를 정의할 때 사용된다.
    선언되는 :py:class:`Entity` 와 실제 정의가 같은 이름 공간에 위치한다면, 모듈 전역이건 함수 지역이건 상관 없다.

    이렇게 전방 선언된 :py:class:`Entity` 는 실제 정의가 제공되는한, 전방 선언 되지 않은 :py:class:`Entity` 와 사용상의 차이는 없다.
    실제 정의가 제공되지 않으면 사용할 때 :py:exc:`ReferenceError` 예외가 발생한다.

    자기 참조 :py:class:`Entity` 는 이런식으로 만들 수 있다.

        .. literalinclude:: /../tests/ex/declare.rst

    Since version 1.0.

Classes
-------

Boolean
^^^^^^^

.. autoclass:: Boolean(**kwargs)

Bytes
^^^^^

.. autoclass:: Bytes(**kwargs)

Codec
^^^^^

.. autoclass:: Codec

    .. automethod:: decode

    .. automethod:: encode

    .. py:decorator:: register(name)

        코덱을 등록하는데 사용하는 데코레이터.

        ``name`` 은 코덱의 이름이다.

        Since version 1.0.

Complex
^^^^^^^

.. autoclass:: Complex(**kwargs)

Context
^^^^^^^

.. autoclass:: Context(strict=False, view=None)
:members: errors, reset, set_codec

Date
^^^^

.. autoclass:: Date(**kwargs)

DateTime
^^^^^^^^

.. autoclass:: DateTime(**kwargs)
:members:

DateTimeFormat
^^^^^^^^^^^^^^

.. autoclass:: DateTimeFormat
:members: name

        .. automethod:: format

    .. automethod:: parse

    .. py:decorator:: register(name, *args, **kwargs)

        날짜시간 형식을 등록하는데 사용하는 데코레이터.

        ``name`` 은 형식의 이름이고, 그 뒤로 ``__init__`` 로 전달할 인자들을 제공할 수 있다.

        Since version 1.0.

Decimal
^^^^^^^

.. autoclass:: Decimal(**kwargs)

Duration
^^^^^^^^

.. autoclass:: Duration(**kwargs)

Entity
^^^^^^

.. autoclass:: Entity([other,] **kwargs)

    .. automethod:: _validate_

    .. automethod:: clear

    .. automethod:: copy

    .. automethod:: define_subclass

    .. automethod:: dump(context=None)

    .. automethod:: get(key[, default])

    .. automethod:: get_class_options

    .. automethod:: get_if_visible(key, context)

    .. automethod:: items

    .. automethod:: keys

    .. py:method:: load(value, context=None)

        JSON Serializable 을 :py:class:`Entity` 인스턴스로 변환한다.

        이 메쏘드는 클래스 메쏘드가 아니다. 메쏘드를 호출하기 위해 인스턴스를 하나 만들어야 하고, ``value`` 를 해석하는데 인스턴스의 옵션이 사용된다.
        인스턴스가 수정되지는 않고 새 인스턴스를 돌려준다.

        보통 호출한 인스턴스와 같은 클래스의 인스턴스를 돌려주지만, 다형성을 제공하는 클래스의 경우는 자식 클래스의 인스턴스를 돌려줄 수 있다.

        ``context`` 로 :py:class:`Context` 인스턴스를 제공하면 여러 변화를 줄 수 있다.

        ``value`` 가 :py:class:`Entity` 의 정의와 맞지 않거나, 순환 참조를 포함하면 예외를 발생시킨다.
        예외가 발생하지 않았다고 해서 검사를 모두 통과한 것은 아니다.
        :py:class:`Entity.load` 는 검사의 첫번째 단계일 뿐이며, 생략된 값에 대해 ``required`` 옵션을 조사하지 않는다.
        두번째 단계인 :py:class:`Entity.validate` 를 실행해야 검사가 완료된다.

        예외가 발생할 경우 에러의 세부 정보는 ``context`` 로 제공한다.

        Example:

            .. literalinclude:: /../tests/ex/entity_load.rst

        Since version 1.0.

    .. automethod:: patch

    .. automethod:: pop(key[, default])

    .. automethod:: popitem

    .. automethod:: setdefault(key[, default])

    .. automethod:: update([other,] **kwargs)

    .. automethod:: validate

    .. automethod:: values

Entity.MetaOptions
^^^^^^^^^^^^^^^^^^

.. py:class:: Entity.MetaOptions

    :py:class:`Entity` 의 클래스 옵션을 정의하는 내부 클래스.

    이 클래스를 재정의하면 옵션을 추가하거나, 기본값을 바꿀 수 있다. 추가하거나 바꿀 옵션을 클래스 어트리뷰트로 제공하면 된다.

        .. literalinclude:: /../tests/ex/entity_metaoptions.rst

    Since version 1.0.

Float
^^^^^

.. autoclass:: Float(**kwargs)

Integer
^^^^^^^

.. autoclass:: Integer(**kwargs)

IpAddress
^^^^^^^^^

.. autoclass:: IpAddress(**kwargs)

Ipv4Address
^^^^^^^^^^^

.. autoclass:: Ipv4Address(**kwargs)

Ipv6Address
^^^^^^^^^^^

.. autoclass:: Ipv6Address(**kwargs)

JsonArray
^^^^^^^^^

.. autoclass:: JsonArray(**kwargs)

JsonObject
^^^^^^^^^^

.. autoclass:: JsonObject(**kwargs)

Kind
^^^^

.. autoclass:: Kind([kind,]**kwargs)

Number
^^^^^^

.. autoclass:: Number(**kwargs)

Primitive
^^^^^^^^^

.. autoclass:: Primitive(**kwargs)
:members:
        :undoc-members:

Property
^^^^^^^^

.. autoclass:: Property(**kwargs)

    .. automethod:: _dump_

    .. automethod:: _load_

    .. automethod:: apply_options(**kwargs)

    .. automethod:: get_options

    .. automethod:: is_ordered

Property.Options
^^^^^^^^^^^^^^^^

.. py:class:: Property.Options

    :py:class:`Property` 의 옵션을 정의하는 내부 클래스.

    이 클래스를 재정의하면 옵션을 추가하거나, 기본값을 바꿀 수 있다. 추가하거나 바꿀 옵션을 클래스 어트리뷰트로 제공하면 된다.
    다만 ``ordered`` 옵션은 예외로, 기본 값을 바꿀 수 없다.

        .. literalinclude:: /../tests/ex/property_options.rst

    Since version 1.0.

Selector
^^^^^^^^

.. autoclass:: Selector

String
^^^^^^

.. autoclass:: String(**kwargs)

Time
^^^^

.. autoclass:: Time(**kwargs)

Tuple
^^^^^

.. autoclass:: Tuple

Unicode
^^^^^^^

.. autoclass:: Unicode(**kwargs)

Union
^^^^^

.. autoclass:: Union(**kwargs)

    .. py:method:: dump(value, context=None)

        값을 JSON Serializable 로 변환한다.

        :py:class:`Entity.dump` 와 동일한 방식으로 동작한다. 다만 :py:class:`dict` 를 출력하는 대신, 값을 직접 출력한다.

        값이 없다면 None 을 돌려준다.

        Since version 1.0.

    .. automethod:: get_item

    .. automethod:: get_key

    .. automethod:: get_value

    .. py:method:: load(value, context=None)

        JSON Serializable 을 :py:class:`Union` 인스턴스로 변환한다.

        :py:class:`Entity.load` 와 동일한 방식으로 동작한다. 다만 :py:class:`dict` 를 받아들이는 대신, ``value`` 를 값으로 해석한다.

        ``value`` 를 정의한 :py:class:`Property` 들 중 어느것으로도 해석할 수 없다면 :py:exc:`ValueError` 예외를 발생시킨다.

        Since version 1.0.

    .. automethod:: validate

Uuid
^^^^

.. autoclass:: Uuid(**kwargs)

