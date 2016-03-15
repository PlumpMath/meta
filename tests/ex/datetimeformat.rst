>>> import datetime
>>> @meta.DateTimeFormat.register('aprilfool')
... class AprilFoolFormat(meta.DateTimeFormat):
...     def format(self, value, property, context):
...         return '2016-04-01'
...     def parse(self, value, property, context):
...         dt = datetime.datetime(2016, 4, 1)
...         if property is meta.Date:
...             return dt.date()
...         elif property is meta.Time:
...             return dt.time()
...         else:
...             return dt
>>> class X(meta.Entity):
...     d = meta.DateTime(format='aprilfool')
>>> x = X()
>>> x.d = 4567
>>> x.d
datetime.datetime(2016, 4, 1, 0, 0)
>>> x.dump()
{'d': '2016-04-01'}
