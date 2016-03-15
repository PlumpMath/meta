>>> class X(meta.Entity):
...     a = meta.Integer[:]()
>>> ctx = meta.Context()
>>> ctx.errors is None
True
>>> X().load({'a': [1,2,3, 'abc']}, ctx)
Traceback (most recent call last):
    ...
ValueError
>>> ctx.errors[0].value
'abc'
>>> ctx.errors[0].location
'/a/3'
