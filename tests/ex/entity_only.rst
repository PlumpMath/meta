>>> class Identifier(meta.Entity):
...     type = meta.Kind()
...     id = meta.String()
...
>>> class Resource(Identifier):
...     related = Identifier(only=['type', 'id'])
...
>>> class Book(Resource):
...     type = 'book'
...
>>> class Author(Resource):
...     type = 'author'
...
>>> book = Book(dict(id='9788932909059'))
>>> author = Author(dict(id='1234567', related=book))
>>> book.related = author
>>> pprint(book.dump())
{'id': '9788932909059',
 'related': {'id': '1234567', 'type': 'author'},
 'type': 'book'}
>>> pprint(author.dump())
{'id': '1234567',
 'related': {'id': '9788932909059', 'type': 'book'},
 'type': 'author'}
