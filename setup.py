#!/usr/bin/env python
from codecs import open
from os import path

from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django_discovery',

    version='0.0.3',

    description='Docker service discovery for Django',
    long_description=long_description,

    url='https://github.com/formikejo/django-discovery',

    author='Yigal Duppen',
    author_email='yigal@publysher.nl',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Framework :: Django :: 1.8',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='django service-discovery docker docker-compose',

    packages=find_packages(exclude=["tests"]),

    install_requires=[
        'docker-py>=1.4.0',
        'dnspython3>=1.12.0',
        'Django>=1.8',
    ],

    test_suite="tests",
)
