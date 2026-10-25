"""Real MkDocs builds of a tiny site in a temporary folder."""

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from mkdocs_privatus_analytics.plugin import PrivatusPlugin

TAG = '<script defer src="https://privatusstats.com/js/pa.js" data-site="pa_TEST123456"'


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("PRIVATUS_SITE_ID", raising=False)
    monkeypatch.delenv("PRIVATUS_SCRIPT_HOST", raising=False)


def build(tmp_path: Path, plugin_yaml: str, theme: str = "mkdocs", env: dict | None = None) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "index.md").write_text("# Home\n\nShowing `/js/pa.js` as text is fine.\n")
    (docs / "guide.md").write_text(
        textwrap.dedent(
            """\
            ---
            privatus_props:
              section: guides
              plan: null
            ---
            # Guide
            """
        )
    )
    (tmp_path / "mkdocs.yml").write_text(
        textwrap.dedent(
            f"""\
            site_name: Test docs
            theme:
              name: {theme}
            plugins:
            """
        )
        + textwrap.indent(plugin_yaml, "  ")
    )
    run_env = {**os.environ, **(env or {})}
    result = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict", "-q"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=run_env,
    )
    assert result.returncode == 0, result.stderr
    return tmp_path / "site"


def test_build_adds_the_tag_to_every_page(tmp_path):
    site = build(tmp_path, "- privatus:\n    site_id: pa_TEST123456\n")
    for page in ("index.html", "guide/index.html", "404.html"):
        html = (site / page).read_text()
        head = html.split("</head>")[0]
        assert head.count("/js/pa.js") == 1, page
        assert TAG in head


def test_site_props_and_page_front_matter_props(tmp_path):
    plugin = "- privatus:\n    site_id: pa_TEST123456\n    props:\n      plan: docs\n      version: 2\n"
    site = build(tmp_path, plugin)
    home = (site / "index.html").read_text()
    guide = (site / "guide/index.html").read_text()
    assert 'window.privatusPageProps=function(){return {"plan":"docs","version":2}}' in home
    assert 'data-props="privatusPageProps"' in home
    assert '{return {"version":2,"section":"guides"}}' in guide


def test_options_reach_the_tag(tmp_path):
    plugin = (
        "- privatus:\n    site_id: pa_TEST123456\n    modules: [engage, auto]\n    spa: hash\n"
        "    excluded_paths: [/drafts/*]\n    queue_stub: true\n    nonce: n0nce\n"
        "    extra_attributes:\n      data-debug: 'true'\n"
    )
    html = (build(tmp_path, plugin) / "index.html").read_text()
    assert 'data-modules="engage,auto"' in html
    assert 'data-exclude="/drafts/*"' in html
    assert 'data-spa="hash"' in html
    assert 'data-debug="true"' in html
    assert '<script nonce="n0nce">window.privatus=window.privatus||{q:[]}' in html


def test_site_id_from_the_environment(tmp_path):
    html = (build(tmp_path, "- privatus\n", env={"PRIVATUS_SITE_ID": "pa_TEST123456"}) / "index.html").read_text()
    assert TAG in html


def test_enabled_false_and_no_site_id_add_nothing(tmp_path):
    off = build(tmp_path / "a", "- privatus:\n    site_id: pa_TEST123456\n    enabled: false\n")
    assert "/js/pa.js" not in (off / "index.html").read_text().split("</head>")[0]


def test_no_site_id_adds_nothing(tmp_path):
    site = build(tmp_path, "- privatus\n")
    assert "/js/pa.js" not in (site / "index.html").read_text().split("</head>")[0]


def test_auto_inject_false_with_the_template_global(tmp_path):
    overrides = tmp_path / "overrides"
    overrides.mkdir(parents=True)
    (overrides / "main.html").write_text(
        '{% extends "base.html" %}\n{% block extrahead %}{{ privatus_analytics(page) }}{% endblock %}\n'
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n")
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: T\ntheme:\n  name: mkdocs\n  custom_dir: overrides\n"
        "plugins:\n  - privatus:\n      site_id: pa_TEST123456\n      auto_inject: false\n"
    )
    subprocess.run([sys.executable, "-m", "mkdocs", "build", "-q"], cwd=tmp_path, check=True)
    html = (tmp_path / "site" / "index.html").read_text()
    assert html.count("/js/pa.js") == 1
    assert TAG in html


def test_works_with_material_for_mkdocs(tmp_path):
    pytest.importorskip("material")
    site = build(tmp_path, "- search\n- privatus:\n    site_id: pa_TEST123456\n", theme="material")
    for page in ("index.html", "guide/index.html", "404.html"):
        html = (site / page).read_text()
        head = html.split("</head>")[0]
        assert head.count("/js/pa.js") == 1, page
        assert TAG in head


def test_serve_is_off_and_build_is_on_by_default():
    plugin = PrivatusPlugin()
    plugin.load_config({"site_id": "pa_TEST123456"})
    plugin.on_startup(command="serve", dirty=False)
    assert plugin.tag() == ""
    plugin.on_startup(command="build", dirty=False)
    assert TAG in plugin.tag()
    plugin.on_startup(command="gh-deploy", dirty=False)
    assert TAG in plugin.tag()


def test_enabled_true_turns_it_on_for_serve():
    plugin = PrivatusPlugin()
    plugin.load_config({"site_id": "pa_TEST123456", "enabled": True})
    plugin.on_startup(command="serve", dirty=False)
    assert TAG in plugin.tag()
