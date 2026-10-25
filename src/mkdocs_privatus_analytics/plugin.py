"""The MkDocs plugin. Add it to mkdocs.yml as `- privatus:`."""

from __future__ import annotations

import logging
from typing import Any

from markupsafe import Markup
from mkdocs.config import base
from mkdocs.config import config_options as c
from mkdocs.plugins import BasePlugin

from ._core import SPA_MODES, Settings, inject, merge_props, off_tag, render_tag

log = logging.getLogger("mkdocs.plugins.privatus")

# Commands that make the real site. `mkdocs serve` is left out so your own
# visits while writing are never counted.
BUILD_COMMANDS = ("build", "gh-deploy")


class PrivatusConfig(base.Config):
    """The settings under `plugins: - privatus:` in mkdocs.yml."""

    site_id = c.Type(str, default="")
    script_host = c.Type(str, default="")
    modules = c.Optional(c.Type((list, str)))
    excluded_paths = c.Optional(c.Type((list, str)))
    domains = c.Optional(c.Type((list, str)))
    spa = c.Optional(c.Choice(SPA_MODES))
    manual = c.Type(bool, default=False)
    enabled = c.Optional(c.Type(bool))
    auto_inject = c.Type(bool, default=True)
    extra_attributes = c.Type(dict, default={})
    props = c.Type(dict, default={})
    queue_stub = c.Type(bool, default=False)
    nonce = c.Type(str, default="")


class PrivatusPlugin(BasePlugin[PrivatusConfig]):
    """Adds the Privatus Analytics script to the <head> of every built page."""

    def __init__(self) -> None:
        super().__init__()
        self.command: str | None = None
        self._warned = False

    def on_startup(self, *, command: str, dirty: bool) -> None:
        self.command = command

    def settings(self) -> Settings:
        cfg = self.config
        return Settings(
            site_id=cfg.site_id,
            script_host=cfg.script_host,
            modules=cfg.modules,
            excluded_paths=cfg.excluded_paths,
            domains=cfg.domains,
            spa=cfg.spa,
            manual=cfg.manual,
            extra_attributes=cfg.extra_attributes,
            queue_stub=cfg.queue_stub,
            nonce=cfg.nonce or None,
        )

    def is_enabled(self) -> bool:
        """`enabled` forces it. Otherwise on for `mkdocs build` and `gh-deploy`, off for `serve`."""
        if self.config.enabled is not None:
            return self.config.enabled
        # No command means MkDocs was run from Python (mike and other tools); treat it as a build.
        return self.command is None or self.command in BUILD_COMMANDS

    def tag(self, page: Any = None) -> str:
        """The HTML for one page: the site props merged with the page's `privatus_props` front matter."""
        settings = self.settings()
        if not self.is_enabled():
            # Off: only the queue stub (when queue_stub is on), so privatus.track calls never throw.
            return off_tag(settings)
        if settings.resolved_site_id() is None:
            if not self._warned:
                log.info("privatus: no site_id (and no PRIVATUS_SITE_ID), so no tag was added.")
                self._warned = True
            return off_tag(settings)
        meta = getattr(page, "meta", None) or {}
        page_props = meta.get("privatus_props") if isinstance(meta.get("privatus_props"), dict) else None
        return render_tag(settings, merge_props(self.config.props, page_props))

    def on_env(self, env: Any, *, config: Any, files: Any) -> Any:
        # For theme overrides: {{ privatus_analytics(page) }} prints the tag where you want it.
        env.globals["privatus_analytics"] = lambda page=None: Markup(self.tag(page))
        return env

    def on_post_page(self, output: str, *, page: Any, config: Any) -> str:
        # When the tag is off, tag() is the queue stub alone (queue_stub on) or "".
        if not self.config.auto_inject:
            return output
        return inject(output, self.tag(page))

    def on_post_template(self, output_content: str, *, template_name: str, config: Any) -> str:
        # Static HTML templates such as 404.html are not pages, so they come through here.
        if not self.config.auto_inject or not template_name.endswith(".html"):
            return output_content
        return inject(output_content, self.tag())
