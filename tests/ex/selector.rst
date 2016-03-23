>>> class Resource(meta.Entity):
...     id = meta.String()
...
>>> class Response(meta.Entity):
...     class Options(meta.Entity.Options):
...         many = False
...
...     @meta.Selector(Resource(), Resource[:]())
...     def data(self):
...         return self.get_options().many
...
>>> resource = Resource({'id': 'article-1'})
>>> response = Response()
>>> response.data = resource
>>> response.dump()
{'data': {'id': 'article-1'}}
>>> response.data = [response]
Traceback (most recent call last):
    ...
ValueError
>>> response = Response(many=True)
>>> response.data = [resource]
>>> response.dump()
{'data': [{'id': 'article-1'}]}
>>> response.data = resource
Traceback (most recent call last):
    ...
ValueError

