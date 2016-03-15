>>> class X(meta.Entity):
...     a = meta.JsonObject()
...     b = meta.JsonObject()
>>> x = X(codec=meta.codec('json', sort_keys=True))
>>> x.a = {'x':1, 'y':[]}
>>> x.b = {'x':1, 'y':[]}
>>> x.dump(meta.Context())
'{"a":{"x":1,"y":[]},"b":{"x":1,"y":[]}}'
