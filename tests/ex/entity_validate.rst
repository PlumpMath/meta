>>> class X(meta.Entity):
...    a = meta.Integer(required=True)
...    b = meta.Integer()
...
>>> class Y(meta.Entity):
...     x = X(required=True)
...     c = meta.Integer()
...
>>> ctx = meta.Context()
>>> y = Y().load({'x': {'b': 2}}, ctx)
>>> y.validate(ctx)
Traceback (most recent call last):
    ...
ValueError
>>> ctx.errors
[ValueError(/x/a)]
