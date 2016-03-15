>>> class X(meta.Entity):
...     a = meta.Integer(required=True)
>>> x = X()
>>> x.a = None
Traceback (most recent call last):
    ...
ValueError
>>> x.a = 123
>>> del x.a
>>> x.a is None
True
