# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="matrix-nio",
    version="0.1",
    url="https://github.com/poljar/matrix-nio",
    author='Damir Jelić',
    author_email="poljar@termina.org.uk",
    description=("A Python Matrix client library, designed according to sans"
                 "I/O principles."),
    license="ISC",
    packages=find_packages(),
    install_requires=[
        "attrs",
        "future",
        "peewee",
        "typing;python_version<'3.5'",
        "h11",
        "h2",
        "logbook",
        "jsonschema",
        "atomicwrites",
        "unpaddedbase64",
        "pycrypto",
        "python-olm @ git+https://github.com/poljar/python-olm.git@master#egg=python-olm-0"
    ],
    zip_safe=False
)
