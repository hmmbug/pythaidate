# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='pythaidate',
    version='0.0.1',
    description='pythaidate',
    # long_description=open('README.md').read(),
    author='Mark Hollow',
    author_email='mark@markhollow.com',
    url='https://github.com/hmmbug/pythaidate',
    license=open('LICENSE').read(),
    packages=find_packages(exclude=('tests', 'docs'))
)
