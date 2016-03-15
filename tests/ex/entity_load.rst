>>> class X(meta.Entity):
...     a = meta.Integer()
...     b = meta.Integer()
...     c = meta.Integer()
...
>>> x = X().load({"d": 4, "c": None, "a": 1})
>>> pprint(x.dump())
{'a': 1, 'c': None}
>>> x.b is None
True
>>> x.c is meta.Null
True
>>> x = X().load({"d": 4, "c": None, "a": 1}, meta.Context(strict=True))
Traceback (most recent call last):
    ...
ValueError
