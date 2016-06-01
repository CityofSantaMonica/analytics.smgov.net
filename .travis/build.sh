#!/bin/bash

git rm -r fake-data/

bundle install --path vendor/bundle
bundle exec jekyll build
#bundle exec htmlproofer ./_site
