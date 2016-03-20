# coding=utf-8
from __future__ import print_function

import random
from collections import OrderedDict

import pytest
from flowdas import meta
from flowdas.meta.compat import *
from tests import *

boolean_options = ('required',)
boolean_values = (True, False)
int_options = ()
int_values = (0, 1)

property_options = cross_dict(cross_kv(boolean_options, boolean_values), cross_kv(int_options, int_values))

boolean_options = ('freeze',)

all_options = cross_kv(boolean_options, boolean_values)


class P(meta.Property):
    def _load_(self, value, context):
        return value

    def _dump_(self, value, context):
        return value


def meta_options(options):
    def deco(meta):
        for k, v in options.items():
            setattr(meta, k, v)
        return meta

    return deco


@pytest.mark.parametrize('options', all_options)
def test_options(options):
    with pytest.raises(TypeError):
        class X(meta.Entity):
            @meta_options(dict(unknown_option=False))
            class Meta:
                pass

    class X(meta.Entity):
        @meta_options(options)
        class Meta:
            pass

    x = X()

    if options['freeze']:
        with pytest.raises(AttributeError):
            x.undefined = False
    else:
        x.undefined = False
        assert x.undefined == False


def test_nesting():
    class MyStruct(meta.Entity):
        member = P(required=True)

    class MyEntity(meta.Entity):
        property = MyStruct(required=True)

    entity = MyEntity()
    assert entity.property is None
    with pytest.raises(ValueError):
        entity.validate()
    struct = MyStruct()
    entity.property = struct
    assert struct is entity.property
    assert struct is entity['property']
    with pytest.raises(ValueError):
        entity.validate()

    assert struct.member is None
    with pytest.raises(ValueError):
        struct.validate()
    struct.member = 12345
    assert 12345 == struct.member
    assert 12345 == struct['member']
    struct.validate()
    entity.validate()

    with pytest.raises(ValueError):
        entity.property = entity


def test_isolation():
    class Y(meta.Entity):
        d = P()

    class X(meta.Entity):
        y = Y(required=True)

    data1 = {"y": {}}
    x1 = X().load(data1)
    assert x1 is not None
    assert x1.y is not None
    assert x1.y.d is None
    assert data1 == x1.dump()

    data2 = {"y": {"d": {}}}
    x2 = X().load(data2)
    assert x2 is not None
    assert x2.y is not None
    assert x2.y.d is not None
    assert data2 == x2.dump()

    assert x1 is not x2
    assert x1.y is not x2.y
    assert x1.y.d is not x2.y.d

    assert x1.y.d is None
    assert data1 == x1.dump()


def test_declare():
    @meta.declare
    class X: pass

    class X(meta.Entity):
        x = X(required=True)

    @meta.declare
    class Child: pass

    class Parent(meta.Entity):
        children = Child[:](required=True)

    class Child(meta.Entity):
        parent = Parent(required=True)

    @meta.declare
    class Y: pass

    class Z(meta.Entity):
        y = Y(required=True)

    x1 = X()
    x2 = X()
    x1.x = x2

    assert {'x': {}} == x1.dump()
    with pytest.raises(ValueError):
        x1.validate()

    z = Z()
    y = Y()
    with pytest.raises(ReferenceError):
        z.y = y

    p = Parent()
    c1 = Child()
    c2 = Child()

    c1.parent = c2.parent = p
    p.children = [c1, c2]

    p.validate()

    with pytest.raises(OverflowError):
        p.dump()


def test_dump_with_hole():
    class X(meta.Entity):
        pass

    class Y(meta.Entity):
        x = meta.Tuple(X(required=False), repeat=Ellipsis)

    y = Y()
    y.x = [X(), None, X()]

    assert {'x': [{}, None, {}]} == y.dump()


def test_polymorphism():
    class B(meta.Entity):
        type = meta.Kind('B')

    class D(B):
        type = 'D'
        i = P()

    class Y(meta.Entity):
        b = B()

    y = Y().load({'b': {'type': 'D', 'i': 1234}})

    assert isinstance(y.b, D)
    assert y.b.i == 1234


