>>> class Base(meta.Entity):
...     type = meta.Kind('base')
...
>>> class Derived(Base):
...     type = 'derived'
...     d = meta.Integer()
...
>>> class X(meta.Entity):
...     b = Base()
...
>>> x = X()
>>> x.b = Base()
>>> x.dump()
{'b': {'type': 'base'}}
>>> x.b = Derived(dict(d=123))
>>> pprint(x.dump())
{'b': {'d': 123, 'type': 'derived'}}
>>> x = X().load({'b':{'type': 'derived', 'd': 789}})
>>> isinstance(x.b, Derived)
True
>>> pprint(x.dump())
{'b': {'d': 789, 'type': 'derived'}}
