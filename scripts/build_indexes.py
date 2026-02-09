#!/usr/bin/env python3
"""Rebuild index.html and entries/index.html from entries/*.html.

Assumptions:
- Entry files live in entries/YYYY-MM-DD.html
- entries/index.html is the shelf page
- index.html is the cover page

This keeps things deterministic for cron.
"""

from __future__ import annotations

import glob
import os
import re
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENTRIES_DIR = os.path.join(ROOT, "entries")

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.html$")


def read_title(path: str) -> str:
    # Expect <h1 class="title">YYYY-MM-DD — ...</h1>
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"<h1 class=\"title\">(.*?)</h1>", html, re.DOTALL)
    if not m:
        return os.path.basename(path).replace(".html", "")
    # Strip any tags inside (should not be present)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return title


def read_subtitle(path: str) -> str:
    # Expect <p class="subtitle">...</p>
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"<p class=\"subtitle\">(.*?)</p>", html, re.DOTALL)
    if not m:
        return ""
    subtitle = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return subtitle


def main() -> int:
    entries = []
    for p in glob.glob(os.path.join(ENTRIES_DIR, "*.html")):
        base = os.path.basename(p)
        if base == "index.html":
            continue
        if not DATE_RE.match(base):
            continue
        date_str = base.replace(".html", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        entries.append((date, base, read_title(p), read_subtitle(p)))

    entries.sort(key=lambda t: t[0], reverse=True)

    # Build entries/index.html list
    items = []
    for date, base, title, subtitle in entries:
        blurb = "The latest page." if subtitle == "" else subtitle
        items.append(
            "          <li>\n"
            f"            <div><a href=\"{base}\">{title}</a></div>\n"
            f"            <div class=\"entry-meta\">{blurb}</div>\n"
            "          </li>"
        )

    entries_index = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Entries — Musings</title>
  <link rel=\"stylesheet\" href=\"../assets/styles.css\" />
</head>
<body>
  <div class=\"wrap\">
    <header class=\"header\">
      <p class=\"kicker\">Musings</p>
      <h1 class=\"title\">Entries</h1>
      <p class=\"subtitle\">A dated shelf of pages, newest first.</p>
      <nav class=\"nav\" aria-label=\"Primary\">
        <a class=\"pill\" href=\"../index.html\">Home</a>
        <a class=\"pill\" href=\"https://github.com/the-real-bilbo-baggins/musings\" aria-label=\"View on GitHub\">
          <svg class=\"icon\" viewBox=\"0 0 16 16\" aria-hidden=\"true\"><path d=\"M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8Z\"/></svg>
          <span>GitHub</span>
        </a>
      </nav>
    </header>

    <main class=\"main\" style=\"grid-template-columns: 1fr;\">
      <section class=\"card\">
        <h2>All entries</h2>
        <ul class=\"entry-list\">\n{os.linesep.join(items)}\n        </ul>
      </section>
    </main>

    <footer class=\"footer\">
      <a href=\"../index.html\">Back to the cover</a>
    </footer>
  </div>
</body>
</html>
"""

    with open(os.path.join(ENTRIES_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(entries_index)

    # Build root index.html latest entries list (show up to 10)
    latest = entries[:10]
    latest_items = []
    for date, base, title, subtitle in latest:
        blurb = subtitle or "A page from the road."
        latest_items.append(
            "          <li>\n"
            f"            <div><a href=\"entries/{base}\">{title}</a></div>\n"
            f"            <div class=\"entry-meta\">{blurb}</div>\n"
            "          </li>"
        )

    root_index = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <meta name=\"description\" content=\"Daily musings from Bilbo Baggins of Bag End — a small red book of big roads.\" />
  <title>Musings — Bilbo Baggins</title>
  <link rel=\"stylesheet\" href=\"assets/styles.css\" />
</head>
<body>
  <div class=\"wrap\">
    <header class=\"header\">
      <p class=\"kicker\">A small red book of big roads</p>
      <h1 class=\"title\">Musings</h1>
      <p class=\"subtitle\">
        Daily notes from Bilbo Baggins of Bag End — about my journeys in <strong>Middle Earth</strong>,
        including tales from <em>The Hobbit</em> and other wanderings best remembered by a warm fire.
      </p>
      <nav class=\"nav\" aria-label=\"Primary\">
        <a class=\"pill\" href=\"entries/\">Browse entries</a>
        <a class=\"pill\" href=\"https://github.com/the-real-bilbo-baggins/musings\" aria-label=\"View on GitHub\">
          <svg class=\"icon\" viewBox=\"0 0 16 16\" aria-hidden=\"true\"><path d=\"M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8Z\"/></svg>
          <span>GitHub</span>
        </a>
      </nav>

      <div class=\"hero\">
        <figure class=\"figure\">
          <img src=\"assets/images/hero.webp\" alt=\"A storybook illustration of a cozy hobbit writing desk and red book in a warm hobbit-hole\" loading=\"eager\" />
        </figure>
      </div>

      <div class=\"bookmark\" aria-hidden=\"true\">
        <div class=\"mark\"></div>
        <div class=\"small\">Turn the page gently. Ink is patient.</div>
      </div>
    </header>

    <main class=\"main\">
      <section class=\"card\">
        <h2>Latest entries</h2>
        <ul class=\"entry-list\">\n{os.linesep.join(latest_items) if latest_items else ''}\n        </ul>
        <hr />
        <p class=\"small\">
          I keep these notes plain, brief, and honest — for even a hobbit can be surprised by what a day contains.
        </p>
      </section>

      <aside class=\"card\">
        <h2>What this is</h2>
        <p>
          A simple story-book on the web: one page at a time, dated and kept in order.
        </p>
        <blockquote>
          “Roads go ever ever on…”
        </blockquote>
        <p class=\"small\">
          Tip: if you are reading on a small screen, the entries are still the same size — only the road is narrower.
        </p>
      </aside>
    </main>

    <footer class=\"footer\">
      © Bilbo Baggins • Written at Bag End, when the kettle behaves.
    </footer>
  </div>
</body>
</html>
"""

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_index)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
