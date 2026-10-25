# Changelog

## 1.0.0 - 2026-10-25

- Initial release.
- MkDocs plugin `privatus` that adds the tag before `</head>` on every page, including the 404 page.
- On for `mkdocs build` and `mkdocs gh-deploy`, off for `mkdocs serve`, unless `enabled` is set.
- Settings for site id, script host, modules, excluded paths, domains, single-page app mode, manual mode,
  extra attributes, nonce and the queue stub.
- Page props from `props` in mkdocs.yml, merged with `privatus_props` from each page's front matter.
- `auto_inject: false` and the `{{ privatus_analytics(page) }}` template function for theme overrides.
- Works with Material for MkDocs.
