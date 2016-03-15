>>> class ProtectedEntity(meta.Entity):
...     class MetaOptions(meta.Entity.MetaOptions):
...         freeze = True
>>> class X(ProtectedEntity):
...     pass
>>> x = X()
>>> x.undefined = 1
Traceback (most recent call last):
    ...
AttributeError: undefined
