#!/bin/bash
# ##########################################################################
# Author: txu
# Brief:  Upload tlib to pypi
#
# Returns:
#   pass: 0
#   fail: not 0
# ##########################################################################

# pip install wheel
# pip install twine
# python setup.py check

rm -rf ./build ./pytest_flexreport.egg-info ./dist
python setup.py sdist bdist_wheel
twine upload  dist/*