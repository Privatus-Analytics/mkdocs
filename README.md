# Privatus Analytics for MkDocs

A [MkDocs](https://www.mkdocs.org) plugin that adds the cookieless
[Privatus Analytics](https://privatusanalytics.com) tracking script to the
`<head>` of every page of your docs site. It works with the default themes and
with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

Privatus Analytics counts visits, sources, pages and conversions without
cookies, local storage or fingerprinting, so analytics does not need a consent
banner by itself. Check with your own counsel for your country.

The plugin only adds the browser script to your built pages. It never sends
events from your computer or build server and sets no cookies. You need a
Privatus Analytics account to see reports, and there is a free plan. Sign up at
https://privatusanalytics.com.

## Requirements

* Python 3.10 or later.
* MkDocs 1.5 or later (1.x). It needs MkDocs plugins, so it does not work with
  a MkDocs version that has no plugin support.
* A Privatus Analytics site id (it starts with `pa_`). You find it under
  Site settings, Tracking.

## Install

```sh
pip install mkdocs-privatus-analytics
```

For the full setup guide and every tracker option, see the [Privatus Analytics
docs](https://privatusanalytics.com/docs).

## Add the tag

Add the plugin to `mkdocs.yml`:

```yaml
plugins:
  - search
  - privatus:
      site_id: pa_YOURSITEID
```

If you list `plugins:` yourself, MkDocs no longer adds `search` for you, so keep
it in the list if you use it.

Instead of writing the site id in the file, you can set an environment
variable on your build machine and use just `- privatus`:

```sh
PRIVATUS_SITE_ID=pa_YOURSITEID mkdocs build
```

`mkdocs build` and `mkdocs gh-deploy` then put this just before `</head>` on
every page, including the 404 page:

```html
<script defer src="https://privatusstats.com/js/pa.js" data-site="pa_YOURSITEID"></script>
```

The plugin adds no tag when there is no site id. It writes a note to the
build log, which does not break `--strict` builds. It also adds no tag while
you run `mkdocs serve`, so your own visits while you write are never counted.
(With `queue_stub: true` it still adds the small queue stub, see below.)
Pages that already have the tag in their head are left alone.

### Or place the tag yourself

If you would rather choose where the tag goes, turn off the automatic step and
call the template function from a theme override:

```yaml
theme:
  name: material
  custom_dir: overrides
plugins:
  - privatus:
      site_id: pa_YOURSITEID
      auto_inject: false
```

```jinja
{# overrides/main.html #}
{% extends "base.html" %}
{% block extrahead %}
  {{ super() }}
  {{ privatus_analytics(page) }}
{% endblock %}
```

### Material for MkDocs without this plugin

Material for MkDocs has its own way to add any analytics tool, with no extra
package. Use it if you only want the basic tag and do not need page props or
the build-only switch. Set a custom provider in `mkdocs.yml`:

```yaml
theme:
  name: material
  custom_dir: overrides
extra:
  analytics:
    provider: custom
```

Then create `overrides/partials/integrations/analytics/custom.html`:

```html
<script defer src="https://privatusstats.com/js/pa.js" data-site="pa_YOURSITEID"></script>
```

With this route the tag is also on the pages that `mkdocs serve` shows you. The
tracker ignores `localhost`, so those visits are still not counted.

### Material's instant loading

Material's `navigation.instant` feature loads the next page without a full
page load. The tracker sees these page changes by itself (its single-page app
mode is `auto` by default), so every page is still counted. One thing to know:
the head is not loaded again, so page props from front matter (see below) stay
the ones from the first page someone opened. Site-wide props are not affected.

## Configuration

Every setting is optional except the site id.

```yaml
plugins:
  - privatus:
      site_id: pa_YOURSITEID          # or the PRIVATUS_SITE_ID environment variable
      script_host: https://privatusstats.com # or PRIVATUS_SCRIPT_HOST
      modules: [engage, auto, vitals, clicks, ask]
      excluded_paths: [/drafts/*]
      domains: [docs.example.com]
      spa: auto                       # auto, history, hash or off
      manual: false                   # true turns off the automatic pageview
      enabled: null                   # true or false forces the tag on or off
      auto_inject: true
      extra_attributes:
        data-mask: /orders/*->/orders/:id
      props:
        docs_version: "2.4"
      queue_stub: false
      nonce: ""
```

| Setting | Default | What it does |
|---|---|---|
| `site_id` | `PRIVATUS_SITE_ID` | The `data-site` attribute. Nothing is added without it |
| `script_host` | `https://privatusstats.com` | Where `/js/pa.js` is served. Change it only if you host your own copy |
| `modules` | tracker default (`engage`) | The `data-modules` attribute. Setting it replaces the default, so keep `engage` for time on page and scroll depth. `[]` loads none |
| `excluded_paths` | none | The `data-exclude` attribute. Path patterns the tracker never counts |
| `domains` | all hosts | The `data-domains` attribute. Count only these hostnames |
| `spa` | `auto` | The `data-spa` attribute |
| `manual` | `false` | The `data-manual` attribute |
| `enabled` | not set | `true` or `false` forces the tag on or off. Not set means on for `mkdocs build` and `mkdocs gh-deploy`, off for `mkdocs serve` |
| `auto_inject` | `true` | Adds the tag before `</head>` on every page. `false` leaves it to `{{ privatus_analytics(page) }}` |
| `extra_attributes` | `{}` | Any other `data-*` attribute |
| `props` | `{}` | Page props sent with every pageview and event. See below |
| `queue_stub` | `false` | Adds a small script first, so `privatus.track` calls made before the tracker loads are kept and sent later |
| `nonce` | none | A Content Security Policy nonce for the tags. Static sites rarely have one |

Each tracker attribute is explained in the [script attributes
reference](https://privatusanalytics.com/docs/tracker/attributes), and the
modules in [Modules](https://privatusanalytics.com/docs/tracker/modules).

### Development and test

`mkdocs serve` never gets the tag, so your own clicking around never reaches
your reports. To see the tag while you write, set `enabled: true`. The tracker
also ignores `localhost` unless you pass `data-allow-local` or `data-debug` (see
[Debug mode](https://privatusanalytics.com/docs/tracker/debug)):

```yaml
      enabled: true
      extra_attributes:
        data-debug: "true"
```

If you build preview copies of your docs (for example for pull requests) and
do not want to count them, set `enabled` from an environment variable with
MkDocs' `!ENV` tag:

```yaml
      enabled: !ENV [PRIVATUS_ENABLED, false]
```

### Leaving people out

Use `excluded_paths` for pages you do not want counted, like drafts. The
`domains` setting makes sure only your real site is counted, not copies on
other hosts.

## Product analytics: see which features people use

Privatus can show which links and buttons people use in your docs, and which
parts of your docs lead people to sign up. You add a few attributes to your
HTML. The tracker reads them in the browser and sends the events. Your build
still sends nothing.

### Name events well

Use a short "Noun verb" name, like `Example copied` or `Download started`. Put
the details in props, not in the name. So write `Download started` with
`format: zip`, not `Download started as zip`. Then all downloads add up in one
place, and you can split them by format.

### Events on buttons, links and forms

Add the attributes in Markdown with the `attr_list` extension (Material for
MkDocs turns it on in most setups):

```yaml
markdown_extensions:
  - attr_list
```

```markdown
[Download the PDF](guide.pdf){ data-privatus-event="Download started" data-privatus-prop-format="pdf" }
```

Or write the HTML yourself:

```html
<a href="/guide.pdf" data-privatus-event="Download started" data-privatus-prop-format="pdf">Download</a>
```

On a form, the event is sent when the form is submitted. Use a short event
name (at most 120 characters). Prop keys are lowercase letters, digits and `_`,
and there can be up to 30 of them.

### Click maps

A click map shows where people click on a page. Give the important parts a
name so they stay easy to find, even when the page changes:

```markdown
[See plans](https://example.com/pricing){ data-privatus-click="docs.pricing-link" }
```

A name may use letters, digits and `_ . : -`, up to 100 characters.

### Page props: version, section and other groups

Page props are sent with every pageview and event on the page. Use them to
split your reports by docs version, section or product.

Set them for the whole site:

```yaml
plugins:
  - privatus:
      site_id: pa_YOURSITEID
      props:
        docs_version: "2.4"
        product: api
```

and change them for one page in its front matter. They are merged over the site
props, and `null` removes one:

```markdown
---
privatus_props:
  section: tutorials
  product: null
---
# Getting started
```

The plugin then adds a small script before the tracker and points the tracker
at it:

```html
<script>window.privatusPageProps=function(){return {"docs_version":"2.4","section":"tutorials"}}</script>
<script defer src="https://privatusstats.com/js/pa.js" data-site="pa_YOURSITEID" data-props="privatusPageProps"></script>
```

Keys are made lowercase, and anything that is not a letter, a digit or `_`
becomes `_`. Numbers and true or false stay as they are, and lists stay lists
(up to 30 items). Text is cut to 500 characters. The props are escaped so they
are safe inside a script.

**Never put names, emails, user ids or anything that points to one person in
props.** Privatus counts visitors without any id. Put groups (like the docs
version or the section), not people. The server also removes emails and long
ids it finds.

### Track from your own JavaScript

For things that are not a click or a submit, call the tracker from your
JavaScript (add it with MkDocs' `extra_javascript`), as the [JavaScript API
docs](https://privatusanalytics.com/docs/tracker/javascript-api) explain:

```js
privatus.track("Feature used", { feature: "search" })
```

If your code may run before the tracker has loaded, set `queue_stub: true`. It
adds a tiny script before the tracker that keeps your calls in a list and
sends them once the tracker is ready. The stub is added even when the tag is
off (for `mkdocs serve`, with `enabled: false` or with no site id). Then your
`privatus.track` calls never fail: they wait in the list and are never sent.

### See the results

* [Funnels](https://privatusanalytics.com/docs/features/funnels): how many
  people go from one step to the next.
* [Click maps](https://privatusanalytics.com/docs/features/click-maps): where
  people click.
* [Goals](https://privatusanalytics.com/docs/features/goals): turn an event
  into a goal to count conversions.
* [Events](https://privatusanalytics.com/docs/events): every custom event and
  its props.

## Privacy

The script sets no cookies and stores nothing in the browser. The plugin only
adds HTML to your pages. Keep people out of your props and event props: no
names, emails or user ids. See the [privacy
documentation](https://privatusanalytics.com/docs/privacy) for what is
collected.

If you have a privacy policy, it should say which tools handle your visitors' data. You can paste this:

> This website uses [Privatus Analytics](https://privatusanalytics.com/privacy-analytics) to count visits. It
> does not use cookies and does not follow you from one website to another. Your IP address is used for a moment
> to count visits and is never stored.

Change it to fit your site. The [privacy policy generator](https://privatusanalytics.com/tools/privacy-policy-generator)
makes a longer version with your site's name in it.

## Development

The tests run in Docker so your local Python does not matter:

```sh
./run-docker.sh
```

It runs pytest (with real MkDocs builds of a tiny site, with the default theme
and with Material for MkDocs), Ruff, and the package build.

The `example/` folder holds a tiny site for the [conformance
tests](https://github.com/Privatus-Analytics/conformance), which open it in a
real browser with the real tracker. Run them from a copy of that repo with
`./run.sh ../mkdocs`.

## Contributing

Bug reports and pull requests are welcome at
https://github.com/Privatus-Analytics/mkdocs.

## License

MIT. See [LICENSE](LICENSE). Privatus Analytics is a product of Two Phase LLC,
Wyoming, USA.
