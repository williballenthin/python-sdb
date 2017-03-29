#!/usr/bin/env python
from setuptools import setup, find_packages

# For Testing:
#
# python3.4 setup.py register -r https://testpypi.python.org/pypi
# python3.4 setup.py bdist_wheel upload -r https://testpypi.python.org/pypi
# python3.4 -m pip install -i https://testpypi.python.org/pypi
#
# For Realz:
#
# python3.4 setup.py register
# python3.4 setup.py bdist_wheel upload
# python3.4 -m pip install

setup(
    name='python-sdb',
    version='0.1',
    description='Pure Python parser for Application Compatibility Shim Databases (.sdb files)',
    author='Willi Ballenthin',
    author_email='willi.ballenthin@gmail.com',
    url='https://github.com/williballenthin/python-sdb',
    license='Apache License 2.0',
    install_requires=[
        "hexdump",
        "vivisect-vstruct-wb>=1.0.3"
    ],
    packages=find_packages(exclude=['*.tests','*.tests.*']),
    entry_points={
        "console_scripts": [
            "sdb_dump_database=scripts.sdb_dump_database:main",
            "sdb_dump_raw=scripts.sdb_dump_raw:main",
            "sdb_dump_shims=scripts.sdb_dump_shims:main",
            "sdb_dump_info=scripts.sdb_dump_info:main",
        ]
      },

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
    ],

)
