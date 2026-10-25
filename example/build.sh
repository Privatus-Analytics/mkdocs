#!/bin/sh
# Builds the three small sites and puts their pages in one folder ($1).
#   main/      /, /event, /nasty and /auto: the plugin as most sites use it
#   off/       /off: the tag forced off, queue stub on
#   off-plain/ /off-plain: the tag forced off, queue stub off
set -e
out="$1"
cd "$(dirname "$0")"
mkdocs build -q -f main/mkdocs.yml -d "$out"
for name in off off-plain; do
  mkdocs build -q -f "$name/mkdocs.yml" -d "/tmp/$name"
  mkdir -p "$out/$name"
  cp "/tmp/$name/index.html" "$out/$name/index.html"
done
