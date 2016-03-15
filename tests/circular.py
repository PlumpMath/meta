from flowdas import meta


@meta.declare
class X: pass


class X(meta.Entity):
    x = X(required=True)


@meta.declare
class Child: pass


class Parent(meta.Entity):
    children = Child[:](required=True)


class Child(meta.Entity):
    parent = Parent(required=True)


@meta.declare
class Y: pass


class Z(meta.Entity):
    y = Y(required=True)
