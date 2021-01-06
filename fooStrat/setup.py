from setuptools import setup

setup(name='fooStrat',
      version='0.1',
      description='Statistical analysis and strategy development for football data',
      url='https://github.com/dpopadic/fooStrat',
      author='Dario Popadic,
author_email = 'dario.popadic@yahoo.com',
               license = 'MIT',
                         packages = ['pandas',
                                     'numpy',
                                     'scipy',
                                     'sklearn',
                                     'itertools',
                                     'os',
                                     'glob',
                                     'datetime'],
                                    zip_safe = False)