# -*- coding: utf-8 -*-
"""
Setup for pyIntertidalDEM

@author: khan
"""

import setuptools

setuptools.setup(
    name='pyintdem',
    author='Jamal Khan',
    contributor='Nazmuddoha Ansary',
    author_email='jamal.khan@legos.obs-mip.fr',
    description='Intertidal DEM generation Package',
    packages=setuptools.find_packages(),
    license='MIT',
    setup_requires=['setuptools-git-versioning', 'setuptools_scm'],
    setuptools_git_versioning={
        "enabled": True,
        "template": "{tag}",
        "dev_template": "{tag}.post{ccount}+git.{sha}",
        "dirty_template": "{tag}.post{ccount}+git.{sha}.dirty",
        "starting_version": "1.0"
    },
    python_requires='>=3.6',
    use_scm_version=True,
    install_requires=[
        'numpy',
        'scipy',
        'gdal',
        'matplotlib',
        'basemap',
        'utide'
    ],
    include_package_data=True,
    url="https://github.com/jamal919/pyIntertidalDEM",
    long_description=open('README.md').read(),
)
