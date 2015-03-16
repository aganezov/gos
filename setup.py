# -*- coding: utf-8 -*-
__author__ = "aganezov"

from setuptools import setup

from gos import version as gos_version

setup(
    name="gos",
    version=gos_version,
    packages=["gos"],
    install_requires=list(map(lambda entry: entry.strip(), open("requirements.txt", "rt").readlines())),
    author="Sergey Aganezov",
    author_email="aganezov@gwu.edu",
    description="Gene order based scaffolding tool for multiple genomes",
    license="GPLv3",
    keywords=["breakpoint graph", "data structures", "python", "scaffolding", "gene order"],
    url="https://github.com/sergey-aganezov-jr/gos",
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)