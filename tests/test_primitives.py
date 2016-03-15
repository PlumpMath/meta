# coding=utf-8
from __future__ import print_function

import cmath
import decimal
import math
import time
import uuid

import pytest
from flowdas import meta
from flowdas.meta.compat import *
from tests import *


class SimpleEntity(meta.Entity):
    a = meta.Boolean()


entity = SimpleEntity()
entity.a = True


def check_json(value):
    assert isinstance(value, (basestring_types, integer_types, float, list, tuple, dict))
    if isinstance(value, (list, tuple)):
        for v in value:
            check_json(v)
    elif isinstance(value, dict):
        for k, v in value.items():
            assert isinstance(k, str)
            check_json(v)


@pytest.mark.parametrize('P', [meta.String, meta.Unicode, meta.Bytes])
def test_string(P):
    class X(meta.Entity):
        p = P()

    success = ['한', u'한', b'\xed\x95\x9c']
    failure = [False, True, 0, 1, long_type(1), 1.0, 0.1, [1], (1,), ['a'], ('b',), {'a': 1}, entity]

    x = X()

    for value in success:
        x.p = value
        if P not in (meta.Unicode, meta.Bytes):
            assert value == x.p
        x.validate()

        if P == meta.Unicode:
            assert unicode_type == type(x.p)
        elif P == meta.Bytes:
            assert bytes_type == type(x.p)
        else:
            assert type(value) == type(x.p)

        decoded = X.p.load(value)
        encoded = X.p.dump(decoded)
        check_json(encoded)
        assert encoded == decoded

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value

    #
    # allow_empty
    #

    class X(meta.Entity):
        p = P(allow_empty=False)

    x = X()

    x.p = 'x'
    with pytest.raises(ValueError):
        x.p = ''

    #
    # encoding
    #

    if P != meta.String:
        class X(meta.Entity):
            p = P(default_encoding='cp949')

        x = X()

        x.p = ''

        for value in (u'한', b'\xc7\xd1'):

            if P == meta.Unicode:
                x.p = value
                assert x.p == u'한'
                with pytest.raises(ValueError):
                    x.p = b'\xed\x95\x9c'
            else:
                x.p = value
                assert x.p == b'\xc7\xd1'
                x.p = b'\xed\x95\x9c'


@pytest.mark.parametrize('P', [meta.Number, meta.Integer, meta.Float])
def test_number(P):
    class X(meta.Entity):
        p = P()

    success = [0, 1, long_type(1), 1.0, MAX_SAFE_INTEGER + 1, -MAX_SAFE_INTEGER - 1]
    failure = ['한', u'한', b'\xed\x95\x9c', False, True, [1], (1,), ['a'], ('b',), {'a': 1}, entity,
               float('nan'), float('inf'), float('-inf')]

    x = X()

    if P != meta.Integer:
        success.append(0.1)

    for value in success:
        x.p = value
        assert value == x.p
        x.validate()

        if P == meta.Integer:
            assert isinstance(x.p, integer_types)
        elif P == meta.Float:
            assert float == type(x.p)
        else:
            assert type(value) == type(x.p)

        decoded = X.p.load(value)
        encoded = X.p.dump(decoded)
        check_json(encoded)
        assert encoded == decoded

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value

    #
    # allow_bool
    #

    class X(meta.Entity):
        p = P(allow_bool=True)

    x = X()

    for value in (False, True):
        x.p = value
        if P == meta.Float:
            assert float == type(x.p)
            assert x.p == value
        else:
            assert int == type(x.p)
            assert x.p == value

        decoded = X.p.load(value)
        encoded = X.p.dump(decoded)
        check_json(encoded)
        assert encoded == decoded

    #
    # allow_nan
    #

    class X(meta.Entity):
        p = P(allow_nan=True)

    x = X()

    for value in (float('nan'), float('inf'), float('-inf')):
        if P == meta.Integer:
            if math.isnan(value):
                with pytest.raises(ValueError):
                    x.p = value
            else:
                with pytest.raises(OverflowError):
                    x.p = value
        else:
            x.p = value
            if math.isnan(value):
                assert math.isnan(x.p)
            else:
                assert x.p == value

    #
    # jssafe
    #

    class X(meta.Entity):
        p = P(jssafe=True)

    x = X()

    for value in (MAX_SAFE_INTEGER + 1, -MAX_SAFE_INTEGER - 1):
        with pytest.raises(ValueError):
            x.p = value