def test_inheritance():
    class B(meta.Entity):
        b = P()

    class D(B):
        d = P()

    x = D()
    x.d = 'abc'
    x.b = 3

    x.validate()

    assert {'b': 3, 'd': 'abc'} == x.dump()

    class X(meta.Entity):
        x = P()

    class Y(X):
        x = P()

    x = X()
    x.x = 345
    x.validate()
    assert {'x': 345} == x.dump()

    y = Y()
    y.x = 'abc'
    y.validate()
    assert {'x': 'abc'} == y.dump()


def test_equality():
    class B(meta.Entity):
        i = P()

    class D(B):
        s = P()
        b = B()

    x1 = D()
    x1.i = 123
    x1.s = 'abc'
    x1.b = B()
    x1.b.i = 456

    x2 = D()
    x2.i = 123
    x2.s = 'abc'
    x2.b = B()
    x2.b.i = 456

    assert x1 == x2
    assert x1 == {'i': 123, 's': 'abc', 'b': {'i': 456}}
    assert {'i': 123, 's': 'abc', 'b': {'i': 456}} == x1
    assert x1 == {'i': 123, 's': 'abc', 'b': x2.b}
    assert {'i': 123, 's': 'abc', 'b': x2.b} == x1
    assert x1 != 789
    assert 789 != x1

    x2.b.i = 789

    assert x1 != x2

    x2.b.i = None

    assert x1 != x2

    x1.b.i = meta.Null

    assert x1 != x2

    x1.b.i = None

    assert x1 == x2

    x1.i = x1.b.i = 12345
    b = x1.b
    x1.b = None
    x1.s = None

    assert x1 == b
    assert b == x1


def test_str():
    class B(meta.Entity):
        x = P[:]()

    class C(meta.Entity):
        b = B[:]()

    c = C()
    c.b = [B()]
    c.b[0].x = [1, 2, 3]

    assert str(c) == '{"b":[{"x":[1,2,3]}]}'


def test_patch():
    class X(meta.Entity):
        a = P()
        b = P()
        c = P()

    x1 = X()
    x1.update(a=1, b=2, c=3)
    assert x1 == dict(a=1, b=2, c=3)

    d = dict(a=1, b=5)
    x2 = X()
    x2.update(d)
    assert x2 == d

    delta = x1 ^ x2
    assert delta == dict(b=2, c=3)
    assert x2.patch(delta) == x1

    delta = x2 ^ x1
    assert delta == dict(b=5, c=meta.Null)
    assert x1.copy().patch(delta, inplace=True) == x2

    delta = x2.copy()
    delta ^= x1
    assert delta == dict(b=5, c=meta.Null)
    assert x1.patch(delta) == x2


@pytest.mark.parametrize('options', property_options)
def test_copy(options):
    class X(meta.Entity):
        a = P()

        def __init__(self, arg, opt=None, **kwargs):
            super(X, self).__init__(**kwargs)
            self.arg = arg
            self.opt = opt

        def copy(self):
            return self._copy_(self.arg, opt=self.opt)

    x = X(1234, opt=4567, **options)
    x.a = 89
    c = x.copy()

    assert x == c
    assert x.__class__ == c.__class__
    assert x.get_options().__dict__ == c.get_options().__dict__
    assert x.arg == c.arg
    assert x.opt == c.opt


def test_ordered():
    class X(meta.Entity):
        a = P()
        b = P(ordered=True)
        y = P()
        x = P(ordered=True)
        c = P(ordered=True)

    x = X()
    x.update(a=1, b=2, c=3, x=4, y=5)

    assert isinstance(x.dump(), OrderedDict)
    assert list(x.keys())[:3] == ['b', 'x', 'c']


