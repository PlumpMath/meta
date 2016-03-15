# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup_requires = [
]

install_requires = [
]

tests_require = [
]

dependency_links = [
]

setup(
    name='flowdas-meta',
    version=open('VERSION').read().strip(),
    url='https://github.com/flowdas/meta',
    description='Meta: A platform-agnostic library for schema modeling.',
    author=u'오동권(Dong-gweon Oh)',
    author_email='prospero@flowdas.com',
    license='MPL 2.0',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['flowdas'],
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    dependency_links=dependency_links,
    scripts=[],
    entry_points={
        'console_scripts': [
        ],
    },
    zip_safe=True,
    keywords=('schema', 'model', 'entity', 'serealization', 'validation'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
