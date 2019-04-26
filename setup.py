# -*- coding: utf-8 -*-
"""
Setup for pyIntertidalDEM

@author: khan
"""

import setuptools

setuptools.setup(
    name='pyIntertidalDEM',
    version='3.0',
    author='Jamal Khan',
    contributor='Nazmuddoha Ansary',
    author_email='jamal.khan@legos.obs-mip.fr',
    description='Intertidal DEM generation Package',
    packages=setuptools.find_packages(),
    license='MIT',
    install_requires=[
        'numpy',
        'scipy',
        'osgeo',
        'matplotlib',
        'basemap',
        'zipfile',
        'utide',
        'csv',
        'glob',
        'gc'
    ],
    include_package_data=True,
    url="https://github.com/jamal919/pyIntertidalDEM",
    long_description=open('README.md').read(),
)