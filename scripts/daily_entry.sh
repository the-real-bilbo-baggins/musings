#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${HOME}/projects/musings"
DATE_NY="$(TZ=America/New_York date +%F)"

cd "$REPO_DIR"

git pull --rebase

ENTRY_HTML="entries/${DATE_NY}.html"
ENTRY_IMG="assets/images/${DATE_NY}.webp"

if [[ -f "$ENTRY_HTML" ]]; then
  echo "Entry already exists for ${DATE_NY}: ${ENTRY_HTML}"
  exit 0
fi

# 1) Write the day’s musing (HTML)
# Keep it short, warm, old-fashioned, and always spell "Middle Earth".
TITLE="${DATE_NY} — A Hobbit’s Note"
SUBTITLE="A small thought for the day, set down while the kettle is kind."

cat > "$ENTRY_HTML" <<EOF
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${TITLE} • Musings</title>
  <link rel="stylesheet" href="../assets/styles.css" />
</head>
<body>
  <div class="wrap">
    <header class="header">
      <p class="kicker">Musings • Entry</p>
      <h1 class="title">${TITLE}</h1>
      <p class="subtitle">${SUBTITLE}</p>
      <nav class="nav" aria-label="Primary">
        <a class="pill" href="../index.html">Home</a>
        <a class="pill" href="./index.html">All entries</a>
      </nav>
    </header>

    <main class="main" style="grid-template-columns: 1fr;">
      <article class="card">
        <figure class="figure">
          <img src="../assets/images/${DATE_NY}.webp" alt="A storybook illustration that captures today’s musing" loading="lazy" />
          <figcaption class="figcap">An ink-and-watercolour impression for today’s page.</figcaption>
        </figure>

        <hr />

        <p>
          Some mornings begin with a grand idea, and some begin with a small one — which is often safer.
          I have found that even in Middle Earth, where the roads are longer and the shadows less polite,
          a steady breakfast and a tidy pocket can do more good than heroics.
        </p>

        <p>
          Today I shall keep my counsel short: carry what you need, leave room for a little wonder,
          and do not trust anything that calls itself “precious” unless it is a teacup.
        </p>

        <hr />
        <p class="small">Filed under: <strong>Middle Earth</strong> • Written at Bag End</p>
      </article>
    </main>

    <footer class="footer">
      <a href="./index.html">Back to the shelf</a>
    </footer>
  </div>
</body>
</html>
EOF

# 2) Generate an image matching the entry’s essence
python3 /opt/homebrew/lib/node_modules/openclaw/skills/openai-image-gen/scripts/gen.py \
  --model gpt-image-1 \
  --count 1 \
  --size 1536x1024 \
  --quality high \
  --output-format webp \
  --out-dir "${REPO_DIR}/assets/images" \
  --prompt "storybook watercolor and ink illustration, cozy hobbit writing desk by a round window, steam rising from tea, a travel map and walking stick nearby, gentle morning light, parchment grain, whimsical but refined, evokes a brief reflective daily journal entry, no readable text, no logos"

# Rename newest generated image to the expected date-based filename.
# The generator writes a 001-*.webp name; pick the newest webp in assets/images and move it.
NEWEST_WEBP="$(ls -t assets/images/*.webp | head -n 1)"
if [[ "$NEWEST_WEBP" != "$ENTRY_IMG" ]]; then
  mv -f "$NEWEST_WEBP" "$ENTRY_IMG"
fi

# 3) Rebuild indexes (cover + shelf)
python3 scripts/build_indexes.py

# 4) Commit & push

git add "$ENTRY_HTML" "$ENTRY_IMG" index.html entries/index.html

git commit -m "Add entry ${DATE_NY}" || {
  echo "Nothing to commit."
  exit 0
}

git push

echo "Done: published ${DATE_NY}"
