>>> import json
>>> class X(meta.Entity):
...     a = meta.Integer()
...     b = meta.Integer()
...     d = meta.Integer(ordered=True)
...     c = meta.Integer(ordered=True)
...
>>> x = X()
>>> x.update(a=1, c=meta.Null, d=4)
>>> x.dump()
OrderedDict([('d', 4), ('c', None), ('a', 1)])
>>> json.dumps(x.dump())
'{"d": 4, "c": null, "a": 1}'
>>> str(x)
'{"d":4,"c":null,"a":1}'