def test_default():
    class X(meta.Entity):
        a = P(default=123)
        b = P(default=random.random)
        c = meta.Tuple(P(), default=tuple, repeat=Ellipsis)

    x = X()

    assert x == {}
    assert list(x.keys()) == []
    assert x.a == 123
    assert x == {'a': 123}
    assert list(x.keys()) == ['a']
    r = x.get('b')
    assert r is not None
    assert r == x.b
    assert x.c == ()
    assert sorted(list(x.keys())) == ['a', 'b', 'c']

    x = X()

    assert x == {}
    x.a = 456
    assert x.a == 456
    x.b = 100
    assert 100 == x.b

    x = X()
    b = x.b
    assert x.dump() == {'a': 123, 'b': b, 'c': []}


def test_error():
    @meta.declare
    class X: pass

    class X(meta.Entity):
        x = X(required=True)

    d = dict(x=dict(x=1))
    context = meta.Context()
    with pytest.raises(ValueError):
        X().load(d, context)
    assert context.errors is not None
    assert len(context.errors) == 1
    assert context.errors[0].value == 1
    assert context.errors[0].location == '/x/x'
    assert context.errors[0].exc_info[0] == ValueError

    @meta.declare
    class Child: pass

    class Parent(meta.Entity):
        children = Child[:](required=True)

    class Child(meta.Entity):
        parent = Parent(required=True)

    d = dict(
        children=[
            dict(
                parent={},
            ),
            dict(parent=dict(
                children=[dict(parent=None)]
            ))
        ],
    )
    context = meta.Context()
    with pytest.raises(ValueError):
        Parent().load(d, context)

    assert context.errors[0].value == None
    assert context.errors[0].location == '/children/1/parent/children/0/parent'
    assert context.errors[0].exc_info[0] == ValueError

    d = dict(
        children=[
            dict(
                parent={},
            ),
            dict(parent=dict(
                children=[dict(father=None)]
            ))
        ],
    )
    context = meta.Context(strict=True)
    with pytest.raises(ValueError):
        Parent().load(d, context)

    assert context.errors[0].value is meta.Null
    assert context.errors[0].location == '/children/1/parent/children/0/father'
    assert context.errors[0].exc_info[0] == ValueError


def test_multi_errors():
    @meta.declare
    class Child: pass

    class Parent(meta.Entity):
        children = Child[:](required=True)

    class Child(meta.Entity):
        parent = Parent(required=True)

    d = dict(
        children=[
            1,  # error
            dict(
                parent=None,  # error
            ),
            dict(parent=dict(
                children=[
                    dict(
                        father=None,  # error
                    ),
                ]
            )),
            'abc',  # error
        ],
    )
    context = meta.Context(strict=True, max_errors=3)
    with pytest.raises(ValueError):
        Parent().load(d, context)

    assert len(context.errors) == 3

    assert context.errors[0].location == '/children/0'
    assert context.errors[0].value == 1
    assert context.errors[0].exc_info[0] == ValueError

    assert context.errors[1].location == '/children/1/parent'
    assert context.errors[1].value is None
    assert context.errors[1].exc_info[0] == ValueError

    assert context.errors[2].location == '/children/2/parent/children/0/father'
    assert context.errors[2].value is meta.Null
    assert context.errors[2].exc_info[0] == ValueError