def test_boolean():
    class X(meta.Entity):
        p = meta.Boolean()

    success = [False, True]
    failure = ['한', u'한', b'\xed\x95\x9c', 0, 1, long_type(1), 1.0, 0.1, [1], (1,), ['a'], ('b',), {'a': 1},
               entity]

    x = X()

    for value in success:
        x.p = value
        assert bool == type(x.p)
        assert value == x.p
        x.validate()

        decoded = X.p.load(value)
        encoded = X.p.dump(decoded)
        check_json(encoded)
        assert encoded == decoded

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value


def test_jsonobject():
    class X(meta.Entity):
        p = meta.JsonObject()

    success = [{'a': 1}]
    failure = [False, True, '한', u'한', b'\xed\x95\x9c', 0, 1, long_type(1), 1.0, 0.1, [1], (1,), ['a'], ('b',),
               entity]

    x = X()

    for value in success:
        x.p = value
        assert dict == type(x.p)
        assert value == x.p
        x.validate()

        decoded = X.p.load(value)
        encoded = X.p.dump(decoded)
        check_json(encoded)
        assert encoded == decoded

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value


def test_jsonarray():
    class X(meta.Entity):
        p = meta.JsonArray()

    success = [[1], (1,), ['a'], ('b',)]
    failure = [False, True, '한', u'한', b'\xed\x95\x9c', 0, 1, long_type(1), 1.0, 0.1, {'a': 1}, entity]

    x = X()

    for value in success:
        x.p = value
        assert type(value) == type(x.p)
        assert value == x.p
        x.validate()

        decoded = X.p.load(value)
        encoded = X.p.dump(decoded)
        check_json(encoded)
        assert encoded == decoded

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value


def test_decimal():
    class X(meta.Entity):
        p = meta.Decimal()

    success = [False, True, 0, 1, long_type(1), 1.0, 0.1, MAX_SAFE_INTEGER + 1, -MAX_SAFE_INTEGER - 1, int('9' * 100)]
    failure = ['한', u'한', b'\xed\x95\x9c', [1], (1,), ['a'], ('b',), {'a': 1}, entity,
               float('nan'), float('inf'), float('-inf')]

    x = X()

    for value in success:
        x.p = value
        assert isinstance(x.p, decimal.Decimal)
        assert x.p == value
        x.validate()

        if not isinstance(value, bool):
            x.p = str(value)
            assert isinstance(x.p, decimal.Decimal)
            if isinstance(value, float):
                assert float(x.p) == value
            else:
                assert x.p == value

        encoded = X.p.dump(x.p)
        decoded = X.p.load(encoded)
        check_json(encoded)
        if isinstance(value, float):
            assert float(decoded) == value
        else:
            assert decoded == value

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value

    #
    # allow_nan
    #

    class X(meta.Entity):
        p = meta.Decimal(allow_nan=True)

    x = X()

    for value in (float('nan'), float('inf'), float('-inf')):
        x.p = value
        if math.isnan(value):
            assert x.p.is_nan()
        else:
            assert x.p == value


