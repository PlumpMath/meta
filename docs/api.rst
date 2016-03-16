flowdas.meta package
====================

.. py:currentmodule:: flowdas.meta

모든 예제는 다음과 같은 선언이 있다고 가정한다.::

    # coding=utf-8
    from flowdas import meta
    from pprint import pprint

Constants
---------

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

.. autofunction:: codec

.. py:decorator:: declare

    아직 정의되지 않은 :py:class:`Entity` 를 미리 선언하는데 사용되는 클래스 데코레이터.

    보통 순환 구조를 갖는 :py:class:`Entity` 를 정의할 때 사용된다. 선언되는 :py:class:`Entity` 는 모듈 전역이어야 하며, 동일한 모듈에서 실제 정의가 이루어져야 한다.
    이렇게 전방 선언된 :py:class:`Entity` 는 실제 정의가 제공되는한, 전방 선언 되지 않은 :py:class:`Entity` 와 사용상의 차이는 없다.
    실제 정의가 제공되지 않으면 사용할 때 :py:exc:`ReferenceError` 예외가 발생한다.

    자기 참조 :py:class:`Entity` 는 이런식으로 만들 수 있다.

        .. literalinclude:: /../tests/ex/declare.py

    Since version 1.0.

Classes
-------

.. autoclass:: Boolean(**kwargs)

.. autoclass:: Bytes(**kwargs)

.. autoclass:: Codec

    .. automethod:: decode

    .. automethod:: encode

    .. py:decorator:: register(name)

        코덱을 등록하는데 사용하는 데코레이터.

        ``name`` 은 코덱의 이름이다.

        Since version 1.0.


.. autoclass:: Complex(**kwargs)

.. autoclass:: Context(strict=False, view=None)
    :members: errors, reset, set_codec

.. autoclass:: Date(**kwargs)

.. autoclass:: DateTime(**kwargs)
    :members:

.. autoclass:: DateTimeFormat
    :members: name

    .. automethod:: format

    .. automethod:: parse

    .. py:decorator:: register(name, *args, **kwargs)

        날짜시간 형식을 등록하는데 사용하는 데코레이터.

        ``name`` 은 형식의 이름이고, 그 뒤로 ``__init__`` 로 전달할 인자들을 제공할 수 있다.

        Since version 1.0.

.. autoclass:: Decimal(**kwargs)

.. autoclass:: Duration(**kwargs)

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

.. py:class:: Entity.MetaOptions

    :py:class:`Entity` 의 클래스 옵션을 정의하는 내부 클래스.

    이 클래스를 재정의하면 옵션을 추가하거나, 기본값을 바꿀 수 있다. 추가하거나 바꿀 옵션을 클래스 어트리뷰트로 제공하면 된다.

        .. literalinclude:: /../tests/ex/entity_metaoptions.rst

    Since version 1.0.

.. autoclass:: Float(**kwargs)

.. autoclass:: Integer(**kwargs)

.. autoclass:: IpAddress(**kwargs)

.. autoclass:: Ipv4Address(**kwargs)

.. autoclass:: Ipv6Address(**kwargs)

.. autoclass:: JsonArray(**kwargs)

.. autoclass:: JsonObject(**kwargs)

.. autoclass:: Kind([kind,]**kwargs)

.. autoclass:: Number(**kwargs)

.. autoclass:: Primitive(**kwargs)
    :members:
    :undoc-members:

.. autoclass:: Property(**kwargs)

    .. automethod:: _dump_

    .. automethod:: _load_

    .. automethod:: apply_options(**kwargs)

    .. automethod:: get_options

    .. automethod:: is_ordered

.. py:class:: Property.Options

    :py:class:`Property` 의 옵션을 정의하는 내부 클래스.

    이 클래스를 재정의하면 옵션을 추가하거나, 기본값을 바꿀 수 있다. 추가하거나 바꿀 옵션을 클래스 어트리뷰트로 제공하면 된다.
    다만 ``ordered`` 옵션은 예외로, 기본 값을 바꿀 수 없다.

        .. literalinclude:: /../tests/ex/property_options.rst

    Since version 1.0.

.. autoclass:: String(**kwargs)

.. autoclass:: Time(**kwargs)

.. autoclass:: Tuple

.. autoclass:: Unicode(**kwargs)

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

.. autoclass:: Uuid(**kwargs)

