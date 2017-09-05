"""A setuptools based setup module.

See:
https://github.com/ONSdigital/ras-common-utils
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session='hack')

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

version = '0.0.7'

setup(
    name='ras_common_utils',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='The Common library for ONS RAS Micro-Services',
    long_description="""
    This library covers a multitude of miscellaneous routines used by micro-services
    including but not limited to, Cloud Foundry provisioning, JWT encryption, generic
    encryption, Database detection and setup, router endpoint provisioning, Swagger
    API setup, configuration file management and async reactor startup.
    """,

    # The project's main homepage.
    url='https://github.com/ONSdigital/ras-common-utils',

    # Author details
    author='RAS Development Team',
    author_email='onsdigital@linux.co.uk',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],

    # What does your project relate to?
    keywords=['micro-service', 'ons-ras'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[str(ir.req) for ir in install_reqs],
    zip_safe=False
)
