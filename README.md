# Frisket samples

Public sample datasets and hosted source fixtures for Frisket walkthroughs.

The first fixture is the fictional **Riverton Civic Dispatch**, available as
ordinary web pages, RSS snapshots, and downloadable CSV files. All people,
organizations, events, and records in this fixture are synthetic.

## Local preview

```sh
python scripts/build_site.py
python -m http.server --directory dist 8000
```

Then open <http://localhost:8000/riverton/>. Local hosting is only for visual
preview; Frisket's URL and RSS importers intentionally reject loopback URLs.

## Published paths

- `/riverton/` — story index
- `/riverton/feed.xml` — current RSS feed
- `/riverton/feed-v1.xml` — earlier feed snapshot
- `/riverton/feed-v2.xml` — current versioned snapshot
- `/riverton/dispatches.csv` and `/riverton/contracts.csv` — offline imports
- `/riverton/lawsuits/` — searchable PDF pack, docket CSV, and short guide
- `/riverton/council-audio/` — local MP3 excerpts, provenance, and guide

GitHub Pages deploys the generated `dist` directory after changes merge to
`main`.
