#!/bin/bash

git rm -r fake-data/

bundle install
bundle exec jekyll build
bundle exec htmlproofer ./_site