Inheritance
===========

.. py:currentmodule:: flowdas.meta

사용자가 정의한 Entity 를 계승하여 공통 자료 구조를 표현하는 방법을 살펴본다.

Subclassing
-----------

Entity 를 정의할 때 이미 정의된 Entity 를 계승할 수 있다. 그 결과는 파이썬에서 일반 클래스들을 계승할 때와 유사하다.
즉 이미 정의된 속성들은 그대로 물려받으며 같은 이름의 속성을 정의하면 기존의 속성은 가려지게된다.

    >>> class Resource(meta.Entity):
    ...     type = meta.String()
    ...     id = meta.String()
    >>>
    >>> class Book(Resource):
    ...     title = meta.String()
    >>>
    >>> book = Book({'type': 'book', 'id': '1234', 'title': 'Meta'})
    >>> book
    Book(dict(id='1234', title='Meta', type='book'))

한 Entity 를 계승해서 다른 Entity 를 만들 때 두 Entity 는 독립된 형이다.

    >>> class X(meta.Entity):
    ...     resource = Resource()
    ...     book = Book()
    >>>
    >>> x = X()
    >>> x.resource = Resource()
    >>> x.book = Book({'type': 'book', 'id': '1234', 'title': 'Meta'})
    >>> x.resource = x.book
    Traceback (most recent call last):
        ...
    ValueError
    >>> x.book = x.resource
    Traceback (most recent call last):
        ...
    ValueError

흔히 OOP(Object Oriented Programming) 에서 지원되는 IS-A 관계는 성립하지 않는다. ``Book`` 인스턴스를 ``Resource`` 속성에 대입하려면 직렬화한 값을 사용하면 된다.
물론 이 때 ``Book`` 이 새로 정의한 속성은 보존되지 않는다.

    >>> x.resource = x.book.dump()
    >>> x.resource
    Resource(dict(id='1234', type='book'))


Polymorphic Entity
------------------

OOP 의 IS-A 관계를 지원하는 Entity 를 만들 수 있다. 이를 위한 특별한 Property :py:class:`Kind` 를 속성에 포함시키면 된다.

    >>> class Resource(meta.Entity):
    ...     type = meta.Kind()
    ...     id = meta.String()
    >>>
    >>> class Book(Resource):
    ...     type = 'book'
    ...     title = meta.String()
    >>>
    >>> book = Book({'id': '1234', 'title': 'Meta'})
    >>> book
    Book(dict(id='1234', title='Meta'))
    >>> book.type
    'book'

``type`` 이라는 이름으로 :py:class:`Kind` Property 를 정의했다.
이제 ``Resource`` 와 이를 계승하는 모든 Entity 들은 다형형(polymorphism)을 갖게 된다.
계승하는 Entity 들은 ``type`` 속성을 다시 지정해 주어야 하는데,
:py:class:`Kind` 나 기타 다른 Property 들을 사용하는 대신 그 클래스를 특정할 수 있는 값을 제공한다. 문자열, 숫자, 튜플등을 사용할 수 있다.
이제 IS-A 관계가 성립한다.

    >>> class X(meta.Entity):
    ...     resource = Resource()
    >>>
    >>> x = X()
    >>> x.resource = book
    >>> x.resource
    Book(dict(id='1234', title='Meta'))

:py:class:`Kind` 로 지정한 속성은 직렬화에 포함된다.

    >>> pprint(x.dump())
    {'resource': {'id': '1234', 'title': 'Meta', 'type': 'book'}}

IS-A 관계는 :py:meth:`Entity.load` 에서도 보존된다.

    >>> x = X().load({'resource': {'id': '1234', 'title': 'Meta', 'type': 'book'}})
    >>> x.resource
    Book(dict(id='1234', title='Meta'))

하지만 이제 ``Resource`` 는 대입할 수 없게 된다.

    >>> x.resource = Resource()
    Traceback (most recent call last):
        ...
    ValueError

이는 ``Resource`` 가 추상(abstract) 클래스로 취급되기 때문이다. ``type`` 의 구체적인 값을 제공하지 않은 클래스들은 모두 추상 클래스로 취급된다.

:py:class:`Kind` 로 지정된 속성은 직렬화에 포함되고, 값을 읽을 수도 있지만, 그외에는 없는 것처럼 취급되고 있음에 주의해야 한다.
인스턴스의 속성이 아니라 클래스의 속성으로 취급되며, 값을 바꿀 수도 없다.

    >>> x.resource.type = 'book'
    Traceback (most recent call last):
        ...
    AttributeError: can’t set attribute

