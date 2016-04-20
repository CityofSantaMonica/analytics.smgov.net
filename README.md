# analytics.smgov.net

A project to publish website analytics for the City of Santa Monica.

Based on the [original](https://github.com/18F/analytics.usa.gov) by
[18F](https://github.com/18F).

For a detailed description of how the site works, read [18F's blog post on analytics.usa.gov](https://18f.gsa.gov/2015/03/19/how-we-built-analytics-usa-gov/).

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

The development settings assume data is available at `/fakedata`. You can change this in `_configdev.yml`.

[`analytics-reporter`](https://github.com/18F/analytics-reporter) is the code that powers the analytics dashboard.

## Public Domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
