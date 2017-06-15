SHELL:=/bin/bash

prod:
	bundle exec jekyll build

dev:
	bundle exec jekyll serve --config=_config.yml,_configdev.yml --host=0.0.0.0

aggregate:
	python App_Data/jobs/triggered/aggregate/job.py data

# All `fetch-*` commands rely on the `analytics.private` file which should
# export the following variables:
#  - ANALYTICS_CMD
#  - ANALYTICS_DATA_PATH
#  - ANALYTICS_REPORT_EMAIL
#  - ANALYTICS_REPORTS_PATH
#  - ANALYTICS_KEY
fetch:
	source analytics.private; \
	for envFile in _site/envs/*.env; do \
		domain=$$(basename $$envFile); \
		domain=$${domain%.*}; \
		mkdir -p "data/$$domain"; \
		echo "--- Start $$domain ---"; \
		source $$envFile; \
		eval $$ANALYTICS_CMD --output="$$ANALYTICS_DATA_PATH/$$domain" --frequency=daily --verbose; \
		eval $$ANALYTICS_CMD --output="$$ANALYTICS_DATA_PATH/$$domain" --frequency=hourly --verbose; \
    if [ "$$REALTIME" = true ]; then \
    echo "Treating $$domain as realtime..."; \
		eval $$ANALYTICS_CMD --output="$$ANALYTICS_DATA_PATH/$$domain" --frequency=realtime --verbose; \
    unset REALTIME; \
    fi; \
		echo "--- End $$domain ---"; \
		sleep 3; done

fetch-all: fetch aggregate