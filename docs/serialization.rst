Serialization
=============

.. py:currentmodule:: flowdas.meta

직렬화에 관련된 개념과 기능들을 살펴본다.

JSON Serializable
-----------------

직렬화는 Meta 의 외부와 데이터를 주고받기 위한 기능이다. 그 외부는 파일, 데이터베이스, 네트웍 패킷등 아주 다양해질 수 있다.
이 모든 가능성들에 직접적인 지원을 하려면 어떤 형태로건 플랫폼 종속적이 될 위험이 있다. 때문에 Meta 는 직렬화의 중간 지대를 설정한다.
이 중간 지대는 직접적으로 사용될 수 있을 정도로 유용하고, 그 외의 다른 형태로 변환 가능할 만큼 표현력이 있어야 한다.
Meta 가 선택한 것은 JSON Serializable 이다.

JSON Serializable 은 다음과 같은 형들로만 구성된다.

- :py:class:`str`, :py:class:`bytes` (Python 2 의 경우는 unicode 포함)
- 모든 정수형과 :py:class:`bool`
- :py:class:`float`
- 문자열 키를 사용하는 :py:class:`dict` 와 :py:class:`collections.OrderedDict`
- :py:class:`tuple` 과 :py:class:`list`

:py:meth:`Entity.dump` 는 항상 JSON Seriazable 을 출력하고, :py:meth:`Entity.load` 는 JSON Seriazable 을 입력으로 받는다.

JSON Serializable 은 표준라이브러리의 :py:mod:`json` 모듈이 다룰 수 있는 형과 일치한다.

Attribute Name
--------------

Entity 를 정의할 때 속성의 이름은 직렬화에 필요한 이름을 사용하는 것이 관례다. 하지만 그 이름이 파이썬의 키워드인 경우 문법적인 문제가 발생한다.
이와 같이 이름을 그대로 사용할 수 없는 경우 Property 의 ``name`` 옵션을 사용할 수 있다.

    >>> class Student(meta.Entity):
    ...     klass = meta.String(name='class')
    >>>
    >>> s = Student()
    >>> s.klass = 'A1'
    >>> s
    Student(dict(klass='A1'))
    >>> s.dump()
    {'class': 'A1'}

Ordering
--------

보통 직렬화에 포함되는 :py:class:`dict` 는 순서가 없다.
하지만 직렬화의 결과를 사람에게 제시하는 경우, 속성들의 순서에 일관성이 있으면 사용자 경험을 개선할 수 있는 경우도 존재한다.
:py:meth:`json.dumps` 등에는 ``sort_keys`` 와 같은 옵션이 제공되지만, 항상 이름 순으로 정렬하게 된다.
이름 순이 아니라 속성들이 정해진 순서대로 직렬화되기를 원할 경우 ``ordered`` 옵션을 사용할 수 있다.

Property 에 ``ordered`` 옵션이 사용되면 Entity 정의에 등장하는 순서를 유지하고,
:py:meth:`Entity.dump` 는 :py:class:`collections.OrderedDict` 를 출력한다.
이 순서는 ``ordered`` 옵션이 사용된 Property 들 간에만 유지되며, 그렇지 않은 Property 등 간의 순서는 유지하지 않고 항상 ``ordered`` Property
뒤에 온다.

    >>> class Resource(meta.Entity):
    ...     type = meta.String(ordered=True)
    ...     id = meta.String(ordered=True)
    >>>
    >>> class Book(Resource):
    ...     title = meta.String()
    >>>
    >>> book = Book({'type': 'book', 'id': '1234', 'title': 'Meta'})
    >>> book.dump()
    OrderedDict([('type', 'book'), ('id', '1234'), ('title', 'Meta')])
    >>> import json
    >>> json.dumps(book.dump())
    '{"type": "book", "id": "1234", "title": "Meta"}'

이 순서는 표준라이브러리의 :py:func:`json.dumps` 를 사용하는 경우 유지된다.
하지만 :py:class:`collections.OrderedDict` 를 고려하지 않는 라이브러리를 사용하는 경우, 이 순서는 무시될 수 있다.

