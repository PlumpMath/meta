import json
from collections import OrderedDict

import pytest
from flowdas import meta
from flowdas.meta.compat import *
from flowdas.meta.property import Marker


def test_null():
    assert not meta.Null


def test_property_protocol():
    class P(meta.Property):
        def _load_(self, value, context):
            return value

    class X(object):
        p = P()

        def _get_(self, name):
            return self.__dict__.get(name)

        def _set_(self, name, value):
            self.__dict__[name] = value

        def _delete_(self, name):
            self.__dict__.pop(name, None)

    X.p._bind_('p', X)

    x = X()

    assert x.p is None
    p = 12345
    x.p = p
    assert x.p is p
    assert x.__dict__ == {'p': p}
    del x.p
    assert x.p is None
    assert x.__dict__ == {}


def test_serialization():
    class P(meta.Property):
        def _load_(self, value, context):
            return value

        def _dump_(self, value, context):
            return value

    p = P()

    assert 12345 == p.dump(p.load(12345))


def check_tuple3567(X):
    X.p3._bind_('p3', X)
    X.p5._bind_('p5', X)
    X.p6._bind_('p6', X)
    X.p7._bind_('p7', X)

    x = X()

    assert x.p3 is None
    x.p3 = [123] * 33
    assert x.p3 == (123,) * 33
    x.p3 = []
    assert x.p3 == ()
    with pytest.raises(ValueError):
        x.p3 = 123

    assert x.p5 is None
    x.p5 = [123] * 5
    assert x.p5 == (123,) * 5
    with pytest.raises(ValueError):
        x.p5 = [123] * 4
    with pytest.raises(ValueError):
        x.p5 = [123] * 6

    assert x.p6 is None
    for i in range(2, 6, 3):
        x.p6 = [123] * i
        assert x.p6 == (123,) * i
    with pytest.raises(ValueError):
        x.p6 = [123] * 3
    with pytest.raises(ValueError):
        x.p6 = [123] * 4

    assert x.p7 is None
    for i in [2, 5]:
        x.p7 = [123] * i
        assert x.p7 == (123,) * i
    with pytest.raises(ValueError):
        x.p7 = [123] * 3
    with pytest.raises(ValueError):
        x.p7 = [123] * 4


def test_tuple():
    class P(meta.Property):
        def _load_(self, value, context):
            return value

        def _dump_(self, value, context):
            return value

    class X(object):
        p1 = meta.Tuple(P())
        p2 = meta.Tuple(P(), P())
        p3 = meta.Tuple(P(), repeat=Ellipsis)
        p4 = meta.Tuple(P(), P(), repeat=Ellipsis)
        p5 = meta.Tuple(P(), repeat=5)
        p6 = meta.Tuple(P(), repeat=slice(2, 6, 3))
        p7 = meta.Tuple(P(), repeat=[2, 5])

        def _get_(self, name):
            return self.__dict__.get(name)

        def _set_(self, name, value):
            self.__dict__[name] = value

        def _delete_(self, name):
            self.__dict__.pop(name, None)

    X.p1._bind_('p1', X)
    X.p2._bind_('p2', X)
    X.p4._bind_('p4', X)

    x = X()

    assert x.p1 is None
    x.p1 = [123]
    assert isinstance(x.p1, tuple)
    assert x.p1 == (123,)
    x.p1 = (123,)
    assert x.p1 == (123,)
    with pytest.raises(ValueError):
        x.p1 = 123
    with pytest.raises(ValueError):
        x.p1 = [123, 456]

    assert x.p2 is None
    x.p2 = [123, 456]
    assert x.p2 == (123, 456)
    with pytest.raises(ValueError):
        x.p2 = [123]

    assert x.p4 is None
    x.p4 = [123] * 32
    assert x.p4 == (123,) * 32
    x.p4 = []
    assert x.p4 == ()
    with pytest.raises(ValueError):
        x.p4 = [123] * 33

    check_tuple3567(X)

    with pytest.raises(TypeError):
        meta.Tuple(None)

    assert repr(meta.Tuple()) == 'Tuple()'
    assert repr(meta.Tuple(P())) == 'Tuple(P())'


def test_default_in_tuple():
    class X(meta.Entity):
        p = meta.Tuple(meta.Integer(default=1))

    x = X()
    x.p = (None,)
    assert x.p == (1,)


def test_tuplization():
    class P(meta.Property):
        def _load_(self, value, context):
            return value

        def _dump_(self, value, context):
            return value

    class X(object):
        p3 = P[:]()
        p5 = P[5]()
        p6 = P[2:6:3]()
        p7 = P[2, 5]()

        def _get_(self, name):
            return self.__dict__.get(name)

        def _set_(self, name, value):
            self.__dict__[name] = value

        def _delete_(self, name):
            self.__dict__.pop(name, None)

    check_tuple3567(X)

    class X(object):
        p3 = P[Ellipsis]()
        p5 = P[5]()
        p6 = P[2:6:3]()
        p7 = P[2, 5]()

        def _get_(self, name):
            return self.__dict__.get(name)

        def _set_(self, name, value):
            self.__dict__[name] = value

        def _delete_(self, name):
            self.__dict__.pop(name, None)

    check_tuple3567(X)


