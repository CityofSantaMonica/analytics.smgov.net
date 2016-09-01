#!/bin/bash

git rm -r fake-data/

bundle install --path vendor/bundle
bundle exec jekyll build
#bundle exec htmlproofer ./_site

# Get our Python dependencies
python --version
python -m virtualenv _site/pyenv
_site/pyenv/bin/pip install -r requirements.txt