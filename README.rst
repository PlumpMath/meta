Meta: A platform-agnostic library for schema modeling
=====================================================

Meta is a platform-agnostic library for defining, serializing, and validating data structures.

.. code-block:: python

    from flowdas import meta

    class Author(meta.Entity):
       name = meta.String()

    class Book(meta.Entity):
       title = meta.String()
       published = meta.Date()
       authors = Author[1:]()

    author1 = Author({'name': 'O'})
    author2 = Author()
    author2.update(name = 'Flowdas')
    book = Book()
    book.title = 'Meta'
    book.published = '2016-03-15'
    book.authors = [author1, author2]
    book.published
    # datetime.date(2016, 3, 15)
    book.validate()
    book.dump()
    # {'authors': [{'name': 'O'}, {'name': 'Flowdas'}], 'published': '2016-03-15', 'title': 'Meta'}

Install
=======

::

    pip install flowdas-meta==1.0.0a1

Meta requires Python 2.7, 3.3, 3.4, or 3.5. It also supports PyPy. There is no external dependencies.

Feature Highlights
==================

- `Polymorphic Type Hierarchy <http://flowdas.github.io/meta/inheritance.html>`_
- `Union <http://flowdas.github.io/meta/union.html>`_
- `Generalized Tuple <http://flowdas.github.io/meta/tuple.html>`_
- `Simplified Nesting <http://flowdas.github.io/meta/nesting.html>`_

Documentation
=============

Documentation is available at http://flowdas.github.io/meta/.

