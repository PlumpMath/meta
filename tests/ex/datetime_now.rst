>>> class Resource(meta.Entity):
...     created = meta.DateTime(default=meta.DateTime.now)
>>> Resource().dump()
{'created': '2016-03-10T07:54:07.923184Z'}