def test_union():
    class P(meta.Property):
        def _load_(self, value, context):
            return value

        def _dump_(self, value, context):
            return value

    class X(meta.Entity):
        class Y(meta.Union):
            v = P[:]().apply_options(ordered=True)
            s = P(ordered=True)

        p = Y()

    x = X()

    assert x.p is None
    assert x.dump() == {}

    x.p = 123
    assert x.p.s == 123
    assert x.p.v is None
    assert x.p == 123
    assert 123 == x.p
    assert x.dump() == {'p': 123}

    x.p = (123,)
    assert x.p.v == (123,)
    assert x.p.s is None
    assert x.p == (123,)
    assert (123,) == x.p
    assert x.dump() == {'p': [123]}

    x.p = P()

    x.p.s = 123
    assert x.p.s == 123
    assert x.p.v is None
    assert x.dump() == {'p': 123}

    x.p.v = (123,)
    assert x.p.v == (123,)
    assert x.p.s is None
    assert x.dump() == {'p': [123]}

    x1 = X()
    x2 = X()

    x1.p = 123
    x2.p = (123,)
    assert x1.p.s == 123
    assert x2.p.v == (123,)
    assert x2.dump() == {'p': [123]}
    assert x1.dump() == {'p': 123}

    class X(meta.Entity):
        class Y(meta.Union):
            v = P[:]()
            s = P(ordered=True)

        p = Y()

    x = X()

    assert x.p is None
    assert x.dump() == {}

    x.p = 123
    assert x.p.s == 123
    assert x.dump() == {'p': 123}

    x.p = (123,)
    assert x.p.s == (123,)
    assert x.dump() == {'p': (123,)}


def test_union_with_error():
    class U(meta.Union):
        s = meta.Integer(ordered=True)
        m = meta.String(ordered=True)

    class X(meta.Entity):
        a = meta.Tuple(meta.Integer(), U())

    ctx = meta.Context(max_errors=10)
    with pytest.raises(ValueError):
        x = X().load({'a': ['abc', 'xyz']}, ctx)

    print(ctx.errors)
    assert len(ctx.errors) == 1
    assert ctx.errors[0].location == '/a/0'


#
# dict interface: mostly borrowed from Python 3.X test.test_dict
#

def test_constructor():
    # calling built-in types without argument must return empty
    assert meta.Entity() == {}
    assert meta.Entity({}) == {}
    assert meta.Entity([]) == {}


def test_bool():
    class X(meta.Entity):
        a = meta.Integer()

    assert not X()
    x = X()
    assert bool(x) == False
    x.a = 0
    assert bool(x) == True


def test_keys():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()

    d = X()
    assert set(d.keys()) == set()
    d.update({'a': 1, 'b': 2})
    k = d.keys()
    assert 'a' in d
    assert 'b' in d
    with pytest.raises(TypeError):
        d.keys(None)


def test_values():
    class X(meta.Entity):
        a = meta.Integer()

    d = X()
    assert set(d.values()) == set()
    d.update({'a': 2})
    assert set(d.values()) == {2}
    with pytest.raises(TypeError):
        d.values(None)


def test_items():
    class X(meta.Entity):
        a = meta.Integer()

    d = X()
    assert set(d.items()) == set()

    d.update({'a': 2})
    assert set(d.items()) == {('a', 2)}
    with pytest.raises(TypeError):
        d.items(None)


def test_contains():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()

    d = X()
    assert 'a' not in d
    assert not ('a' in d)
    d.update({'a': 1, 'b': 2})
    assert 'a' in d
    assert 'b' in d
    assert 'c' not in d
    with pytest.raises(TypeError):
        d.__contains__()


def test_len():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()

    d = X()
    assert len(d) == 0
    d.update({'a': 1, 'b': 2})
    assert len(d) == 2


def test_getitem():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()
        c = meta.Integer()

    d = X()
    d.update({'a': 1, 'b': 2})

    assert d['a'] == 1
    assert d['b'] == 2
    d['c'] = 3
    d['a'] = 4
    assert d['c'] == 3
    assert d['a'] == 4
    del d['b']
    assert d == {'a': 4, 'c': 3}

    with pytest.raises(TypeError):
        d.__getitem__()


def test_clear():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()
        c = meta.Integer()

    d = X()
    d.update({'a': 1, 'b': 2, 'c': 3})
    d.clear()
    assert d == {}

    with pytest.raises(TypeError):
        d.clear(None)


