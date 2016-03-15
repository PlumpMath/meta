>>> class X(meta.Entity):
...     defined = None
...     class Meta:
...         freeze = True
>>> x = X()
>>> x.defined = 1
>>> x.undefined = 1
Traceback (most recent call last):
    ...
AttributeError: undefined
