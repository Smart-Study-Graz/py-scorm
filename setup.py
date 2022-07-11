from setuptools import setup
from setuptools import find_packages

setup(
  name='py_scorm',
  packages=find_packages(),
  install_requires=[
    'click==8.1.3',
    'lxml==4.9.1'
    ],
  include_package_data=True,
  entry_points={
    'console_scripts' : [
      'pyscorm = py_scorm.cli:execute_from_command_line',
    ]
  }
)