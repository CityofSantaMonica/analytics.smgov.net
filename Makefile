DEPLOY_BUCKET=18f-dap

production:
	bundle exec jekyll build

dev:
	bundle exec jekyll serve --watch --config=_config.yml,_development.yml

deploy:
	make production