View
----

지금까지 :py:class:`Context` 는 에러 정보를 얻는 용도로만 사용해왔다. 하지만 :py:class:`Context` 는 직렬화에 직접적으로 관여한다.

예를 들어 RESTful API 의 직렬화에 사용될 경우, 사용자의 권한에 따라 노출되는 정보가 다르다고 가정해보자.
:py:class:`Entity` 의 ``only`` 옵션이 일부 속성을 숨길 수 있는 기능을 제공하지만, 보통 구조적인 특성을 표현할 때 사용한다.
직렬화의 문맥에 따라 속성의 노출 여부를 제어할 때는 ``view`` 옵션을 사용한다.

    >>> class User(meta.Entity):
    ...     nick = meta.String()
    ...     email = meta.String(view='staff')

``nick`` 은 누구나 볼 수 있는 속성인 반면, ``email`` 는 관리자만 볼 수 있는 속성이다.

:py:class:`Context` 가 개입하지 않으면 모든 속성이 노출된다.

    >>> user = User()
    >>> user.nick = 'Meta'
    >>> user.email = 'honeypot@flowdas.com'
    >>> pprint(user.dump())
    {'email': 'honeypot@flowdas.com', 'nick': 'Meta'}

:py:class:`Context` 가 제공되더라도 ``view`` 가 설정되지 않으면 마찬가지다.

    >>> pprint(user.dump(meta.Context()))
    {'email': 'honeypot@flowdas.com', 'nick': 'Meta'}

``view`` 가 제공되면 :py:class:`Context` 의 ``view`` 와 일치하거나 ``view`` 가 없는 속성들만 노출된다.

    >>> user.dump(meta.Context(view='user'))
    {'nick': 'Meta'}
    >>> pprint(user.dump(meta.Context(view='staff')))
    {'email': 'honeypot@flowdas.com', 'nick': 'Meta'}

Codec
-----

특별한 형태의 자료 변환을 요구하는 자료형이 있을 경우는 Custom Property 를 만드는 것이 답이다.
하지만 이 변환이 직렬화 과정에서만 필요하고, 인스턴스의 속성을 다루는 과정에서는 필요하지 않은 경우도 있다.
네트웍으로 전달될 때 특정 속성을 암호화할 필요가 있거나, base64 인코딩을 사용해야할 경우 같은 것이다.

또는 API 클라이언트로 전달할 때는 ``id`` 라는 이름을 사용하고, MongoDB 로 보낼 때는 ``_id`` 로 이름을 바꾸고 싶을 수 있다.

또는 API 클라이언트의 요청에 따라 JSON 이나 MessagePack 중 하나를 선택하고 싶을 수 있다.

이처럼 직렬화의 문맥에 맞춰 그 결과를 변환하고 싶을 경우, ``codec`` 옵션을 사용할 수 있다.
Property 의 ``codec`` 옵션은 하나나 그 이상의 코덱 이름을 요구하는데, :py:class:`Context` 가 제공되지 않는 직렬화에서는 무시되지만,
일단 :py:class:`Context` 가 제공되면 직렬화의 방향에 따라 정방향 혹은 역방향으로 데이터를 변환한다.
이 때 :py:class:`Context` 를 여러개 만들어 각기 다른 코덱이 실행되도록 설정할 수 있다. 보통 :py:class:`Codec` 을 계승해서 필요한 코덱을 정의한다.

간단한 예를 들면

    >>> class Book(meta.Entity):
    ...     title = meta.String()
    >>> Book({'title': 'Meta'}, codec='json').dump()
    {'title': 'Meta'}
    >>> Book({'title': 'Meta'}, codec='json').dump(meta.Context())
    '{"title":"Meta"}'

``json`` 코덱은 JSON 문자열을 만드는 방법을 제공하는데, 더 간단한 방법도 있다.

    >>> str(Book({'title': 'Meta'}))
    '{"title":"Meta"}'
