>>> class X(meta.Union):
...     mono = meta.String()
...     many = meta.String[:]()
...
>>> x = X()
>>> x.mono = 'abc'
>>> x.dump()
'abc'
>>> x.many = ['abc']
>>> x.mono is None
True
>>> x.dump()
['abc']
>>> x = X().load('xyz')
>>> x.mono
'xyz'
>>> x.many is None
True
>>> x = X().load(['xyz'])
>>> x.many
('xyz',)
>>> x.mono is None
True
>>> class Y(meta.Entity):
...     x = X()
...
>>> y = Y()
>>> y.x = ['xyz']
>>> y.x.many
('xyz',)
>>> y.x.get_key()
'many'
>>> y.x.get_value()
('xyz',)
>>> y.x.get_item()
('many', ('xyz',))
