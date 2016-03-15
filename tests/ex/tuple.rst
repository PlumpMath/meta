>>> class X(meta.Entity):
...     pair = meta.Tuple(meta.Integer(), meta.Integer())
...     ints = meta.Integer[:](required=True)
...
>>> x = X()
>>> x.pair = [1,2]
>>> x.pair
(1, 2)
>>> x.ints = list(range(10))
>>> x.ints
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
>>> x.pair = []
Traceback (most recent call last):
    ...
ValueError: length mismatch
>>> x.ints = []
>>> x.pair = [1, None]
>>> x.ints = [1, None]
Traceback (most recent call last):
    ...
ValueError
