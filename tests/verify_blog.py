#!/usr/bin/env python3
"""Validate the static Blog's reader-visible navigation and local assets."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
NEW_ARTICLE = BLOG / "temporal-semantic-runtime.html"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1_count = 0
        self.links: list[str] = []
        self.images: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        if tag == "img" and values.get("src"):
            self.images.append(values["src"] or "")


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def resolve_local(page: Path, ref: str) -> Path | None:
    if not ref or ref.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return None
    return (page.parent / ref.split("#", 1)[0]).resolve()


def main() -> None:
    assert NEW_ARTICLE.exists(), "missing Temporal Semantic Runtime article"

    index = parse(BLOG / "index.html")
    assert "temporal-semantic-runtime.html" in index.links, "Blog index has no link to the new article"

    pages = list(BLOG.glob("*.html"))
    for page in pages:
        parsed = parse(page)
        assert parsed.h1_count == 1, f"{page.name} must contain exactly one h1"
        for ref in parsed.links + parsed.images:
            local = resolve_local(page, ref)
            if local is not None:
                assert local.exists(), f"{page.name} has broken local reference: {ref}"

    article = NEW_ARTICLE.read_text(encoding="utf-8")
    for heading in ("World State", "ΔWorld", "Evidence Chain", "最终架构思想"):
        assert heading in article, f"article is missing core section: {heading}"

    print(f"Verified {len(pages)} Blog pages and all local references.")


if __name__ == "__main__":
    main()
