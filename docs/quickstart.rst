Quickstart
==========

.. py:currentmodule:: flowdas.meta


자료 구조를 정의하는 기본 문법을 소개하고, 직렬화와 검사를 다룬다.

Entity & Property
-----------------

Meta 가 제공하는 가장 기본적인 도구는 Entity 인데, 자료 구조를 표현한다. Entity 를 정의는 방법은 클래스를 정의하는 방법과 같다.
즉 :py:class:`Entity` 를 계승하고, 클래스 어트리뷰트로 자료 구조의 속성들을 정의한다.

    >>> from flowdas import meta
    >>>
    >>> class Book(meta.Entity):
    ...    title = meta.String()
    ...    published = meta.Date()

이제 모든 ``Book`` 의 인스턴스는 ``title`` 과 ``published`` 를 속성으로 갖게 된다.
인스턴스를 처음 만들면 모든 속성은 None 값을 갖는다.

    >>> book = Book()
    >>> book.title is None
    True
    >>> book.published is None
    True

이제 속성에 값을 줄 수 있다.

    >>> book.title = 'Meta'
    >>> book.title
    'Meta'
    >>> book.published = '2016-03-15'
    >>> book.published
    datetime.date(2016, 3, 15)

속성에 형을 부여하는 것을 Property 라고 한다.
가령 ``title`` 은 문자열(:py:class:`String`), ``published`` 는 날짜(:py:class:`Date`)로 제한된다.
잘못된 값은 받아들이지 않는다.

    >>> book.title = 3
    Traceback (most recent call last):
        ...
    ValueError
    >>> book.published = 'abc'
    Traceback (most recent call last):
        ...
    ValueError

``published`` 는 문자열(``'2016-03-15'``)을 제공했는데, 실제 속성의 값은 :py:class:`datetime.date` 의 인스턴스다.
물론 ``published`` 는 :py:class:`datetime.date` 의 인스턴스도 받아들인다.

    >>> import datetime
    >>> book.published = datetime.date(2016, 3, 15)
    >>> book.published
    datetime.date(2016, 3, 15)

이처럼 Property 들은 속성의 값으로 제공하는 형이 정해져 있는데, 대부분 파이썬의 내장형이거나 표준 라이브러리가 제공하는 형이다.
:py:class:`Date` 에서 볼 수 있는 것처럼 이 속성에 대입할 수 있는 값의 범위는 더 넓다.

속성들의 값을 읽거나 쓰는데, :py:class:`dict` 와 같은 문법을 사용해도 된다.

    >>> book['title'] = 'Meta'
    >>> book['title']
    'Meta'
    >>> book['published'] = '2016-03-15'
    >>> book['published']
    datetime.date(2016, 3, 15)

이외에도 Entity 는 최대한 :py:class:`dict` 와 유사한 방식으로 사용될 수 있도록 지원한다.

    >>> book = Book({'title': 'Meta', 'published': '2016-03-15'})
    >>> book.update(title='Meta', published='2016-03-15')
    >>> sorted(book.items())
    [('published', datetime.date(2016, 3, 15)), ('title', 'Meta')]

속성을 지울수도 있다. 일 단 지워지면 다시 None 값이 제공된다.

    >>> del book.published
    >>> del book['published']
    >>> repr(book.published)
    'None'

None 값이 읽힌다 하더라도, 값이 None 인 속성은 없는 것처럼 취급된다.

    >>> list(book.items())
    [('title', 'Meta')]

때문에 None 을 대입하는 것 역시 지우는 것과 같다.

    >>> book.title = None
    >>> list(book.items())
    []

Dumping
-------

:py:meth:`Entity.dump` 메쏘드를 사용하면 Entity 를 :py:class:`dict` 로 변환할 수 있는데, 이를 직렬화(serialization)라고 부른다.

    >>> from pprint import pprint
    >>>
    >>> book.update(title='Meta', published='2016-03-15')
    >>> pprint(book.dump())
    {'published': '2016-03-15', 'title': 'Meta'}

이 :py:class:`dict` 는 :py:meth:`json.dumps` 에 바로 넘겨줄 수 있는 형태의 값들로만 구성된다.
``published`` 는 :py:class:`datetime.date` 이 아닌 문자열로 변환되고 있다.

    >>> import json
    >>>
    >>> json.dumps(book.dump(), sort_keys=True)
    '{"published": "2016-03-15", "title": "Meta"}'

앞서 살펴보았듯이 속성에 None 값을 주는 것은 지우는 것과 같고, 지워진 속성은 없는 것처럼 취급되기 때문에 :py:meth:`Entity.dump` 에서도 제외된다.

    >>> book.published = None
    >>> book.dump()
    {'title': 'Meta'}

None 값을 출력하고 싶다면 :py:data:`Null` 을 사용하면 된다.

    >>> book.published = meta.Null
    >>> pprint(book.dump())
    {'published': None, 'title': 'Meta'}

Loading
-------

:py:meth:`Entity.load` 는 :py:meth:`Entity.dump` 의 역함수다.

    >>> book = Book().load({'title': 'Meta', 'published': '2016-03-15'})
    >>> book == Book({'title': 'Meta', 'published': '2016-03-15'})
    True

