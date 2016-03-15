>>> class X(meta.Entity):
...     positive = meta.Integer(validate=lambda x: x > 0)
>>> x = X()
>>> x.positive = 1
>>> x.positive = -1
Traceback (most recent call last):
    ...
ValueError

