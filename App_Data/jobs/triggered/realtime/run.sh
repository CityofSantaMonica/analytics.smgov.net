#!/bin/bash

export HOME="$HOME/site/wwwroot"
export ANALYTICS_KEY=$(echo -e $ANALYTICS_KEY)
export ANALYTICS_CMD="${HOME}/node_modules/analytics-reporter/bin/analytics"

cd $HOME

for envFile in envs/*.env
do
  (
    domain=$(basename $envFile)
    domain=${domain%.*}

    mkdir -p "data/$domain"

    source $envFile

    if [ "$REALTIME" = true ]
    then
      echo "Running $domain as realtime..."
      eval $ANALYTICS_CMD --output="$ANALYTICS_DATA_PATH/$domain" --frequency=realtime --verbose
    fi
  ) &

  sleep 3 # Delay the next call; Google Analytics rate limiting
done
