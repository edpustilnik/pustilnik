# South Florida Cigar Events

A daily agent that scouts the web for cigar events in South Florida —
festivals, lounge nights, brand launches, pairing dinners, promotions,
charity and golf events — and keeps them in one list.

**👉 The list: [EVENTS.md](EVENTS.md)**

## How it works

A Claude Code Routine fires every morning. Each run:

1. Reads [`AGENT.md`](AGENT.md) for the search procedure and scope
   (Miami-Dade, Broward, Palm Beach, and the Keys).
2. Runs 20+ web searches across event sites, lounges, manufacturers, and local news,
   confirming details on the source pages.
3. Merges new or changed events into [`data/events.json`](data/events.json),
   de-duplicating against what's already there.
4. Runs `python3 scripts/render.py` to rebuild [`EVENTS.md`](EVENTS.md) and
   [`ARCHIVE.md`](ARCHIVE.md).
5. Writes a daily report to [`reports/`](reports/) and commits everything.

## Changing it

- **What it looks for / where** — edit the Scope and search list in `AGENT.md`.
- **Schedule, or pausing it** — edit the Routine at claude.ai/code (Routines).
- **Run it manually** — `python3 scripts/render.py` re-renders the list from the JSON;
  a full scan is triggered by running the Routine on demand.
