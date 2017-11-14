#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(os.path.join(here, "ras_common_utils", "__version__.py")) as f:
    exec(f.read(), about)

required = [
    'Flask>=0.12.2',
    'PyYAML>=3.12',
    'SQLAlchemy>=1.1.10',
    'structlog>=17.2.0',
    'zest.releaser[recommended]'
]

setup(
    name='ras_common_utils',
    version=about['__version__'],
    description='The Common library for ONS RAS Micro-Services.',
    long_description=long_description,
    url='https://github.com/ONSdigital/ras-common-utils',
    author='RAS Development Team',
    author_email='onsdigital@linux.co.uk',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords=['micro-service', 'ons-ras'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=required,
    zip_safe=False
)
