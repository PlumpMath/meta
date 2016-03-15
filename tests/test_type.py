import pytest
from flowdas.meta.type import TypeMeta, Type


def test_type():
    class X(Type):
        @staticmethod
        def _init_(cls, attrs, options):
            Type._init_(cls, attrs, options)
            cls.x = 789

        @classmethod
        def _getitem_(cls, key):
            return key

    assert isinstance(X, TypeMeta)
    assert issubclass(X, Type)
    assert type(X) == TypeMeta
    assert X.__name__ == 'X'
    assert X.__bases__ == (Type,)
    assert X.__module__ == 'tests.test_type'
    assert X.x == 789
    assert X[:] == slice(None)

    x = X()
    with pytest.raises(TypeError):
        _ = x[:]

    class Y(Type):
        pass

    with pytest.raises(TypeError):
        _ = Y[:]


def test_meta_options():
    class X(Type):
        class MetaOptions(Type.MetaOptions):
            x = 789

        @staticmethod
        def _init_(cls, attrs, options):
            Type._init_(cls, attrs, options)
            cls.options = options

    assert isinstance(X.options, X.MetaOptions)
    assert X.options.x == 789
    assert X.options.__dict__ == {}

    class Y(X):
        class Meta:
            x = 123

    assert X.MetaOptions is Y.MetaOptions
    assert isinstance(Y.options, X.MetaOptions)
    assert Y.options.x == 123
    assert Y.options.__dict__ == {'x': 123}
