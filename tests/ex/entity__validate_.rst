>>> import datetime
...
>>> class Period(meta.Entity):
...     begin = meta.DateTime()
...     end = meta.DateTime()
...
...     def _validate_(self, context):
...         begin = self.get_if_visible('begin', context)
...         end = self.get_if_visible('end', context)
...
...         if begin is not None and end is not None:
...             return begin <= end
...         return True
...
>>> p = Period()
>>> p.begin = meta.DateTime.now()
>>> p.end = p.begin + datetime.timedelta(hours=1)
>>> ctx = meta.Context()
>>> p.validate(ctx)
>>> p.end = p.begin - datetime.timedelta(hours=1)
>>> p.validate(ctx)
Traceback (most recent call last):
    ...
ValueError
>>> ctx.errors
[ValueError()]