def test_complex():
    class X(meta.Entity):
        p = meta.Complex()

    success = [False, True, 0, 1, long_type(1), 1.0, 0.1, MAX_SAFE_INTEGER + 1, -MAX_SAFE_INTEGER - 1, 1 + 1j, 1j,
               [1, 1], (1, 1)]
    failure = ['한', u'한', b'\xed\x95\x9c', [1], (1,), ['a'], ('b',), {'a': 1}, entity,
               float('nan'), float('inf'), float('-inf'), [], [1], [1, 2, 3]]

    x = X()

    for value in success:
        x.p = value
        assert isinstance(x.p, complex)
        if isinstance(value, (tuple, list)):
            assert x.p == complex(*value)
        else:
            assert x.p == value
        x.validate()

        encoded = X.p.dump(x.p)
        decoded = X.p.load(encoded)
        check_json(encoded)
        if isinstance(value, (tuple, list)):
            assert decoded == complex(*value)
        else:
            assert decoded == value

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value

    #
    # allow_nan
    #

    class X(meta.Entity):
        p = meta.Complex(allow_nan=True)

    x = X()

    nans = (float('nan'), float('inf'), float('-inf'))
    values = list(nans)
    values.extend(complex(1, x) for x in nans)
    values.extend(complex(x, 1) for x in nans)
    values.extend(complex(x, y) for x in nans for y in nans)

    for value in values:
        x.p = value
        if cmath.isnan(value):
            assert cmath.isnan(x.p)
        else:
            assert x.p == value


def test_uuid():
    class X(meta.Entity):
        p = meta.Uuid()

    ref = uuid.uuid4()
    sample = str(ref)
    samples = [sample]
    samples.append(sample.replace('-', ''))
    samples.append('{' + sample + '}')
    samples.append('{' + sample)
    samples.append(sample + '}')
    samples.append('urn:uuid:' + sample)
    success = [ref]
    success.extend(samples)
    if PY2:
        success.extend(x.decode('utf-8') for x in samples)
    else:
        success.extend(x.encode('utf-8') for x in samples)
    failure = ['한', u'한', b'\xed\x95\x9c', [1], (1,), ['a'], ('b',), {'a': 1}, entity,
               float('nan'), float('inf'), float('-inf'), [], [1], [1, 2, 3]]
    failure.extend(x[:-2] if x.endswith('}') else x[:-1] for x in samples)

    x = X()

    for value in success:
        x.p = value
        assert isinstance(x.p, uuid.UUID)
        assert x.p == ref
        x.validate()

        encoded = X.p.dump(x.p)
        assert encoded == str(ref)
        decoded = X.p.load(encoded)
        check_json(encoded)
        assert decoded == ref

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value


def test_datetime():
    class X(meta.Entity):
        p = meta.DateTime(format='unix')

    success = [datetime.datetime.now(), time.time(), 0, 0.0]
    failure = [datetime.time(), datetime.date(1999, 1, 1), '한', u'한', b'\xed\x95\x9c', [1], (1,), ['a'], ('b',), entity]

    x = X()

    for value in success:
        x.p = value
        assert isinstance(x.p, datetime.datetime)
        x.validate()

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value
            print(value)

    timestamp = 1457276664.038691

    utc_naive = datetime.datetime(2016, 3, 6, 15, 4, 24, 38691)
    kst_naive = datetime.datetime(2016, 3, 7, 0, 4, 24, 38691)

    utc_aware = utc_naive.replace(tzinfo=timezone.utc)
    kst_aware = kst_naive.replace(tzinfo=timezone(datetime.timedelta(hours=9)))

    assert X.p.dump(utc_naive) == timestamp
    assert X.p.dump(utc_aware) == timestamp
    assert X.p.dump(kst_aware) == timestamp

    assert X.p.load(timestamp).tzinfo is timezone.utc
    assert utc_aware == X.p.load(timestamp)
    assert kst_aware == X.p.load(timestamp)

    x.p = timestamp
    assert x.p == utc_aware

    x.p = utc_aware
    assert x.p == utc_aware

    x.p = kst_aware
    assert x.p == utc_aware

    x.p = utc_naive
    assert x.p == utc_naive

    #
    # now
    #
    assert meta.DateTime.now().tzinfo is timezone.utc
    assert -0.01 < X.p.dump(meta.DateTime.now()) - time.time() <= 0

    #
    # iso8601
    #

    class X(meta.Entity):
        p = meta.DateTime()

    naive_iso8601 = '2016-03-06T15:04:24.038691'
    utc_iso8601 = '2016-03-06T15:04:24.038691Z'
    kst_iso8601 = '2016-03-07T00:04:24.038691+09:00'

    context = meta.Context()

    assert X.p.dump(utc_naive, context) == naive_iso8601
    assert X.p.dump(utc_aware, context) == utc_iso8601
    assert X.p.dump(kst_aware, context) == kst_iso8601

    assert X.p.load(utc_iso8601, context).tzinfo is timezone.utc
    assert utc_aware == X.p.load(utc_iso8601, context)
    assert kst_aware == X.p.load(utc_iso8601, context)

    assert X.p.load(kst_iso8601, context).utcoffset() == datetime.timedelta(hours=9)
    assert utc_aware == X.p.load(kst_iso8601, context)
    assert kst_aware == X.p.load(kst_iso8601, context)


