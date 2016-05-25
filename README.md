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

These notes represent an evolving effort. Create an [issue](https://github.com/CityofSantaMonica/analytics.smgov.net/issues) or send us a [pull request](https://github.com/CityofSantaMonica/analytics.smgov.net/pulls) if you have questions or suggestions about anything outline below.

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

The report definitions are specified as JSON objects. In this repository, individual report definitions are stored in the `_reports` folder, and aggregated into a single file `reports/csm.json` by using Jekyll's build process and a custom plugin for [JSONifying Jekyll frontmatter](https://github.com/CityofSantaMonica/jekyll-frontmatter-jsonify).

### JSON Structure

An individual report definition looks like the following:

```
{
  "name": "report-name",
  "frequency": "daily",
  "query": {
    "dimensions": [ "ga:pagePath", "ga:pageTitle" ],
    "metrics": [ "ga:sessions" ],
    "start-date": "yesterday",
    "end-date": "today",
    "sort": "-ga:sessions",
    "max-results": "20"
  },
  "meta": {
    "name": "Dummy Report",
    "description": "Sample report definition to show the structure of a report"
  }
}
```
- `name` - the name of the report; *this will be the resulting file name for the report*
- `frequency` - corresponds to the [`--frequency` command line option](https://github.com/18F/analytics-reporter#options). This option does **not** automagically create cron jobs; separate cron jobs or WebJobs are required.
- `query`
  - `dimensions` & `metrics` - valid values can be found in the [Google Analytics Docs](https://developers.google.com/analytics/devguides/reporting/core/v3/reference)
  - `start-date` or `end-date` - time period for the report
    - `today`
    - `yesterday`
    - `7daysAgo`
    - `30daysAgo`
    - `90daysAgo`
  - `sort` - valid values can be found in the [Google Analytics Docs](https://developers.google.com/analytics/devguides/reporting/core/v3/reference)
  - `max-results` - maximum results to return for this report

## Deployment

18F's original [analytics dashboard](https://github.com/18F/analytics.usa.gov) was written with a Linux environment and [18F pages](https://github.com/18F/pages) in mind. For this project, we've ported 18F's work into an [Azure Web App](https://azure.microsoft.com/en-us/services/app-service/web/).

This fork has both the Jekyll website and node app (`analytics-reporter`) deployed to a single Azure Web App so that everything remains on the same domain. We use [TravisCI](https://travis-ci.org/) to kick off Jekyll builds and related pre-deployment tasks, and publish the end result to Azure.

### Travis CI

Travis can automatically [deploy to Azure after a successful build](https://docs.travis-ci.com/user/deployment/azure-web-apps) and have the following environment variables set:

- `AZURE_WA_SITE` - the name of the Azure Web App
- `AZURE_WA_USERNAME` - the git/deployment username, configured in the Azure Web App settings
- `AZURE_WA_PASSWORD` - The password of the above user, also configured in the Azure Web App settings
  - **Heads up!** Travis sends this password in the remote URL (i.e. `https://user:password@domain.com/repo.git`), so be careful with special characters in your passwords (e.g. spaces don't work and will cause a cryptic error to be thrown).

#### Scripts

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

We are calling two separate scripts for Travis to execute. The first script is the `.build.sh` script which actually builds the Jekyll website (into the `_site` folder as per Jekyll convention).

> In our case, we have a "fake-data" folder for development so we remove that before we build the final website.

The second script (`pre-deploy.sh`) is called before we deploy everything to Azure. Content is deployed to Azure via git, meaning `.gitignore` is respected and the compiled `_site` wouldn't be deployed to Azure.

To fix this, the pre-deploy script gives Travis an identity for git, forcefully adds the `_site` directory, and amends the commit we were just building:

```bash
git config user.name "travis-ci"
git config user.email "travis@localhost"
git add -f _site/
git commit --amend --no-edit
```

By amending the commit, the message and author stay intact when viewed from the Azure portal.

### Azure

18F [specifies required environment variables](https://github.com/18F/analytics-reporter#setup) in `.env` files. Instead of placing all of them in `.env` files and worry about sensitive information or repetition, we store them as [Azure Application Settings](https://azure.microsoft.com/en-us/documentation/articles/web-sites-configure/).

We also opted to make use of [Azure WebJobs](https://azure.microsoft.com/en-us/documentation/articles/websites-dotnet-deploy-webjobs/) for background tasks (such as polling Google Analytics and aggregating the results). 18F's `cron` jobs were easily ported over to [Azure's syntax](https://azure.microsoft.com/en-us/documentation/articles/web-sites-create-web-jobs/#CreateScheduledCRON).

WebJobs are placed in `App_Data/jobs/<triggered|continuous>` and each WebJob belongs in its own folder (the name of the folder is arbitrary). By adding a `run.sh` (or `run.py`) and a `settings.job` file containing a `cron` expression, the `run` file is executed based on the `cron` schedule.

All of the scripts available have a custom `$HOME` which is set to: `D:\home\site\wwwroot` (the default for Azure Web Apps). All of the paths defined in Azure Application Settings or environment variables should be **relative** to the custom `$HOME` directory; **do not** use absolute paths.

#### Kudu Configuration

[Kudu](https://github.com/projectkudu/kudu) is the Azure build/deploy system tied into git, which is used to move the (compiled) site files into the website root (`$HOME`) after a successful Travis build. Our Kudu configuration file looks like:

```
[config]
DEPLOYMENT_SOURCE = _site
COMMAND = bash .kudu/deploy.sh
```

## Polling Google Analytics

This WebJob executes a bash script that reads every `.env` file inside of `$HOME/envs` and fetches the Google Analytics for each profile. The fetched data is then placed in a subdirectory with the same name as the `.env` file, inside of `ANALYTICS_DATA_PATH`.

> For example, data for `smgov.env` will be placed at: `$HOME/data/smgov`.

### Google Analytics Configuration

These Azure Application Settings are required for interaction with the Google Analytics API (via `analytics-reporter`):

- `ANALYTICS_REPORT_EMAIL` - The email used for your Google developer account; this account is automatically generated for you by Google. This account should have access to the appropriate profiles in Google Analytics.

    > e.g. `example@analytics.iam.gserviceaccount.com`

  it should be noted that this email account must have **Collaborate, Read & Analyze** permissions on the Google Analytics profile(s)/view(s) being queried.

- `ANALYTICS_REPORTS_PATH` - The location of the JSON file that contains all of your reports.

    > e.g. `reports/your-reports.json`

- `ANALYTICS_KEY` - Copy the `private_key` value from the Google Analytics json file. Keep all of the `\n`s in there and **do not** expand it; the bash scripts will take care of the expansion; this should be one really long line.

- `ANALYTICS_DATA_PATH` - The folder where all of the Google Analytics data will be stored.

    > e.g. `data`

## Data Aggregation

Since we do not have "One Analytics Account to Rule Them All" like the [DAP](http://www.digitalgov.gov/services/dap/), we are aggregating individual websites together. This is a scheduled WebJob (using Python) which goes through all of the agency directories, `$HOME/$ANALYTICS_DATA_PATH/<agency>` and aggregates all of the data together and outputs them to, `$HOME/$ANALYTICS_DATA_PATH`.

Our analytics dashboard then points to the `ANALYTICS_DATA_PATH` folder instead of an individual agency; individual agency data is still available at the subdirectory level.

## Archiving to Socrata

Because the data files powering the dashboard are constantly being overwritten, we have another Python WebJob that takes the daily analytics reports and snapshots them in to our [open data portal](https://data.smgov.net).

### Socrata Configuration

These Azure Application Settings are required for publishing data to the Socrata portal (via [`soda-py`](https://github.com/xmunoz/sodapy)):

- `SOCRATA_HOST` - the Socrata host (e.g. **data.smgov.net**)
- `SOCRATA_APPTOKEN` - reduces throttling with API calls with an [App Token](https://dev.socrata.com/docs/app-tokens.html)
- `SOCRATA_USER` & `SOCRATA_PASS` - for basic HTTP authentication
- `SOCRATA_RESOURCEID` - the [4x4 ID](https://dev.socrata.com/docs/endpoints.html) of the dataset

## Public Domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
