#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013 Tomasz Wójcik <tomek@bthlabs.pl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import codecs
from setuptools import setup

import envelopes

desc_file = codecs.open('README.rst', 'r', 'utf-8')
long_description = desc_file.read()
desc_file.close()

setup(
    name="Envelopes",
    version=envelopes.__version__,
    packages=['envelopes'],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    tests_require=[
        'nose',
    ],
    author=u'Tomasz Wójcik'.encode('utf-8'),
    author_email='tomek@bthlabs.pl',
    maintainer=u'Tomasz Wójcik'.encode('utf-8'),
    maintainer_email='tomek@bthlabs.pl',
    url='http://tomekwojcik.github.io/envelopes/',
    download_url='http://github.com/tomekwojcik/envelopes/tarball/v%s' %\
        envelopes.__version__,
    description='Mailing for human beings',
    long_description=long_description,
    license='https://github.com/tomekwojcik/envelopes/blob/master/LICENSE',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