def test_time():
    class X(meta.Entity):
        p = meta.Time(format='unix')

    success = [datetime.datetime.now(), datetime.datetime.now().time(), datetime.time(), time.time(), 0, 0.0]
    failure = [datetime.date(1999, 1, 1), '한', u'한', b'\xed\x95\x9c', [1], (1,), ['a'], ('b',), entity]

    x = X()

    for value in success:
        x.p = value
        assert isinstance(x.p, datetime.time)
        x.validate()

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value
            print(value)

    timestamp = 1457276664.038691

    utc_naive = datetime.datetime(2016, 3, 6, 15, 4, 24, 38691).time()
    kst_naive = datetime.datetime(2016, 3, 7, 0, 4, 24, 38691).time()

    utc_aware = utc_naive.replace(tzinfo=timezone.utc)
    kst_aware = kst_naive.replace(tzinfo=timezone(datetime.timedelta(hours=9)))

    tod = 15 * 3600 + 4 * 60 + 24.038691

    assert X.p.dump(utc_naive) == tod
    assert X.p.dump(utc_aware) == tod
    assert X.p.dump(kst_aware) == tod

    assert X.p.load(timestamp).tzinfo is timezone.utc
    assert utc_aware == X.p.load(timestamp)

    assert X.p.load(tod).tzinfo is timezone.utc
    assert utc_aware == X.p.load(tod)

    for value in (timestamp, tod):
        x.p = value
        assert x.p == utc_aware

    x.p = utc_aware
    assert x.p == utc_aware

    x.p = kst_aware
    assert x.p == kst_aware

    x.p = utc_naive
    assert x.p == utc_naive

    #
    # iso8601
    #

    class X(meta.Entity):
        p = meta.Time()

    naive_iso8601 = '15:04:24.038691'
    utc_iso8601 = '15:04:24.038691Z'
    kst_iso8601 = '00:04:24.038691+09:00'

    context = meta.Context()

    assert X.p.dump(utc_naive, context) == naive_iso8601
    assert X.p.dump(utc_aware, context) == utc_iso8601
    assert X.p.dump(kst_aware, context) == kst_iso8601

    assert X.p.load(utc_iso8601, context).tzinfo is timezone.utc
    assert utc_aware == X.p.load(utc_iso8601, context)

    assert X.p.load(kst_iso8601, context).utcoffset() == datetime.timedelta(hours=9)
    assert kst_aware == X.p.load(kst_iso8601, context)


