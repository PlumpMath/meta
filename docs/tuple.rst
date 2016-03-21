Tuple
=====

.. py:currentmodule:: flowdas.meta

배열을 표현하는 방법을 소개한다.

Tuple
-----

:py:class:`JsonArray` 가 배열을 표현하는 방법을 제공하기는 하지만, 배열을 이루는 항목들의 형을 제한하지는 못한다.

:py:class:`Tuple` Property 는 배열의 길이와 항목들의 형을 제한하는 방법을 제공한다.

:py:class:`Tuple` 은 생성자로 배열을 이루는 Property 의 목록을 받아들인다.

    >>> class Point3D(meta.Entity):
    ...     xyz = meta.Tuple(meta.Float(), meta.Float(), meta.Float())
    >>> p = Point3D()
    >>> p.xyz = [1, 2, 3]
    >>> p.xyz
    (1.0, 2.0, 3.0)

:py:class:`tuple` 과 :py:class:`list` 모두 입력으로 받아들이지만 값은 항상 :py:class:`tuple` 로 표현되고,
:py:meth:`Entity.dump` 할 때는 :py:class:`list` 로 변환된다.

    >>> p.dump()
    {'xyz': [1.0, 2.0, 3.0]}

길이가 일치하지 않거나, 항목의 형이 다르면 받아들이지 않는다.

    >>> p.xyz = [1, 2, 3, 4]
    Traceback (most recent call last):
        ...
    ValueError: length mismatch
    >>> p.xyz = [1, 2, '3']
    Traceback (most recent call last):
        ...
    ValueError

하지만 None 이 포함될 수는 있다.

    >>> p.xyz = [1, 2, None]
    >>> p.xyz
    (1.0, 2.0, None)

None 을 허락하지 않으려면 항목을 이루는 Property 들에 ``required`` 옵션을 제공해야 한다.

    >>> class Point3D(meta.Entity):
    ...     xyz = meta.Tuple(meta.Float(required=True), meta.Float(required=True), meta.Float(required=True))
    >>> p = Point3D()
    >>> p.xyz = [1, 2, None]
    Traceback (most recent call last):
        ...
    ValueError

Repeating
---------

``repeat`` 옵션을 사용하면 앞의 예를 좀 더 간략히 표현할 수 있다.


    >>> class Point3D(meta.Entity):
    ...     xyz = meta.Tuple(meta.Float(required=True), repeat=3)
    >>> p = Point3D()
    >>> p.xyz = [1, 2, 3]
    >>> p.xyz
    (1.0, 2.0, 3.0)

``repeat`` 가 주어지면 제공한 Property 목록 전체를 반복한다.

    >>> class X(meta.Entity):
    ...     pairs = meta.Tuple(meta.String(), meta.Integer(), repeat=2)
    >>> x = X()
    >>> x.pairs = ['1', 1, '2', 2]
    >>> x.pairs
    ('1', 1, '2', 2)

:py:class:`slice` 로 범위를 지정할 수도 있다.

    >>> class Polygon3D(meta.Entity):
    ...     points = meta.Tuple(meta.Float(required=True), repeat=slice(3,None,3))
    >>> p = Polygon3D()
    >>> p.points = [1, 2, 3]
    >>> p.points = [1, 2, 3, 4, 5, 6]
    >>> p.points
    (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
    >>> p.points = []
    Traceback (most recent call last):
        ...
    ValueError: length mismatch
    >>> p.points = [1, 2, 3, 4]
    Traceback (most recent call last):
        ...
    ValueError: length mismatch

최소 길이는 3 이고, 최대 길이는 제한이 없으나 항상 3의 배수가 되어야 한다는 뜻이다.

Tuplization
-----------

앞의 예처럼 한가지 형으로만 구성된 균등 배열(homogeneous array)은 자주 사용된다.
Property 클래스에 튜플화 연산자를 사용하면 좀 더 간략하게 표현할 수 있다.

    >>> class Point3D(meta.Entity):
    ...     xyz = meta.Float[3](required=True)
    >>> p = Point3D()
    >>> p.xyz = [1, 2, 3]
    >>> p.xyz
    (1.0, 2.0, 3.0)
    >>> class Polygon3D(meta.Entity):
    ...     points = meta.Float[3::3](required=True)
    >>> p = Polygon3D()
    >>> p.points = [1, 2, 3]
    >>> p.points = [1, 2, 3, 4, 5, 6]
    >>> p.points
    (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)

Entity Array
------------

Entity 역시 튜플화가 된다.

    >>> class Book(meta.Entity):
    ...     title = meta.String()
    >>> books = Book[:]().load([{'title': 'meta'}, {'title': 'O'}])
    >>> books
    (Book(dict(title='meta')), Book(dict(title='O')))
