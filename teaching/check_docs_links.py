#!/usr/bin/env python3
"""Check docs HTML relative links and anchors. No network."""

from pathlib import Path
import re
import sys

docs = Path(__file__).resolve().parents[1] / "docs"
href_re = re.compile(r'href="([^"]+)"')
id_re = re.compile(r'\sid="([^"]+)"')
errors = []
pages = sorted(docs.rglob("*.html"))
for page in pages:
    text = page.read_text(encoding="utf-8")
    ids = set(id_re.findall(text))
    for href in href_re.findall(text):
        if href.startswith("#"):
            if href[1:] not in ids:
                errors.append(f"{page.name}: missing {href}")
            continue
        if href.startswith("http://") or href.startswith("https://"):
            continue
        target = (page.parent / href.split("#", 1)[0]).resolve()
        if not target.is_file():
            errors.append(f"{page.relative_to(docs)} -> {href}")
            continue
        if "#" in href:
            frag = href.split("#", 1)[1]
            tids = set(id_re.findall(target.read_text(encoding="utf-8")))
            if frag not in tids:
                errors.append(f"{href}: missing anchor")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"ok {len(pages)} html")