def test_update():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()
        c = meta.Integer()

    d = X()
    d.update({'a': 100})
    d.update({'b': 20})
    d.update({'a': 1, 'b': 2, 'c': 3})
    assert d, {'a': 1, 'b': 2, 'c': 3}

    d.update()
    assert d, {'a': 1, 'b': 2, 'c': 3}

    with pytest.raises(TypeError):
        d.update(None)

    class SimpleUserDict:
        def __init__(self):
            self.d = {'a': 1, 'b': 2, 'c': 3}

        def keys(self):
            return self.d.keys()

        def __getitem__(self, i):
            return self.d[i]

    d.clear()
    d.update(SimpleUserDict())
    assert d == {'a': 1, 'b': 2, 'c': 3}

    class Exc(Exception):
        pass

    d.clear()

    class FailingUserDict:
        def keys(self):
            raise Exc

    with pytest.raises(Exc):
        d.update(FailingUserDict())

    class FailingUserDict:
        def keys(self):
            class BogonIter:
                def __init__(self):
                    self.i = 1

                def __iter__(self):
                    return self

                def __next__(self):
                    if self.i:
                        self.i = 0
                        return 'a'
                    raise Exc

                if PY2:
                    next = __next__

            return BogonIter()

        def __getitem__(self, key):
            return ord(key)

    with pytest.raises(Exc):
        d.update(FailingUserDict())

    class FailingUserDict:
        def keys(self):
            class BogonIter:
                def __init__(self):
                    self.i = ord('a')

                def __iter__(self):
                    return self

                def __next__(self):
                    if self.i <= ord('c'):
                        rtn = chr(self.i)
                        self.i += 1
                        return rtn
                    raise StopIteration

                if PY2:
                    next = __next__

            return BogonIter()

        def __getitem__(self, key):
            raise Exc

    with pytest.raises(Exc):
        d.update(FailingUserDict())

    class badseq(object):
        def __iter__(self):
            return self

        def __next__(self):
            raise Exc()

        if PY2:
            next = __next__

    with pytest.raises(Exc):
        X().update(badseq())

    with pytest.raises(ValueError):
        X().update([(1, 2, 3)])


def test_copy2():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()
        c = meta.Integer()

    d = X()
    d.update({'a': 1, 'b': 2, 'c': 3})
    assert d.copy() == {'a': 1, 'b': 2, 'c': 3}
    assert X().copy() == {}
    with pytest.raises(TypeError):
        d.copy(None)


def test_get():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()
        c = meta.Integer()

    d = X()
    assert d.get('c') is None
    assert d.get('c', 3) == 3
    d.update({'a': 1, 'b': 2})
    assert d.get('c') is None
    assert d.get('c', 3) == 3
    assert d.get('a') == 1
    assert d.get('a', 3) == 1
    with pytest.raises(TypeError):
        d.get()
    with pytest.raises(TypeError):
        d.get(None, None, None)


def test_setdefault():
    class X(meta.Entity):
        key0 = meta.JsonArray()
        key = meta.JsonArray()

    d = X()
    assert d.setdefault('key0') is None
    assert d.setdefault('key0', []) == []
    assert d.setdefault('key0') == []
    d.setdefault('key', []).append(3)
    assert d['key'][0] == 3
    d.setdefault('key', []).append(4)
    assert len(d['key']) == 2
    with pytest.raises(TypeError):
        d.setdefault()


def test_popitem():
    # dict.popitem()
    for copymode in -1, +1:
        # -1: b has same structure as a
        # +1: b is a.copy()
        for log2size in range(12):
            size = 2 ** log2size
            X = meta.Entity.define_subclass('X', {'p' + repr(i): meta.Integer() for i in range(size)})
            a = X()
            b = X()
            for i in range(size):
                a['p' + repr(i)] = i
                if copymode < 0:
                    b['p' + repr(i)] = i
            if copymode > 0:
                b = a.copy()
            for i in range(size):
                ka, va = ta = a.popitem()
                assert va == int(ka[1:])
                kb, vb = tb = b.popitem()
                assert vb == int(kb[1:])
                # assert not (copymode < 0 and ta != tb) ; 이 조건은 보장할 수 없다. 실제로 PyPy 에서는 통과하지 못한다.
            assert not a
            assert not b

    d = meta.Entity()
    with pytest.raises(KeyError):
        d.popitem()


