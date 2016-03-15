>>> class Rect(meta.Entity):
...     ul = meta.Complex()
...     lr = meta.Complex()
...
>>> class Shape(meta.Entity):
...     bound = Rect()
...
>>> class Circle(Shape):
...     center = meta.Complex()
...     radius = meta.Float()
...
>>> class Polygon(Shape):
...     vertices = meta.Tuple[3:](meta.Complex())
...
>>> b = Rect(dict(ul=1j, lr=1))
>>> c = Circle()
>>> c.update(bound=b, center = 0.5+0.5j, radius=0.5)
>>> pprint(c.dump())
{'bound': {'lr': (1.0, 0.0), 'ul': (0.0, 1.0)},
 'center': (0.5, 0.5),
 'radius': 0.5}
>>> Circle().load(c.dump()) == c
True