``Book.load`` 라고 표현하지 않고, ``Book().load`` 라고 표현하는 것에 주목해야 한다.
:py:meth:`Entity.load` 는 ``@classmethod`` 가 아니다. :py:meth:`Entity.load` 의 동작에 영향을 줄 수 있는
옵션이 ``Book()`` 에 제공될 수 있기 때문인데, 당장은 :py:meth:`Entity.load` 를 호출할 때 항상 인스턴스가 필요하다는 것만 기억하면 된다.

:py:meth:`Entity.dump` 와는 반대로, 데이터에 None 이 포함되어 있는 경우 :py:data:`Null` 로 변환된다.

    >>> book = Book().load({'title': 'Meta', 'published': None})
    >>> book.published
    Null

속성에 값을 직접 대입할 때와 마찬가지로, 값에 문제가 있으면 :py:meth:`Entity.load` 도 예외를 일으킨다.

    >>> book = Book().load({'title': 'Meta', 'published': 'abc'})
    Traceback (most recent call last):
        ...
    ValueError

Validation
----------

잘못된 값을 대입하거나 :py:meth:`Entity.load` 하는 경우 예외가 발생하는데, 암묵적으로 검사(validation) 이 수행되고 있기 때문이다.
그런데 검사는 이 것으로만 한정되지 않는다. 가령 자료 구조를 정의할 때 반드시 필요한 속성이라는 조건을 줄 수 있다.

    >>> class Book(meta.Entity):
    ...    title = meta.String(required=True)
    ...    published = meta.Date()

``required`` 옵션을 사용해서 ``title`` 속성이 반드시 필요하다고 선언했다. 하지만 이 값을 제공하지 않고도 인스턴스를 만들 수 있다.

    >>> book = Book()
    >>> repr(book.title)
    'None'

다만 이 값에 None 이나 :py:data:`Null` 을 대입하는 것은 더이상 허락되지 않는다.

    >>> book.title = None
    Traceback (most recent call last):
        ...
    ValueError
    >>> book.title = meta.Null
    Traceback (most recent call last):
        ...
    ValueError

하지만 값을 대입하지 않는 경우 예외는 일어나지 않고, :py:meth:`Entity.load` 하는 데이터에 값이 등장하지 않는 경우도 예외는 발생하지 않는다.
더군다나 ``del`` 을 사용해서 속성을 지우는 것은 여전히 허락된다.

    >>> del book.title
    >>> del book['title']

:py:meth:`Entity.validate` 메쏘드로 현재 인스턴스가 이 조건을 만족하는지 검사할 수 있다.

    >>> book.validate()
    Traceback (most recent call last):
        ...
    ValueError

때문에 검사가 필요한 경우 :py:meth:`Entity.load` 뒤에 :py:meth:`Entity.validate` 를 호출하는 것이 일반적인 사용법이다.

    >>> book = Book().load({'published': None})
    >>> book.validate()
    Traceback (most recent call last):
        ...
    ValueError

Error
-----

:py:meth:`Entity.load` 나 :py:meth:`Entity.validate` 에서 예외가 발생하는 경우, 구체적으로 어디에 문제가 있는지 확인해야 할 경우가 있다.
이 때 :py:class:`Context` 를 전달할 수 있는데, :py:attr:`Context.errors` 로 에러 정보가 제공된다.

    >>> ctx = meta.Context()
    >>> book = Book().load({'title':None}, ctx)
    Traceback (most recent call last):
        ...
    ValueError
    >>> ctx.errors[0].location
    '/title'
    >>> repr(ctx.errors[0].value)
    'None'

``'/title'`` 이라는 위치에서 예외가 발생했으며, 문제를 일으킨 값은 None 이라는 의미다.
위치를 나타내는 문자열은 `JSON Pointer <https://tools.ietf.org/html/rfc6901>`_ 규격을 사용하고 있다.

:py:meth:`Entity.validate` 도 마찬가지다.

    >>> ctx = meta.Context()
    >>> book = Book()
    >>> book.validate(ctx)
    Traceback (most recent call last):
        ...
    ValueError
    >>> ctx.errors[0].location
    '/title'
    >>> repr(ctx.errors[0].value)
    'None'

똑 같아 보이지만 한가지 차이가 있다.
:py:meth:`Entity.load` 의 경우 ``location`` 과 ``value`` 는 입력으로 주어진 데이터(``{'title':None}``)를 가리킨다.
반면에 :py:meth:`Entity.validate` 는 검사의 대상이 되는 Entity 인스턴스(``book``) 을 가리킨다.
지금은 두 경우 모두 같은 값을 주지만, 늘 그런 것은 아니다.

보통는 첫번째 에러가 발생할 때 예외를 일으키고, :py:attr:`Context.errors` 에는 하나의 에러만 기록된다.
하지만 ``max_errors`` 옵션을 사용하면 여러개의 문제를 한번에 검출할 수 있다.

    >>> ctx = meta.Context(max_errors=10)
    >>> book = Book().load({'title':None, 'published':'abc'}, ctx)
    Traceback (most recent call last):
        ...
    ValueError
    >>> len(ctx.errors)
    2
    >>> sorted(map(lambda e: (e.location, e.value), ctx.errors))
    [('/published', 'abc'), ('/title', None)]

