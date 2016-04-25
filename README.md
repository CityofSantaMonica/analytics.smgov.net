# analytics.smgov.net [![Build Status](https://travis-ci.org/CityofSantaMonica/analytics.smgov.net.svg?branch=master)](https://travis-ci.org/CityofSantaMonica/analytics.smgov.net)

A project to publish website analytics for the City of Santa Monica.

Based on the [original](https://github.com/18F/analytics.usa.gov) by
[18F](https://github.com/18F).

Other government agencies who have reused this project for their analytics dashboard:
* [U.S. Federal Government](https://analytics.usa.gov/)
* [Tennessee Department of Environment & Conservation](http://analytics.tdec.tn.gov/)
* [City of Boulder](https://bouldercolorado.gov/stats)
* [City of Philadelphia](http://analytics.phila.gov/)
* [City of Sacramento](http://analytics.cityofsacramento.org)

## Developing

Ths app uses [Jekyll](http://jekyllrb.com) to build the site, and [Sass](http://sass-lang.com/),
[Bourbon](http://bourbon.io), and [Neat](http://neat.bourbon.io) for CSS.

Install them all:

```bash
bundle install
```

To run locally:

```bash
bundle exec jekyll serve --watch --config _config.yml,_configdev.yml
```

The development settings assume data is available at `/fake-data`. You can change this in `_configdev.yml`.

[`analytics-reporter`](https://github.com/18F/analytics-reporter) is the code that powers the dashboard by pulling data from Google Analytics.

## Deploying

18F's original [analytics dashboard](https://github.com/18F/analytics.usa.gov) was written with a Linux environment and [18F pages](https://github.com/18F/pages) in mind. For this project, we've ported 18F's work into an [Azure Web App](https://azure.microsoft.com/en-us/services/app-service/web/).

This fork has both the Jekyll website and node app (`analytics-reporter`) deployed to a single Azure Web App; everything remains on the same domain and in one place. Travis is being used to compile the Jekyll website and then deploy it to Azure.

Create an [issue](https://github.com/CityofSantaMonica/analytics.smgov.net/issues) or send us a [pull request](https://github.com/CityofSantaMonica/analytics.smgov.net/pulls) on how to improve these notes for deploying to Azure, asking questions, or improving our process.

### Polling Google Analytics

18F provides us with bash scripts and `cron` jobs but they aren't very generic or Azure friendly, so we make use of [Azure WebJobs](https://azure.microsoft.com/en-us/documentation/articles/websites-dotnet-deploy-webjobs/). The `cron` jobs were easily ported over to [Azure's syntax](https://azure.microsoft.com/en-us/documentation/articles/web-sites-create-web-jobs/#CreateScheduledCRON).

WebJobs are placed in `App_Data/jobs/<triggered|continuous>` and each WebJob belongs in its own folder (the name of the folder is arbitrary). By adding a `run.sh` and a `settings.job` file in the folder, the `run.sh` will be executed based on the schedule defined by the `cron` expression located in `settings.job`.

### Configuring Travis

Travis CI can automatically [deploy to Azure after a successful build](https://docs.travis-ci.com/user/deployment/azure-web-apps) and have the following environment variables set:

- `AZURE_WA_USERNAME` - The Git/Deployment username located in the portal
- `AZURE_WA_PASSWORD` - The password of the above user; also located in the portal
- `AZURE_WA_SITE` - The name of the actual Web App

#### Setting Up Our Scripts

Here's what our `.travis.yml` file looks like

```yaml
language: ruby
cache: bundler
rvm:
  - 2.2
script:
  - bash .travis/build.sh
before_deploy:
  - bash .travis/pre-deploy.sh
deploy:
  provider: azure_web_apps
env:
  global:
    - NOKOGIRI_USE_SYSTEM_LIBRARIES=true

```

We are calling two separate scripts for Travis to execute. The first script is the `.build.sh` script which actually builds the Jekyll website.

> In our case, we have a "fake-data" folder for development so we remove that before we build the final website.

Our second script (`pre-deploy.sh`) is called before we deploy everything to Azure. Content is deployed to Azure via Git, which means that `.gitignore` will be respected and our `_site` won't be deployed to Azure. To fix this, our pre-deploy script will give Travis an identity for git, forcefully add the `_site` directory, and amend the commit we were just building. By amending the previous commit, the commit message and author stay intact when being viewed from the Azure portal.

```bash
git config user.name "travis-ci"
git config user.email "travis@localhost"
git add -f _site/
git commit --amend --no-edit
```

### Setting Up Azure

18F [specifies what environment variables](https://github.com/18F/analytics-reporter#setup) are needed in `.env` files. Instead of placing all of them in `.env` files and worry about sensitive information or repetition, we store them as Azure Application Settings.

- `ANALYTICS_REPORT_EMAIL` - `example@analytics.iam.gserviceaccount.com`
- `ANALYTICS_REPORTS_PATH` - `reports/your-reports.json`
- `ANALYTICS_KEY` - Copy the `private_key` value from the Google Analytics json file. Keep the `\n` in there and do **not** expand it; the bash scripts will take care of that.

### Configuring Kudu

Now that we have our already-built Jekyll site **and** our web jobs to poll Google Analytics, we have [Kudu](https://github.com/projectkudu/kudu) copy over the '\_site' folder (as specified by `DEPLOYMENT_SOURCE`).

```
[config]
DEPLOYMENT_SOURCE = _site
COMMAND = bash .kudu/deploy.sh
```

Kudu will copy over our `App_Data` and `env` folders to `site\wwwroot` because that's where they belong.

## Public Domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