def test_date():
    class X(meta.Entity):
        p = meta.Date(format='unix')

    success = [datetime.datetime.now(), datetime.datetime.now().date(), time.time(), 0, 0.0]
    failure = [datetime.time(), '한', u'한', b'\xed\x95\x9c', [1], (1,), ['a'], ('b',), entity]

    x = X()

    for value in success:
        x.p = value
        assert isinstance(x.p, datetime.date)
        x.validate()

    for value in failure:
        with pytest.raises(ValueError):
            x.p = value
            print(value)

    timestamp = 1457276664.038691

    utc_naive = datetime.datetime(2016, 3, 6, 15, 4, 24, 38691)
    kst_naive = datetime.datetime(2016, 3, 7, 0, 4, 24, 38691)

    utc_aware = utc_naive.replace(tzinfo=timezone.utc)
    kst_aware = kst_naive.replace(tzinfo=timezone(datetime.timedelta(hours=9)))

    sod = timestamp - (15 * 3600 + 4 * 60 + 24.038691)
    utc_date = datetime.date(2016, 3, 6)
    kst_date = datetime.date(2016, 3, 7)

    assert X.p.dump(utc_date) == sod

    assert utc_date == X.p.load(timestamp)

    assert utc_date == X.p.load(sod)

    x.p = timestamp
    assert x.p == utc_date

    x.p = utc_aware
    assert x.p == utc_date

    x.p = kst_aware
    assert x.p == kst_date

    x.p = utc_naive
    assert x.p == utc_date

    x.p = kst_date
    assert x.p == kst_date

    x.p = utc_date
    assert x.p == utc_date

    #
    # iso8601
    #

    class X(meta.Entity):
        p = meta.Date()

    date_iso8601 = '2016-03-06'
    utc_iso8601 = '2016-03-06T15:04:24.038691Z'
    kst_iso8601 = '2016-03-07T00:04:24.038691+09:00'

    context = meta.Context()

    assert X.p.dump(utc_naive.date(), context) == date_iso8601
    assert X.p.dump(utc_aware.date(), context) == date_iso8601

    assert utc_date == X.p.load(date_iso8601, context)

    assert utc_date == X.p.load(utc_iso8601, context)

    assert kst_date == X.p.load(kst_iso8601, context)


