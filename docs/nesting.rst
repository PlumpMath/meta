Nesting
=======

.. py:currentmodule:: flowdas.meta

Entity 를 다른 Entity 의 정의에 사용하는 방법을 살펴본다.

Embedding
---------

사용자가 새로 정의한 Entity 역시 Property 다. 때문에 특별한 준비 없이 Entity 정의에 사용할 수 있다.

    >>> class Author(meta.Entity):
    ...    name = meta.String()
    >>>
    >>> class Book(meta.Entity):
    ...    title = meta.String()
    ...    published = meta.Date()
    ...    author = Author()
    >>>
    >>> book = Book()
    >>> book.author = Author({'name': 'O'})
    >>> book
    Book(dict(author=Author(dict(name='O'))))

직렬화 하면 Entity 에 포함된 Entity 들 역시 직열화된다.

    >>> book.dump()
    {'author': {'name': 'O'}}

반대도 역시 성립한다.

    >>> book = Book().load({'author': {'name': 'O'}})
    >>> book
    Book(dict(author=Author(dict(name='O'))))

Entity 에 내장된 Entity 는 데이터를 직접 대입해도 된다.

    >>> book.author = {'name': 'O'}
    >>> book.author
    Author(dict(name='O'))

Circular Reference
------------------

자기 자신을 Property 로 갖는 자료 구조를 생각해보자.

    >>> class Tree(meta.Entity):
    ...     children = Tree[:]() # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    NameError: ... 'Tree' is not defined

클래스 정의가 완료되기 전에는 그 이름이 정의되지 않은 상태기 때문에 :py:exc:`NameError` 예외가 발생한다.

이 문제를 해결하기 위해 ``@declare`` 데코레이터를 제공한다.

    >>> @meta.declare
    ... class Tree: pass
    >>>
    >>> class Tree(meta.Entity):
    ...     children = Tree[:]()

클래스를 ``@declare`` 로 선언해주면, Meta 는 같은 이름의 Entity 를 뒤에 정의하겠다는 뜻으로 받아들인다.
이 때 ``@declare`` 로 선언해주는 클래스는 이름만 중요할뿐 그 내용은 신경쓰지 않는다.
이제 ``Tree`` 라는 이름을 ``Tree`` 정의에 사용할 수 있게된다.

    >>> tree = Tree()
    >>> tree.children = [Tree(), Tree()]
    >>> tree
    Tree(dict(children=(Tree(), Tree())))
    >>> tree.dump()
    {'children': [{}, {}]}

이런 상황은 꼭 자기 자신을 참조하는 경우만 발생하지는 않는다.

    >>> @meta.declare
    ... class Child: pass
    >>>
    >>> class Mother(meta.Entity):
    ...     children = Child[:]()
    ...

만약 ``@declare`` 한 Entity 의 정의를 제공하겠다는 약속을 지키지 않아도, 그 Entity 가 필요한 순간이 오기 전에는 문제를 일으키지 않는다.

    >>> mother = Mother()
    >>> mother.children = []

하지만 필요한 시점이 오면 :py:exc:`ReferenceError` 예외를 일으킨다.

    >>> mother.children = [{}]
    Traceback (most recent call last):
        ...
    ReferenceError: unresolved class __main__.Child

약속을 이행하면 문제가 해결된다.

    >>> class Child(meta.Entity):
    ...     mother = Mother()
    >>>
    >>> mother.children = [{}]
    >>> mother
    Mother(dict(children=(Child(),)))
    >>> mother.dump()
    {'children': [{}]}

Hiding Properties
-----------------

앞에서 예로 든 ``Mother`` 와 ``Child`` 의 구조는 실용적이지 않다. 그 의미상 클래스 구조 뿐만 아니라 인스턴스 역시 상호 참조해야 하기 때문이다.
만약 ``Child`` 의 ``mother`` 에 값을 주고 직렬화 한다면 무한 순환에 빠지게 된다.

    >>> child = Child()
    >>> child.mother = mother
    >>> mother.children = [child]
    >>> mother.dump()
    Traceback (most recent call last):
        ...
    OverflowError

이처럼 Entity 인스턴스가 순환 참조되는 경우 :py:exc:`OverflowError` 예외를 일으킨다.

이런 무한 순환을 막는 방법중 하나는, Entity 를 특정할 수 있는 속성을 도입하고, 어느 한쪽에서 순환 고리를 끊는 것이다.

    >>> @meta.declare
    ... class Child: pass
    >>>
    >>> class Mother(meta.Entity):
    ...     id = meta.String()
    ...     children = Child[:]()
    ...
    >>> class Child(meta.Entity):
    ...     mother = Mother(only='id')
    >>>
    >>> mother = Mother()
    >>> mother.id = '1234'
    >>> child = Child()
    >>> mother.children = [child]
    >>> child.mother = mother.copy()
    >>> pprint(mother.dump())
    {'children': [{'mother': {'id': '1234'}}], 'id': '1234'}

Entity 에 제공할 수 있는 ``only`` 라는 옵션은,
지정한 속성들(:py:class:`list` 를 줄 수 있다)을 제외한 모든 속성들을 직렬화에 포함시키지 않도록 만든다.

