>>> class X(meta.Entity):
...     klass = meta.String(name='class')
>>> x = X(dict(klass='A1'))
>>> x.dump()
{'class': 'A1'}