def test_pop():
    class X(meta.Entity):
        abc = meta.Primitive()

    d = X()
    k, v = 'abc', 'def'
    d[k] = v
    with pytest.raises(KeyError):
        d.pop('ghi')

    assert d.pop(k) == v
    assert len(d) == 0

    with pytest.raises(KeyError):
        d.pop(k)

    assert d.pop(k, v) == v
    d[k] = v
    assert d.pop(k, 1) == v

    with pytest.raises(TypeError):
        d.pop()


def test_mutating_iteration():
    # changing dict size during iteration
    class X(meta.Entity):
        p1 = meta.Integer()
        p2 = meta.Integer()

    d = X()
    d['p1'] = 1
    with pytest.raises(RuntimeError):
        for i in d:
            d['p%d' % (int(i[1:]) + 1)] = 1


def test_eq():
    class X(meta.Entity):
        a = meta.Integer()
        b = meta.Integer()

    assert X() == X()
    assert X() == {}
    assert {} == X()
    x = X()
    x.update({'a': 2})
    assert x == {'a': 2}


def test_instance_dict_getattr_str_subclass():
    class Foo(meta.Entity):
        msg = meta.Primitive()

        def __init__(self, msg):
            super(Foo, self).__init__()
            self.msg = msg

    f = Foo('123')

    class _str(str):
        pass

    assert f.msg == getattr(f, _str('msg'))
    assert f.msg == f[_str('msg')]


def test_metaoptions():
    class X(meta.Entity):
        pass

    x = X()
    x.undefined = 1

    class X(meta.Entity):
        class Meta:
            freeze = True

    x = X()
    with pytest.raises(AttributeError):
        x.undefined = 1

    class ProtectedEntity(meta.Entity):
        class MetaOptions(meta.Entity.MetaOptions):
            freeze = True

    class X(ProtectedEntity):
        pass

    x = X()
    with pytest.raises(AttributeError):
        x.undefined = 1


def test_validate():
    class X(meta.Entity):
        a = meta.Integer(required=True)
        b = meta.Integer()
        c = meta.Integer(required=True, default=3)
        d = meta.Integer(default=4)

    x = X()
    with pytest.raises(ValueError):
        x.validate()

    x = X()
    x.update(a=1)

    assert 'c' not in x
    assert 'd' not in x

    x.validate()

    assert 'c' in x
    assert 'd' in x


def test_is_visible():
    class X(meta.Entity):
        a = meta.Integer(required=True)
        b = meta.Integer()
        c = meta.Integer(view='private')

    public = meta.Context(view='public')
    private = meta.Context(view='private')

    x = X()
    assert x.is_visible('a', None)
    assert x.is_visible('b', None)
    assert x.is_visible('c', None)

    assert x.is_visible('a', public)
    assert x.is_visible('b', public)
    assert not x.is_visible('c', public)

    assert x.is_visible('a', private)
    assert x.is_visible('b', private)
    assert x.is_visible('c', private)

    x = X(only='b')
    assert x.is_visible('a', None)
    assert x.is_visible('b', None)
    assert not x.is_visible('c', None)

    assert x.is_visible('a', public)
    assert x.is_visible('b', public)
    assert not x.is_visible('c', public)

    assert x.is_visible('a', private)
    assert x.is_visible('b', private)
    assert not x.is_visible('c', private)

    x = X(only='c')
    assert x.is_visible('a', None)
    assert not x.is_visible('b', None)
    assert x.is_visible('c', None)

    assert x.is_visible('a', public)
    assert not x.is_visible('b', public)
    assert not x.is_visible('c', public)

    assert x.is_visible('a', private)
    assert not x.is_visible('b', private)
    assert x.is_visible('c', private)
