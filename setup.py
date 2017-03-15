from setuptools import setup

with open('requirements.txt', 'r') as f:
  lines = f.read().split('\n')

requirements = [package for package in lines if package and not package.startswith('#')]

setup(name='cassandra_migrator',
      version='0.1',
      description='cassanra migration tools',
      url='ssh://zouth@zouth.visualstudio.com:22/MarketAnywareGlobal/_git/cassandra-migrator',
      author='Pitsanu Swangpheaw',
      author_email='pitsanu_s@hotmail.com',
      license='MIT',
      packages=['migrator'],
      zip_safe=False,
      install_requires=requirements,
      scripts=['scripts/cmig']
      )
