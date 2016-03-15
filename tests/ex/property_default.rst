>>> class X(meta.Entity):
...     a = meta.Integer(default=345)
>>> x = X()
>>> 'a' in x
False
>>> x.a
345
>>> 'a' in x
True
