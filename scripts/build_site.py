"""Build the dependency-free Riverton Pages fixture from checked-in CSV data."""

from __future__ import annotations

import csv
import html
import shutil
import zipfile
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
SITE = DIST / "riverton"
BASE_URL = "https://frisket-dev.github.io/frisket-samples/riverton"


def read_csv(name: str) -> list[dict[str, str]]:
    with (CONTENT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def page(title: str, body: str, *, description: str = "") -> str:
    safe_title = html.escape(title)
    safe_description = html.escape(description or title, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title} · Riverton Civic Dispatch</title>
  <meta name="description" content="{safe_description}">
  <link rel="alternate" type="application/rss+xml" title="Riverton Civic Dispatch" href="{BASE_URL}/feed.xml">
  <link rel="stylesheet" href="{BASE_URL}/assets/site.css">
</head>
<body>
  <header class="masthead">
    <a class="brand" href="{BASE_URL}/">Riverton Civic Dispatch</a>
    <span>Synthetic public-interest reporting fixture</span>
  </header>
  <main>{body}</main>
  <footer>Fictional source material created for Frisket walkthroughs.</footer>
</body>
</html>
"""


def story_body(row: dict[str, str]) -> str:
    paragraphs = "\n".join(
        f"<p>{html.escape(paragraph.strip())}</p>"
        for paragraph in row["story"].split("\n\n")
        if paragraph.strip()
    )
    return f"""<article>
  <p class="eyebrow">{html.escape(row["source_kind"].replace("_", " "))}</p>
  <h1>{html.escape(row["headline"])}</h1>
  <p class="byline">{html.escape(row["publisher"])} · <time datetime="{html.escape(row["published_at"])}">{html.escape(row["published_at"][:10])}</time></p>
  <div class="story-body">{paragraphs}</div>
  <dl class="record-meta"><dt>Record ID</dt><dd>{html.escape(row["record_id"])}</dd></dl>
</article>"""


def rss(rows: list[dict[str, str]]) -> str:
    items: list[str] = []
    for row in reversed(rows):
        url = f"{BASE_URL}/dispatches/{row['record_id']}.html"
        published = format_datetime(
            datetime.fromisoformat(row["published_at"].replace("Z", "+00:00"))
        )
        encoded_story = row["story"].replace("]]>", "]]]]><![CDATA[>")
        items.append(
            f"""    <item>
      <title>{escape(row["headline"])}</title>
      <link>{escape(url)}</link>
      <guid isPermaLink="false">{escape(row["record_id"])}</guid>
      <pubDate>{published}</pubDate>
      <dc:creator>{escape(row["publisher"])}</dc:creator>
      <description>{escape(row["story"][:280])}</description>
      <content:encoded><![CDATA[{encoded_story}]]></content:encoded>
    </item>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Riverton Civic Dispatch</title>
    <link>{BASE_URL}/</link>
    <description>Synthetic civic reporting fixture for Frisket walkthroughs.</description>
    <language>en-us</language>
    <lastBuildDate>{format_datetime(datetime.fromisoformat(rows[-1]["published_at"].replace("Z", "+00:00")))}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""


def build() -> None:
    rows = read_csv("dispatches.csv")
    contracts = read_csv("contracts.csv")
    if DIST.exists():
        shutil.rmtree(DIST)
    (SITE / "dispatches").mkdir(parents=True)
    (SITE / "assets").mkdir()
    (SITE / "lawsuits").mkdir()

    cards = []
    for row in reversed(rows):
        target = SITE / "dispatches" / f"{row['record_id']}.html"
        target.write_text(
            page(row["headline"], story_body(row), description=row["story"][:150]),
            encoding="utf-8",
        )
        cards.append(
            f"""<li><a href="{BASE_URL}/dispatches/{row["record_id"]}.html">
  <span class="card-date">{html.escape(row["published_at"][:10])}</span>
  <strong>{html.escape(row["headline"])}</strong>
  <span>{html.escape(row["story"][:170])}…</span>
</a></li>"""
        )

    index_body = f"""<section class="intro">
  <p class="eyebrow">Sample source</p>
  <h1>Follow the contracts shaping a fictional city</h1>
  <p>These {len(rows)} dispatches contain recurring agencies, vendors, people, disputed claims, corrections, and contract identifiers. Use the RSS feed or CSV snapshot to import them into Frisket.</p>
  <nav class="downloads"><a href="feed.xml">RSS feed</a><a href="dispatches.csv">Dispatches CSV</a><a href="contracts.csv">Contracts CSV</a><a href="lawsuits/">Lawsuit PDF lab</a></nav>
</section>
<ol class="story-list">{"".join(cards)}</ol>"""
    (SITE / "index.html").write_text(page("Home", index_body), encoding="utf-8")

    shutil.copy2(CONTENT / "dispatches.csv", SITE / "dispatches.csv")
    shutil.copy2(CONTENT / "contracts.csv", SITE / "contracts.csv")
    (SITE / "feed-v1.xml").write_text(rss(rows[:18]), encoding="utf-8")
    current_feed = rss(rows)
    (SITE / "feed-v2.xml").write_text(current_feed, encoding="utf-8")
    (SITE / "feed.xml").write_text(current_feed, encoding="utf-8")
    (SITE / "assets" / "site.css").write_text(STYLES, encoding="utf-8")

    lawsuit_source = CONTENT / "lawsuit-pdfs"
    lawsuit_files = sorted(lawsuit_source.glob("*.pdf"))
    lawsuit_links = "".join(
        f'<li><a href="{html.escape(path.name)}">{html.escape(path.name)}</a></li>'
        for path in lawsuit_files
    )
    for path in lawsuit_files:
        shutil.copy2(path, SITE / "lawsuits" / path.name)
    shutil.copy2(CONTENT / "court-docket.csv", SITE / "lawsuits" / "court-docket.csv")
    shutil.copy2(lawsuit_source / "README.txt", SITE / "lawsuits" / "README.txt")
    archive_path = SITE / "lawsuits" / "riverton-lawsuit-document-lab.zip"
    with zipfile.ZipFile(
        archive_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        archive.write(CONTENT / "court-docket.csv", "court-docket.csv")
        archive.write(lawsuit_source / "README.txt", "README.txt")
        for path in lawsuit_files:
            archive.write(path, path.name)
    lawsuit_body = f"""<section class="intro">
  <p class="eyebrow">Downloadable sample pack</p>
  <h1>Lawsuit document lab</h1>
  <p>Six fictional, searchable court filings with recurring vendors, city contracts, case numbers, deadlines, damages, and deliberately qualified claims.</p>
  <nav class="downloads"><a href="riverton-lawsuit-document-lab.zip">Download ZIP</a><a href="court-docket.csv">Court docket CSV</a><a href="README.txt">Walkthrough guide</a></nav>
</section><ul class="file-list">{lawsuit_links}</ul>"""
    (SITE / "lawsuits" / "index.html").write_text(
        page("Lawsuit document lab", lawsuit_body), encoding="utf-8"
    )
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    # A small machine-checkable build summary keeps accidental empty fixtures obvious.
    print(
        f"Built {len(rows)} dispatch pages, {len(contracts)} contracts, "
        f"{len(lawsuit_files)} lawsuit PDFs, and 2 feed snapshots"
    )


STYLES = """
:root { color-scheme: light; --ink:#25221d; --muted:#736d63; --paper:#fbfaf7; --line:#ddd8ce; --accent:#8b3d2e; }
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink); font:16px/1.6 Georgia,serif; }
a { color:inherit; }
.masthead { display:flex; justify-content:space-between; gap:1rem; padding:1rem max(1.25rem,calc((100vw - 980px)/2)); border-bottom:1px solid var(--line); font:13px/1.2 system-ui,sans-serif; color:var(--muted); }
.brand { color:var(--ink); font-weight:750; text-decoration:none; letter-spacing:.02em; }
main { width:min(760px,calc(100% - 2.5rem)); margin:4rem auto; }
.intro { margin-bottom:3rem; }
.eyebrow { margin:0 0 .5rem; color:var(--accent); font:700 12px/1.2 system-ui,sans-serif; letter-spacing:.1em; text-transform:uppercase; }
h1 { max-width:720px; margin:.25rem 0 1rem; font-size:clamp(2.2rem,6vw,4.5rem); line-height:1.02; letter-spacing:-.035em; }
.byline,.card-date { color:var(--muted); font:13px/1.4 system-ui,sans-serif; }
.story-body { margin-top:2.5rem; font-size:1.12rem; }
.story-body p:first-child::first-letter { float:left; padding:.08em .1em 0 0; color:var(--accent); font-size:3.5em; line-height:.78; }
.downloads { display:flex; flex-wrap:wrap; gap:.6rem; margin-top:1.5rem; }
.downloads a { padding:.55rem .8rem; border:1px solid var(--line); border-radius:4px; font:600 13px/1 system-ui,sans-serif; text-decoration:none; }
.story-list { padding:0; border-top:1px solid var(--line); list-style:none; }
.story-list li { border-bottom:1px solid var(--line); }
.story-list a { display:grid; grid-template-columns:8rem 1fr; gap:.3rem 1rem; padding:1.3rem 0; text-decoration:none; }
.story-list strong { font-size:1.2rem; line-height:1.25; }
.story-list span:last-child { grid-column:2; color:var(--muted); font-size:.94rem; }
.file-list { padding:0; border-top:1px solid var(--line); list-style:none; }
.file-list li { padding:.8rem 0; border-bottom:1px solid var(--line); font:14px/1.4 ui-monospace,monospace; overflow-wrap:anywhere; }
.record-meta { display:grid; grid-template-columns:max-content 1fr; gap:.25rem 1rem; margin-top:3rem; padding-top:1rem; border-top:1px solid var(--line); font:12px/1.5 system-ui,sans-serif; color:var(--muted); }
.record-meta dt { font-weight:700; }
.record-meta dd { margin:0; }
footer { width:min(760px,calc(100% - 2.5rem)); margin:5rem auto 2rem; padding-top:1rem; border-top:1px solid var(--line); color:var(--muted); font:12px/1.4 system-ui,sans-serif; }
@media (max-width:600px) { .masthead { align-items:flex-start; flex-direction:column; } main { margin-top:2.5rem; } .story-list a { grid-template-columns:1fr; } .story-list span:last-child { grid-column:1; } }
"""


if __name__ == "__main__":
    build()
