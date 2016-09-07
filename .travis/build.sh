#!/bin/bash

git rm -r fake-data/

bundle install --path vendor/bundle
bundle exec jekyll build
#bundle exec htmlproofer ./_site

# Handle our Python setup and requirements
python --version

# Create a virtual enviornment for Python in order to store all of the necessary executables
# and libraries used by our Python scripts/project.
#
# http://docs.python-guide.org/en/latest/dev/virtualenvs/
python -m virtualenv _site/pyenv

# Install the requirements listed in this file into the virtual environment
_site/pyenv/bin/pip install -r requirements.txt