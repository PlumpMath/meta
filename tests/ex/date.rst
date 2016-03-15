>>> class X(meta.Entity):
...     d1 = meta.Date()
...     d2 = meta.Date(format='%m/%d/%Y')
>>> x = X()
>>> x.d1 = '2016-03-10'
>>> x.d1
datetime.date(2016, 3, 10)
>>> x.d2 = '03/10/2016'
>>> x.d2
datetime.date(2016, 3, 10)
>>> pprint(x.dump())
{'d1': '2016-03-10', 'd2': '03/10/2016'}
