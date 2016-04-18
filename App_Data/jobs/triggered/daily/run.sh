#!/bin/bash

export HOME="$HOME/site/wwwroot"
export ANALYTICS_KEY=$(echo -e $ANALYTICS_KEY)

cd $HOME

for envFile in "envs/*.env"
do
	domain=$(basename $envFile)
	domain=${domain%.*}

	mkdir -p "data/$domain"

	source $envFile
	analytics --output="data/$domain" --frequency=daily --slim --verbose
	analytics --output="data/$domain" --frequency=daily --slim --verbose --csv
done
