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
	analytics --output="data/$domain" --frequency=realtime --slim --verbose
	#analytics --output="data/$domain" --only=all-pages-realtime --slim --verbose --csv
done
