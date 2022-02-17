from setuptools import setup
from setuptools import find_packages

def _find_packages():
    packages = find_packages(where='.')
    #packages.append('py_scorm.data')
    return packages

setup(
  name='py_scorm',
  packages=_find_packages(),
  install_requires=[
    ],
  # package_data={
  #   'py_scorm': ['py_scorm/data/scorm_12/*']
  # },
  include_package_data=True,
  # package_dir={
  #           'py_scorm.data': 'data',
  #       },
)