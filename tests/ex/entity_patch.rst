>>> class X(meta.Entity):
...     a = meta.Integer(required=True)
...     b = meta.Integer()
...
>>> x1 = X(dict(a=1, b=2))
>>> x2 = X(dict(a=3))
>>> delta = x1 ^ x2
>>> pprint(delta.dump())
{'a': 1, 'b': 2}
>>> x3 = x2.patch(delta)
>>> pprint(x3.dump())
{'a': 1, 'b': 2}
>>> x3 == x1
True
>>> delta = x2 ^ x1
>>> pprint(delta.dump())
{'a': 3, 'b': None}
>>> x3 = x1.patch(delta)
>>> x3.dump()
{'a': 3}
>>> x3 == x2
True
