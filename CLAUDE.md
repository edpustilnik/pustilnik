# pustilnik — South Florida cigar events agent

A scheduled Claude Code Routine runs daily, searches the web for cigar events
in South Florida (Miami-Dade, Broward, Palm Beach, Monroe), and keeps a list.

- `AGENT.md` — the full procedure each run follows. Read it first on a scan run.
- `data/events.json` — source of truth for all events (never hand-edit the Markdown lists).
- `scripts/render.py` — validates the JSON and regenerates `EVENTS.md` and `ARCHIVE.md`.
- `reports/YYYY-MM-DD.md` — one scan report per day.
