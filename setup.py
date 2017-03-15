from setuptools import setup

with open('requirements.txt', 'r') as f:
  lines = f.read().split('\n')

requirements = [package for package in lines if package and not package.startswith('#')]

setup(name='cassandra_migrator',
      version='0.1.001',
      description='cassanra migration tools',
      url='https://github.com/webscal3r/cassandra-migrator.git',
      author='Pitsanu Swangpheaw',
      author_email='pitsanu_s@hotmail.com',
      license='MIT',
      packages=['migrator'],
      zip_safe=False,
      install_requires=requirements,
      scripts=['scripts/cmig'],
      data_files=[('.', ['requirements.txt'])]
      )
