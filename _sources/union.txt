Union
=====

.. py:currentmodule:: flowdas.meta

여러 형태를 가질 수 있는 자료 구조를 정의하는 법을 살펴본다.

Union
-----

API 의 응답에 URL 이 포함되는데, 문자열로 표현되기도 하고, 메타정보가 있는 경우 JSON Object 로 표현된다고 가정해보자.
먼저 메타정보가 있는 경우는 이렇게 표현할 수 있다.

    >>> class LinkObject(meta.Entity):
    ...    href = meta.String(required=True)
    ...    meta = meta.JsonObject()

문자열인 경우는 ``meta.String()`` 으로 표현할 수 있다.

이 두가지를 :py:class:`Union` 을 사용해서 조합할 수 있다.

    >>> class Link(meta.Union):
    ...     href = meta.String()
    ...     link = LinkObject()
    >>>
    >>> class Resource(meta.Entity):
    ...     self = Link()

:py:class:`Union` 은 :py:class:`Entity` 와 동일한 문법 구조를 갖는다. 다만 각 속성들은 동시에 값이 존재할 수 없고, 최대 하나만 값을 가질 수 있다.
이제 다음과 같이 사용할 수 있다.

    >>> r = Resource()
    >>>
    >>> r.self = 'https://github.com/flowdas/meta'
    >>> r.self
    Link(href='https://github.com/flowdas/meta')
    >>> r.self.href
    'https://github.com/flowdas/meta'
    >>> repr(r.self.link)
    'None'
    >>> r.dump()
    {'self': 'https://github.com/flowdas/meta'}
    >>>
    >>> r.self = {'href': 'https://github.com/flowdas/meta', 'meta': {'type': 'git'}}
    >>> r.self
    Link(link=LinkObject(dict(href='https://github.com/flowdas/meta', meta={'type': 'git'})))
    >>> repr(r.self.href)
    'None'
    >>> r.self.link
    LinkObject(dict(href='https://github.com/flowdas/meta', meta={'type': 'git'}))
    >>> pprint(r.dump())
    {'self': {'href': 'https://github.com/flowdas/meta', 'meta': {'type': 'git'}}}

``r.self`` 에 대입하면 정의한 두 Property 중에서 올바른 형을 찾는다. 물론 찾을 수 없다면 예외를 일으킨다.

    >>> r.self = 1
    Traceback (most recent call last):
        ...
    ValueError

어트리뷰트 이름을 지정하면 원하는 Property 를 선택할 수 있다.

    >>> r.self.link = 'https://github.com/flowdas/meta'
    Traceback (most recent call last):
        ...
    ValueError

만약 제공한 값이 여러 Property 로 해석될 수 있다면, Property 에 ``ordered`` 옵션을 제공해서 순서를 정해줄 필요가 있다.

Selector
--------

때로는 어떤 조건에 따라 받아들일 수 있는 형이 결정되는 경우가 있다. 예를들어 RESTful API 의 GET 요청은 그 대상이 컬렉션인 경우 JSON Array를 주고,
그렇지 않은 경우 JSON Object 를 줄 수 있다.

먼저 조건을 결정할 변수를 제공하는 방법이 필요한데, Entity 에 옵션을 추가하는 방법을 사용할 수 있다. 내부 클래스 ``Options`` 를 정의하면 된다.

    >>> class Response(meta.Entity):
    ...     class Options(meta.Entity.Options):
    ...         many = False

이제 ``Response`` 라는 Entity 에는 ``many`` 라는 옵션이 추가되고 기본 값은 False 가 된다.
그외의 다른 옵션들은 ``meta.Entity.Options`` 로부터 물려받는다.

이제 :py:class:`Selector` 를 사용하면 이 옵션에 따라 형이 바뀌는 속성을 정의할 수 있다. 다른 Property 들과는 달리 데코레이터 문법을 사용한다.

    >>> class Resource(meta.Entity):
    ...     type = meta.String()
    ...     id = meta.String()
    >>>
    >>> class Response(meta.Entity):
    ...     class Options(meta.Entity.Options):
    ...         many = False
    ...
    ...     @meta.Selector(Resource(), Resource[:]())
    ...     def data(self):
    ...         return self.get_options().many

:py:class:`Tuple` 과 유사하게 인자로 Property 목록을 제공한다. 데코레이터로 감싼 메쏘드는 이 중 선택해야할 Property 의 인덱스를 돌려준다.
``many`` 가 False 면 ``Resource()`` 를 선택하고, True 면 그 배열을 선택하도록 구성했다.

    >>> r = Response()
    >>> r.data = {}
    >>> r.data = [{}]
    Traceback (most recent call last):
        ...
    ValueError
    >>> r.dump()
    {'data': {}}
    >>>
    >>> r = Response(many=True)
    >>> r.data = {}
    Traceback (most recent call last):
        ...
    ValueError
    >>> r.data = [{}]
    >>> r.dump()
    {'data': [{}]}


