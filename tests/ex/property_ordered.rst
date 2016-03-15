>>> class Array(meta.Union):
...     point = meta.Tuple(meta.Integer(), meta.Integer(), ordered=True)
...     other = meta.JsonArray(ordered=True)
>>> x = Array().load([1,2])
>>> x.point
(1, 2)
>>> x.other is None
True
>>> x = Array().load([1,2,3])
>>> x.point is None
True
>>> x.other
[1, 2, 3]
