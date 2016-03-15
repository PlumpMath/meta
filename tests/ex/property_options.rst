>>> class Natural(meta.Integer):
...     class Options(meta.Integer.Options):
...         multipleof = None
...         def validate(self, value):
...             return value > 0 and (self.multipleof is None or value % self.multipleof == 0)
...
>>> class X(meta.Entity):
...     n = Natural(multipleof = 3)
>>> x = X()
>>> x.n = 3
>>> x.n = -3
Traceback (most recent call last):
    ...
ValueError
>>> x.n = 1
Traceback (most recent call last):
    ...
ValueError
