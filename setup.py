from setuptools import setup
from setuptools import find_packages

setup(
  name='py_scorm',
  packages=find_packages('.'),
  install_requires=[
    ],
  package_data={
    'py_scorm': ['data/*']
  }
)