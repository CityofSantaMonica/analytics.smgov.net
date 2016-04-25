#!/bin/bash

export HOME="$HOME/site/wwwroot"
export ANALYTICS_KEY=$(echo -e $ANALYTICS_KEY)

cd $HOME

ANALYTICS_CMD="${HOME}/node_modules/analytics-reporter/bin/analytics"

for envFile in "envs/*.env"
do
	domain=$(basename $envFile)
	domain=${domain%.*}

	mkdir -p "data/$domain"

	source $envFile
	eval $ANALYTICS_CMD --output="data/$domain" --frequency=realtime --slim --verbose
	eval $ANALYTICS_CMD --output="data/$domain" --only=all-pages-realtime --slim --verbose --csv
done