def test_marker():
    context = meta.Context()
    value = {
        'a': [1, 2, 3],
        'b': [5, {
            'x': 1234,
        }]
    }

    def travel(value, context):
        if value == 1234:
            raise ValueError()
        with Marker(context, value) as marker:
            if isinstance(value, dict):
                for k, v in value.items():
                    with marker.cursor(k, v):
                        travel(v, marker.context)
            elif isinstance(value, (tuple, list)):
                for i, v in enumerate(value):
                    with marker.cursor(i, v):
                        travel(v, marker.context)

    with pytest.raises(ValueError):
        travel(value, context)

    assert context.errors is not None
    assert context.errors[0].value == 1234
    assert context.errors[0].location == '/b/1/x'


def test_apply_options():
    class P(meta.Property):
        def _load_(self, value, context):
            return value

        def _dump_(self, value, context):
            return value

    class X(object):
        p1 = P().apply_options()

        p2 = P().apply_options(required=True)

        def _set_(self, name, value):
            self.__dict__[name] = value

    x = X()
    x.p1 = None

    with pytest.raises(ValueError):
        x.p2 = None


def test_ordered():
    class P(meta.Property):
        def _load_(self, value, context):
            return value

        def _dump_(self, value, context):
            return value

    class X(object):
        p1 = P()

        p2 = P(ordered=True)

        def _set_(self, name, value):
            self.__dict__[name] = value

    assert not X.p1.is_ordered()
    assert X.p2.is_ordered()
    assert X.p1._pm_order_ is None
    assert isinstance(X.p2._pm_order_, integer_types)


def test_validate():
    class P(meta.Property):
        def _load_(self, value, context):
            return value

        def _dump_(self, value, context):
            return value

    class X(object):
        p1 = P(validate=lambda v: 1 < v < 7)

        def _set_(self, name, value):
            self.__dict__[name] = value

    x = X()
    x.p1 = 2
    with pytest.raises(ValueError):
        x.p1 = 1


def test_json_codec():
    class X(meta.Entity):
        a = meta.JsonObject()
        b = meta.JsonObject(codec='json')

    x = X()
    data = OrderedDict({'x': 1, 'y': []})
    x.a = x.b = data
    assert x.dump() == {'a': data, 'b': data}
    assert x.dump(meta.Context()) == {'a': data, 'b': json.dumps(data, ensure_ascii=False, separators=(',', ':'))}
    x = X(codec='json')
    x.a = data
    assert x.dump() == {'a': data}
    assert x.dump(meta.Context()) == json.dumps({'a': data}, ensure_ascii=False, separators=(',', ':'))


def test_context_local_codec():
    class X(meta.Entity):
        a = meta.Integer(codec='test')

    class TestCodec(meta.Codec):
        def encode(self, value, property, context):
            return -value

        def decode(self, value, property, context):
            return -value

    ctx = meta.Context()
    ctx.set_codec('test', TestCodec())

    x = X()
    x.a = 123
    assert x.dump(ctx) == {'a': -123}
    x = X().load({'a': 789}, ctx)
    assert x.a == -789

    with pytest.raises(LookupError):
        x.dump(meta.Context())

    ctx.set_codec('test', TestCodec())

    x = X()
    x.a = 123
    assert x.dump(ctx) == {'a': -123}
    x = X().load({'a': 789}, ctx)
    assert x.a == -789


def test_overide_options():
    class PositiveInteger(meta.Integer):
        class Options(meta.Integer.Options):
            validate = staticmethod(lambda x: x > 0)
            newoption = None

    class X(meta.Entity):
        positive = PositiveInteger(newoption=True)

    x = X()
    x.positive = 1
    assert x.positive == 1
    with pytest.raises(ValueError):
        x.positive = -1
    assert X.positive.get_options().newoption is True


def test_selector():
    class A(meta.Entity):
        pass

    class X(meta.Entity):
        class Options(meta.Entity.Options):
            many = False

        @meta.Selector(A(), A[:]())
        def data(self):
            return self.get_options().many

    x = X()
    a = A()
    x.data = a
    with pytest.raises(ValueError):
        x.data = [a]
    assert x.dump() == {'data': {}}

    x = X(many=True)
    x.data = [a]
    with pytest.raises(ValueError):
        x.data = a
    assert x.dump() == {'data': [{}]}

    # error conditions

    with pytest.raises(TypeError):
        meta.Selector(None)

    class X(meta.Entity):
        data = meta.Selector(A(), A[:]())

    x = X()
    with pytest.raises(NotImplementedError):
        x.data = a

    class X(meta.Entity):
        @meta.Selector(A(), A[:]())
        def data(self):
            return None

    x = X()
    with pytest.raises(TypeError):
        x.data = a

    class X(meta.Entity):
        @meta.Selector(A(), A[:]())
        def data(self):
            return 2

    x = X()
    with pytest.raises(IndexError):
        x.data = a


def test_options():
    class X(meta.Entity):
        class Options(meta.Entity.Options):
            opt = False

    x = X(opt=True)
    assert x.get_options().opt is True

    assert repr(x.get_options()) == 'Options(opt=True)'


def test_context():
    assert repr(meta.Context()) == 'Context()'

    ctx = meta.Context(strict=True)
    with pytest.raises(ValueError):
        x = meta.Entity().load({'x': 1}, ctx)
    assert repr(ctx) == 'Context(errors=[ValueError(/x?)], strict=True)'
