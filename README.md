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

## Reporting

The report definitions are JSON objects defined inside of a `reports` JSON array. In this repository, the report definitions are stored inside of the `reports` folder.

```
{
  "reports": [
    {
      "name": "report-name",
      "frequency": "daily",
      "query": {
        "dimensions": [ "ga:pagePath", "ga:pageTitle" ],
        "metrics": [ "ga:sessions" ],
        "start-date": "yesterday",
        "end-date": "today"
      },
      "meta": {
        "name": "Dummy Report",
        "description": "Sample report definition to show the structure of a report"
      }
    }
  ]
}
```

### JSON Object Structure

- `name` - The name of the report, this will be the resulting file name for the reports
- `frequency` - Corresponds to the `--frequency` command line option. This option does **not** automagically create cron jobs; separate cron jobs or WebJobs are required.
- `query`
  - `dimensions` & `metrics` - Valid values can be found in the [Google Analytics Docs](https://developers.google.com/analytics/devguides/reporting/core/dimsmets)
  - `start-date` or `end-date` - Time period for the report
    - `today`
    - `yesterday`
    - `7daysAgo`
    - `30daysAgo`
    - `90daysAgo`

## Deploying

18F's original [analytics dashboard](https://github.com/18F/analytics.usa.gov) was written with a Linux environment and [18F pages](https://github.com/18F/pages) in mind. For this project, we've ported 18F's work into an [Azure Web App](https://azure.microsoft.com/en-us/services/app-service/web/).

This fork has both the Jekyll website and node app (`analytics-reporter`) deployed to a single Azure Web App; everything remains on the same domain and in one place. Travis is being used to compile the Jekyll website and then deploy it to Azure.

Create an [issue](https://github.com/CityofSantaMonica/analytics.smgov.net/issues) or send us a [pull request](https://github.com/CityofSantaMonica/analytics.smgov.net/pulls) on how to improve these notes for deploying to Azure, asking questions, or improving our process.

### Configuring Travis

Travis CI can automatically [deploy to Azure after a successful build](https://docs.travis-ci.com/user/deployment/azure-web-apps) and have the following environment variables set:

- `AZURE_WA_SITE` - The name of the actual Web App
- `AZURE_WA_USERNAME` - The Git/Deployment username located in the portal
- `AZURE_WA_PASSWORD` - The password of the above user
  - **Heads up!** Travis sends this password in the remote URL (i.e. `https://user:password@domain.com/repo.git`), so be careful with special characters in your passwords.

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

All of the scripts available have a custom `$HOME` which is set to: `D:\home\site\wwwroot`. All of the paths defined in Azure Application Settings or environment variables should be **relative** to the custom `$HOME` directory; do **not** use absolute paths.

#### Google Analytics

- `ANALYTICS_REPORT_EMAIL` - The email used for your Google developer account; this account is automatically generated for you by Google. This account should have access to the appropriate profiles in Google Analytics.

    e.g. `example@analytics.iam.gserviceaccount.com`

- `ANALYTICS_REPORTS_PATH` - The location of the JSON file that contains all of your reports.

    e.g. `reports/your-reports.json`

- `ANALYTICS_KEY` - Copy the `private_key` value from the Google Analytics json file. Keep all of the `\n`s in there and do **not** expand it; the bash scripts will take care of the expansion; this should be one really long line.

- `ANALYTICS_DATA_PATH` - The folder where all of the Google Analytics data will be stored.

    e.g. `data`

#### Socrata

The `socrata/run.py` WebJob will look and require these values to push data to Socrata.

- `SOCRATA_HOST` - The Socrata host
- `SOCRATA_APPTOKEN` - Reduces throttling with API calls with an [App Token](https://dev.socrata.com/docs/app-tokens.html)
- `SOCRATA_USER` & `SOCRATA_PASS` - For basic HTTP authentication
- `SOCRATA_RESOURCEID` - The 4x4 ID of the dataset

### Polling Google Analytics

18F provides us with bash scripts and `cron` jobs but they aren't very generic or Azure friendly, so we make use of [Azure WebJobs](https://azure.microsoft.com/en-us/documentation/articles/websites-dotnet-deploy-webjobs/). The `cron` jobs were easily ported over to [Azure's syntax](https://azure.microsoft.com/en-us/documentation/articles/web-sites-create-web-jobs/#CreateScheduledCRON).

WebJobs are placed in `App_Data/jobs/<triggered|continuous>` and each WebJob belongs in its own folder (the name of the folder is arbitrary). By adding a `run.sh` and a `settings.job` file in the folder, the `run.sh` will be executed based on the schedule defined by the `cron` expression located in `settings.job`.

Our bash scripts will read every `.env` file inside of `$HOME/envs` and fetch the Google Analytics for each profile. The fetched data will then be placed in a subdirectory with the same name as the `.env` file inside of `ANALYTICS_DATA_PATH`. For example, data for `smgov.env` will be placed at: `$HOME/data/smgov`.

### Data Aggregation

Since we do not have a "One Analytics Account to Rule Them All" like the [DAP](http://www.digitalgov.gov/services/dap/), we are aggregating all of our websites data together. This is a scheduled WebJob which goes through all of the agency directories, `$HOME/$ANALYTICS_DATA_PATH/<agency>` and aggregates all of the data together and outputs them to, `$HOME/$ANALYTICS_DATA_PATH`. Our analytics dashboard now points to the `ANALYTICS_DATA_PATH` folder instead of an individual agency but individual agency data is still available.

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
