>>> class X(meta.Entity):
...    a = meta.Integer()
>>> x = X()
>>> x.a is None
True
>>> x.dump()
{}
>>> x.a = meta.Null
>>> x.a
Null
>>> x.a is None
False
>>> x.dump()
{'a': None}
>>> x.a = None
>>> x.dump()
{}
