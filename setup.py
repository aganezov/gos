# -*- coding: utf-8 -*-
__author__ = "aganezov"

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name="gos",
      version="0.1.3",
      packages=["gos", "tests", "gos.utils",
                "gos.algo", "gos.algo.executable_containers"],
      author="Sergey Aganezov",
      author_email="aganezov@cs.jhu.edu",
      description="Generically organizable supervisor to create multi-level executable pipelines",
      license="MIT",
      keywords=["pipeline", "data structures", "python"],
      url="https://github.com/aganezov/gos",
      classifiers=[
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License"
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5'
      ]
      )
