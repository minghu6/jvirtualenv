# -*- coding:utf-8 -*-
"""Setup file"""
import os
import re
import codecs
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()
with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()


def find_version():
    here = os.path.abspath(os.path.dirname(__file__))
    there = os.path.join(here, 'jvirtualenv', '__main__.py')

    version_file = codecs.open(there, 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)

    else:
        raise RuntimeError("Unable to find version string.")


__version__ = find_version()

setup(
    name='jvirtualenv',
    version=__version__,
    packages=find_packages(),
    install_requires=REQUIRED,
    entry_points={
        'console_scripts': ['jvirtualenv=jvirtualenv.__main__:cli'],
    },
    include_package_data=True,
    license='BSD License',
    description='micro virtualenv for Java',
    long_description=README,
    url='https://github.com/minghu6/jvirtualenv',
    author='minghu6',
    author_email='a19678zy@163.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation',
    ],
)
