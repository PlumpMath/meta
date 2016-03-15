>>> from flowdas import meta
>>> from pprint import pprint
...
>>> class Author(meta.Entity):
...    name = meta.String()
...
>>> class Book(meta.Entity):
...    title = meta.String()
...    published = meta.Date()
...    authors = Author[1:]()
...
>>> author1 = Author({'name': 'O'})
>>> author2 = Author()
>>> author2.update(name = 'Flowdas')
>>> book = Book()
>>> book.title = 'Meta'
>>> book.published = '2016-03-15'
>>> book.authors = [author1, author2]
>>> book.published
datetime.date(2016, 3, 15)
>>> book.validate()
>>> pprint(book.dump())
{'authors': [{'name': 'O'}, {'name': 'Flowdas'}],
 'published': '2016-03-15',
 'title': 'Meta'}
