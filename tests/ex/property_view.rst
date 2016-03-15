>>> class X(meta.Entity):
...     anyone = meta.Integer()
...     user = meta.Integer(view=['user', 'staff'])
...     staff = meta.Integer(view='staff')
>>> x = X(dict(anyone=0, user=1, staff=2))
>>> pprint(x.dump())
{'anyone': 0, 'staff': 2, 'user': 1}
>>> pprint(x.dump(meta.Context()))
{'anyone': 0, 'staff': 2, 'user': 1}
>>> pprint(x.dump(meta.Context(view='user')))
{'anyone': 0, 'user': 1}
>>> pprint(x.dump(meta.Context(view='staff')))
{'anyone': 0, 'staff': 2, 'user': 1}
