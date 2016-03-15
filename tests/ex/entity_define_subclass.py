class Declarative(meta.Entity):
    a = meta.Integer()

Imperative = meta.Entity.define_subclass('Imperative', {'a': meta.Integer()})
