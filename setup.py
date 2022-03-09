from setuptools import setup
from setuptools import find_packages

setup(
  name='py_scorm',
  packages=find_packages(),
  install_requires=[
    'click'
    ],
  include_package_data=True,
  entry_points={
    'console_scripts' : [
      'pyscorm = py_scorm.cli:execute_from_command_line',
    ]
  }
)