def test_rfc822format():
    utc_naive = datetime.datetime(2016, 3, 6, 15, 4, 24)
    kst_naive = datetime.datetime(2016, 3, 7, 0, 4, 24)

    utc_aware = utc_naive.replace(tzinfo=timezone.utc)
    kst_aware = kst_naive.replace(tzinfo=timezone(datetime.timedelta(hours=9)))

    class X(meta.Entity):
        x = meta.DateTime(format='email')
        y = meta.Date(format='email')
        z = meta.Time(format='email')

    x = X()

    x.x = 'Mon, 07 Mar 2016 00:04:24 +0900'
    x.y = 'Mon, 07 Mar 2016 00:04:24 +0900'
    x.z = 'Mon, 07 Mar 2016 00:04:24 +0900'
    assert x.x == kst_aware
    assert x.y == kst_aware.date()
    assert x.z == kst_aware.timetz()
    assert x.dump()['x'] == 'Mon, 07 Mar 2016 00:04:24 +0900'
    assert x.dump()['y'] == 'Mon, 07 Mar 2016 00:00:00'
    assert x.dump()['z'] == 'Thu, 01 Jan 1970 00:04:24 +0900'

    x.x = 'Sun, 06 Mar 2016 15:04:24 GMT'
    x.y = 'Sun, 06 Mar 2016 15:04:24 GMT'
    x.z = 'Sun, 06 Mar 2016 15:04:24 GMT'
    assert x.x == utc_aware
    assert x.y == utc_aware.date()
    assert x.z == utc_aware.timetz()
    assert x.dump()['x'] == 'Sun, 06 Mar 2016 15:04:24 GMT'
    assert x.dump()['y'] == 'Sun, 06 Mar 2016 00:00:00'
    assert x.dump()['z'] == 'Thu, 01 Jan 1970 15:04:24 GMT'

    x.x = 'Sun, 06 Mar 2016 15:04:24 +0000'
    x.y = 'Sun, 06 Mar 2016 15:04:24 +0000'
    x.z = 'Sun, 06 Mar 2016 15:04:24 +0000'
    assert x.x == utc_aware
    assert x.y == utc_aware.date()
    assert x.z == utc_aware.timetz()
    assert x.dump()['x'] == 'Sun, 06 Mar 2016 15:04:24 GMT'
    assert x.dump()['y'] == 'Sun, 06 Mar 2016 00:00:00'
    assert x.dump()['z'] == 'Thu, 01 Jan 1970 15:04:24 GMT'

    x.x = 'Sun, 06 Mar 2016 15:04:24'
    x.y = 'Sun, 06 Mar 2016 15:04:24'
    x.z = 'Sun, 06 Mar 2016 15:04:24'
    assert x.x == utc_naive
    assert x.y == utc_naive.date()
    assert x.z == utc_naive.timetz()
    assert x.dump()['x'] == 'Sun, 06 Mar 2016 15:04:24'
    assert x.dump()['y'] == 'Sun, 06 Mar 2016 00:00:00'
    assert x.dump()['z'] == 'Thu, 01 Jan 1970 15:04:24'

    class X(meta.Entity):
        x = meta.DateTime(format='http')
        y = meta.Date(format='http')
        z = meta.Time(format='http')

    x = X()

    x.x = 'Mon, 07 Mar 2016 00:04:24 +0900'
    x.y = 'Mon, 07 Mar 2016 00:04:24 +0900'
    x.z = 'Mon, 07 Mar 2016 00:04:24 +0900'
    assert x.x == kst_aware
    assert x.y == kst_aware.date()
    assert x.z == kst_aware.timetz()
    assert x.dump()['x'] == 'Sun, 06 Mar 2016 15:04:24 GMT'
    assert x.dump()['y'] == 'Mon, 07 Mar 2016 00:00:00 GMT'
    assert x.dump()['z'] == 'Wed, 31 Dec 1969 15:04:24 GMT'

    x.x = 'Sun, 06 Mar 2016 15:04:24 GMT'
    x.y = 'Sun, 06 Mar 2016 15:04:24 GMT'
    x.z = 'Sun, 06 Mar 2016 15:04:24 GMT'
    assert x.x == utc_aware
    assert x.y == utc_aware.date()
    assert x.z == utc_aware.timetz()
    assert x.dump()['x'] == 'Sun, 06 Mar 2016 15:04:24 GMT'
    assert x.dump()['y'] == 'Sun, 06 Mar 2016 00:00:00 GMT'
    assert x.dump()['z'] == 'Thu, 01 Jan 1970 15:04:24 GMT'

    x.x = 'Sun, 06 Mar 2016 15:04:24 +0000'
    x.y = 'Sun, 06 Mar 2016 15:04:24 +0000'
    x.z = 'Sun, 06 Mar 2016 15:04:24 +0000'
    assert x.x == utc_aware
    assert x.y == utc_aware.date()
    assert x.z == utc_aware.timetz()
    assert x.dump()['x'] == 'Sun, 06 Mar 2016 15:04:24 GMT'
    assert x.dump()['y'] == 'Sun, 06 Mar 2016 00:00:00 GMT'
    assert x.dump()['z'] == 'Thu, 01 Jan 1970 15:04:24 GMT'

    x.x = 'Sun, 06 Mar 2016 15:04:24'
    x.y = 'Sun, 06 Mar 2016 15:04:24'
    x.z = 'Sun, 06 Mar 2016 15:04:24'
    assert x.x == utc_naive
    assert x.y == utc_naive.date()
    assert x.z == utc_naive.timetz()
    assert x.dump()['x'] == 'Sun, 06 Mar 2016 15:04:24 GMT'
    assert x.dump()['y'] == 'Sun, 06 Mar 2016 00:00:00 GMT'
    assert x.dump()['z'] == 'Thu, 01 Jan 1970 15:04:24 GMT'


@pytest.mark.skipif(PY3 and PYPY, reason='no usable ipaddress')
def test_ipaddress():
    class X(meta.Entity):
        ip = meta.IpAddress()
        ipv4 = meta.Ipv4Address()
        ipv6 = meta.Ipv6Address()

    x = X()

    x.ip = '192.168.0.1'
    assert isinstance(x.ip, ipaddress.IPv4Address)
    assert x.ip == ipaddress.IPv4Address('192.168.0.1')
    x.ipv4 = '192.168.0.1'
    assert isinstance(x.ipv4, ipaddress.IPv4Address)
    assert x.ipv4 == ipaddress.IPv4Address('192.168.0.1')

    x.ip = '::1'
    assert isinstance(x.ip, ipaddress.IPv6Address)
    assert x.ip == ipaddress.IPv6Address('::1')
    x.ipv6 = '::1'
    assert isinstance(x.ipv6, ipaddress.IPv6Address)
    assert x.ipv6 == ipaddress.IPv6Address('::1')

    with pytest.raises(ValueError):
        x.ipv4 = '::1'

    with pytest.raises(ValueError):
        x.ipv6 = '192.168.0.1'
