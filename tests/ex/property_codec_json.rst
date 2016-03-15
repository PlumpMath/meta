>>> class X(meta.Entity):
...     a = meta.JsonObject()
>>> x = X(codec='json')
>>> x.a = {'x':1, 'y':[]}
>>> pprint(x.dump())
{'a': {'x': 1, 'y': []}}
>>> x.dump(meta.Context())
'{"a":{"y":[],"x":1}}'
