# Changelog

## Unreleased

- With `queue_stub: true`, the `{{ privatus_analytics(page) }}` template function now prints the queue stub
  and nothing else when the tag is off (`mkdocs serve`, `enabled: false` or no site id), so `privatus.track`
  calls never fail. Before, it printed nothing.
- With `queue_stub: true`, the automatic step now also adds the queue stub alone to every page when the tag
  is off (no tracker, no page props script). A page that already prints the stub with the template function
  does not get a second one. With `queue_stub: false` nothing is added, as before.
- `example/`: a tiny site for the Privatus conformance tests, built with the plugin and served by nginx.

## 1.0.0 - 2026-10-25

- Initial release.
- MkDocs plugin `privatus` that adds the tag before `</head>` on every page, including the 404 page.
- On for `mkdocs build` and `mkdocs gh-deploy`, off for `mkdocs serve`, unless `enabled` is set.
- Settings for site id, script host, modules, excluded paths, domains, single-page app mode, manual mode,
  extra attributes, nonce and the queue stub.
- Page props from `props` in mkdocs.yml, merged with `privatus_props` from each page's front matter.
- `auto_inject: false` and the `{{ privatus_analytics(page) }}` template function for theme overrides.
- Works with Material for MkDocs.
