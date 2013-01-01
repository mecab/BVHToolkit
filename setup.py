from setuptools import setup, find_packages
import sys, os

version = '0.8'

setup(name='BVHToolkit',
      version=version,
      description="An easy BVH handler for cgkit",
      long_description="""
      An easy BVH handler for cgkit
      """,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Programming Language :: Python :: 2.7",
          "Topic :: Multimedia :: Graphics :: 3D Modeling"
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='BVH cgkit',
      author='mecab',
      author_email='mecab@misosi.ru',
      url='http://misosi.ru/',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      dependency_links=[
          "http://sourceforge.net/projects/cgkit/files/cgkit/cgkit-2.0.0alpha9/"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite="BVHToolkit"
      )
