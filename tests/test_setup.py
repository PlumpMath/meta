import os
from flowdas import meta


def test_version():
    VERSION = os.path.join(os.path.dirname(__file__), '../VERSION')
    assert meta.__version__ == open(VERSION).read().strip()
