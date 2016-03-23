# coding=utf-8
from __future__ import print_function

import doctest
import glob
from pprint import pprint

import os
import pytest
from flowdas import meta
from flowdas.meta.compat import *

EX = os.path.join(os.path.dirname(__file__), 'ex')


def get_names(pattern):
    return map(lambda x: os.path.splitext(os.path.basename(x))[0], glob.glob(os.path.join(EX, pattern)))


@pytest.mark.parametrize('name', get_names('*.py'))
def test_py(name):
    with open(os.path.join(EX, name + '.py')) as f:
        code = compile(f.read(), name + '.py', 'exec')
        exec (code, globals(), locals())


@pytest.mark.parametrize('name', get_names('*.rst'))
def test_rst(name):
    failure_count, test_count = doctest.testfile(os.path.join(EX, name + '.rst'),
                                                 globs={'meta': meta, 'pprint': pprint}, module_relative=False)
    if name in ('datetime_now', 'property_codec_json'):
        return
    if name == 'codec' and PY2:
        return
    assert failure_count == 0

GUIDE = os.path.join(os.path.dirname(__file__), '../docs')

@pytest.mark.parametrize('name', [
    'quickstart',
    'tuple',
    'nesting',
    'union',
    'inheritance',
    'serialization',
])
def test_guide(name):
    failure_count, test_count = doctest.testfile(os.path.join(GUIDE, name + '.rst'),
                                                 globs={'meta': meta, 'pprint': pprint}, module_relative=False)
    assert failure_count == 0
