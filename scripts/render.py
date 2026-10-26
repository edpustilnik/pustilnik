#!/usr/bin/env python3
"""Validate data/events.json and render EVENTS.md (upcoming) and ARCHIVE.md (past)."""

import json
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "events.json"
EVENTS_MD = ROOT / "EVENTS.md"
ARCHIVE_MD = ROOT / "ARCHIVE.md"

REQUIRED = ["id", "title", "category", "start_date", "end_date", "city", "county",
            "url", "status", "first_seen", "last_verified"]
CATEGORIES = {"festival", "lounge-event", "promotion", "pairing-dinner", "tasting",
              "charity", "golf", "launch", "social", "other"}
COUNTIES = {"Miami-Dade", "Broward", "Palm Beach", "Monroe"}
STATUSES = {"confirmed", "tentative", "cancelled"}


def parse_date(value):
    return date.fromisoformat(value) if value else None


def validate(events):
    errors = []
    seen = set()
    for i, ev in enumerate(events):
        label = ev.get("id") or f"#{i}"
        for key in REQUIRED:
            if key not in ev:
                errors.append(f"{label}: missing field '{key}'")
        if ev.get("id") in seen:
            errors.append(f"{label}: duplicate id")
        seen.add(ev.get("id"))
        if ev.get("category") not in CATEGORIES:
            errors.append(f"{label}: category must be one of {sorted(CATEGORIES)}")
        if ev.get("county") not in COUNTIES:
            errors.append(f"{label}: county must be one of {sorted(COUNTIES)}")
        if ev.get("status") not in STATUSES:
            errors.append(f"{label}: status must be one of {sorted(STATUSES)}")
        for key in ("start_date", "end_date", "first_seen", "last_verified"):
            try:
                parse_date(ev.get(key))
            except (TypeError, ValueError):
                errors.append(f"{label}: {key} must be YYYY-MM-DD or null")
    return errors


def possible_duplicates(events):
    """Pairs that look like the same event under different ids (warn, don't fail)."""
    warnings = []
    by_url, by_slot = {}, {}
    for ev in events:
        if ev.get("status") == "cancelled":
            continue
        url = (ev.get("url") or "").rstrip("/").lower()
        slot = (ev.get("start_date"), (ev.get("venue") or ev.get("city") or "").strip().lower())
        for key, index in ((url, by_url), (slot if slot[0] else None, by_slot)):
            if not key:
                continue
            if key in index:
                warnings.append(f"{ev['id']} may duplicate {index[key]} (same {'url' if index is by_url else 'date and venue'})")
            else:
                index[key] = ev["id"]
    return warnings


def end_of(ev):
    return parse_date(ev.get("end_date")) or parse_date(ev.get("start_date"))


def fmt_dates(ev):
    start, end = parse_date(ev.get("start_date")), parse_date(ev.get("end_date"))
    if not start:
        return "Date TBA"
    text = start.strftime("%a %b %-d, %Y")
    if end and end != start:
        text += " – " + end.strftime("%a %b %-d, %Y")
    return text


def row(ev, today):
    title = f"[{ev['title']}]({ev['url']})" if ev.get("url") else ev["title"]
    flags = []
    if ev.get("first_seen") == today.isoformat():
        flags.append("🆕")
    if ev["status"] == "tentative":
        flags.append("_(tentative)_")
    if ev["status"] == "cancelled":
        title = f"~~{title}~~"
        flags.append("**CANCELLED**")
    where = ", ".join(x for x in (ev.get("venue"), ev.get("city")) if x)
    cells = [
        fmt_dates(ev) + (f"<br>{ev['time']}" if ev.get("time") else ""),
        f"{title} {' '.join(flags)}".strip(),
        ev["category"],
        f"{where}<br>_{ev['county']}_",
        ev.get("price") or "—",
        (ev.get("description") or "").replace("|", "\\|").replace("\n", " "),
    ]
    return "| " + " | ".join(cells) + " |"


HEADER = ["| When | Event | Type | Where | Price | Details |",
          "|---|---|---|---|---|---|"]


def sort_key(ev):
    return (parse_date(ev.get("start_date")) or date.max, ev["title"])


def main():
    events = json.loads(DATA.read_text())
    errors = validate(events)
    if errors:
        print("Validation errors:", *errors, sep="\n  ")
        sys.exit(1)
    for warning in possible_duplicates(events):
        print(f"Warning: {warning}")

    today = datetime.now(ZoneInfo("America/New_York")).date()
    upcoming = sorted([e for e in events if not end_of(e) or end_of(e) >= today], key=sort_key)
    past = sorted([e for e in events if end_of(e) and end_of(e) < today], key=sort_key, reverse=True)

    lines = [
        "# South Florida Cigar Events",
        "",
        f"_Last updated {today:%A, %B %-d, %Y} · {len(upcoming)} upcoming · "
        "Miami-Dade, Broward, Palm Beach & the Keys_",
        "",
        "🆕 = found in today's scan. Past events move to [ARCHIVE.md](ARCHIVE.md); "
        "daily scan notes are in [reports/](reports/).",
        "",
    ]

    # upcoming already excludes ended events, so this also catches ones in progress
    soon = [e for e in upcoming if parse_date(e.get("start_date"))
            and parse_date(e["start_date"]) <= today + timedelta(days=14)]
    lines += ["## Next 14 days", ""]
    lines += (HEADER + [row(e, today) for e in soon]) if soon else ["_Nothing on the calendar yet._"]
    lines.append("")

    by_month = defaultdict(list)
    for ev in upcoming:
        start = parse_date(ev.get("start_date"))
        by_month[start.strftime("%B %Y") if start else "Date TBA"].append(ev)
    lines += ["## All upcoming events", ""]
    if not upcoming:
        lines += ["_No upcoming events recorded yet._", ""]
    for month, evs in by_month.items():
        lines += [f"### {month}", ""] + HEADER + [row(e, today) for e in evs] + [""]

    EVENTS_MD.write_text("\n".join(lines))

    archive = ["# Past South Florida Cigar Events", ""]
    archive += (HEADER + [row(e, today) for e in past]) if past else ["_None yet._"]
    ARCHIVE_MD.write_text("\n".join(archive) + "\n")

    new_today = sum(1 for e in events if e.get("first_seen") == today.isoformat())
    print(f"OK: {len(upcoming)} upcoming, {len(past)} past, {new_today} new today")


if __name__ == "__main__":
    main()
