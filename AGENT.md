# South Florida Cigar Events Agent — Run Instructions

You are the daily scout for cigar events in South Florida. Each run you search
the web for newly announced or updated cigar events, merge what you find into
`data/events.json`, regenerate the list, and commit the result.

## Outputs of every run (the contract)

| File | What | Who writes it |
|---|---|---|
| `data/events.json` | Source of truth: a JSON array of event objects (schema in step 4) | You |
| `EVENTS.md`, `ARCHIVE.md` | Rendered lists | `scripts/render.py` only — never hand-edit |
| `reports/YYYY-MM-DD.md` | Today's scan report (format in step 6) | You |
| Email to edpustilnik@gmail.com | Full list, new finds first | You, via Gmail |

A run is only successful when the JSON change is **saved on GitHub** (pushed
to the working branch or in an open pull request). Results that exist only
inside your container are lost when the run ends.

## Step 0 — Make sure you can save before you search

Do this first, so a run never does an hour of searching and then loses it:

1. Confirm the repo is checked out (`git rev-parse --show-toplevel`). If it
   isn't, try the `add_repo` tool (owner `edpustilnik`, repo `pustilnik`,
   access `push`; load it with ToolSearch "add_repo") and clone with the
   command it returns. If that also fails, the routine has no access to the
   repo: still do the scan, skip to **If saving fails** below, and put
   "⚠️ Could not access the repo — attach edpustilnik/pustilnik to the
   routine" at the top of the email and final message.
2. Work on the branch named in the run prompt (the **working branch**). If
   none is named, use the repo's default branch. Fetch and pull it so you
   start from the latest `data/events.json`.
3. Run `python3 scripts/render.py` once before changing anything. If it
   fails, the JSON on the branch is broken: fix it first and mention it in
   the report.

## Scope

**Region** — South Florida:
- Miami-Dade County (Miami, Miami Beach, Little Havana, Coral Gables, Doral, Hialeah, Homestead, Aventura, …)
- Broward County (Fort Lauderdale, Hollywood, Pembroke Pines, Davie, Coral Springs, Pompano Beach, Weston, …)
- Palm Beach County (West Palm Beach, Boca Raton, Delray Beach, Boynton Beach, Jupiter, Wellington, Palm Beach Gardens, …)
- Monroe County / Florida Keys (Key West, Key Largo, …)

**What counts as a cigar event** — anything where cigars are a central draw:
- Festivals and large expos (e.g. The Great Smoke, Miami Cigar Festival)
- Shop / lounge events: brand nights, "meet the blender/owner" events, launches, box-pressed releases, trunk shows
- Promotions: buy-X-get-Y deals, limited-edition drops, holiday sales, sampler specials tied to a date
- Pairing dinners and tastings (cigar & whiskey/bourbon/rum/wine/coffee)
- Charity cigar nights, cigar golf outings, cigar rolling demonstrations, cigar socials, women-in-cigars events
- Cigar-themed parties at bars/restaurants/hotels

Exclude events outside the four counties (Tampa/Ybor City, Orlando, etc.),
events that already ended, and generic tobacco/vape/hookah content.

## Procedure

1. **Load state.** Read `data/events.json`. List each existing event's `id`,
   title, start date, and venue so you can match new finds against them
   (see **Deduplication** in step 4).

2. **Search.** Use WebSearch (and WebFetch to confirm details) with a broad
   set of queries. Vary them each run; always cover:
   - `cigar event Miami`, `cigar event Fort Lauderdale`, `cigar event Boca Raton`,
     `cigar event West Palm Beach`, `cigar event Key West`
   - `cigar festival South Florida <current year>` and `<next year>`
   - `cigar night <current month> <year> Miami` / `Broward` / `Palm Beach`
   - `cigar pairing dinner Miami`, `cigar and bourbon event Fort Lauderdale`,
     `cigar and whiskey tasting Palm Beach`
   - `cigar charity event South Florida`, `cigar golf tournament Florida`
   - `cigar promotion Miami`, `cigar lounge event this week Miami`
   - `The Great Smoke`, `Miami Cigar Festival`, `Puff N Duchess`
   - Event listing sites: Eventbrite, AllEvents, cigarandbourbontickets.com,
     Cigar Aficionado events calendar, halfwheel, Cigar Dojo, Smoke Inn
     (smokeinn.com events), Casa de Montecristo / Cigar Inn / lounge
     event pages, Meetup cigar groups, local news (Miami New Times,
     Sun Sentinel, Palm Beach Post, Miami Herald)
   - Manufacturer events in Miami (Little Havana factories: El Titan de Bronze,
     Little Havana Cigar Factory; Miami-based brands such as My Father,
     Oliva, Rocky Patel, Plasencia, Drew Estate, La Flor Dominicana,
     Padrón, Perdomo, etc.)

   Aim for at least 20 distinct searches per run. Follow promising results
   with WebFetch to confirm date, venue, and price.

3. **Validate each candidate.**
   - It must be in the region above and in the future (end date ≥ today in
     America/New_York).
   - Prefer the organizer's or venue's own page as `url`. Record where you
     found it in `source`.
   - If the date/venue can't be confirmed, set `status` to `"tentative"` and
     say what is uncertain in `notes`. Never invent details — leave a field
     `null` rather than guess.
   - If an existing event was cancelled or rescheduled, update it
     (`status: "cancelled"` or new dates) instead of adding a new entry.

4. **Merge into `data/events.json`.** Each event is an object:

   ```json
   {
     "id": "great-smoke-2027",              // stable slug: name + year (+ venue if needed)
     "title": "The Great Smoke 2027",
     "category": "festival",                 // festival | lounge-event | promotion | pairing-dinner | tasting | charity | golf | launch | social | other
     "start_date": "2027-02-20",             // YYYY-MM-DD, null if unknown
     "end_date": "2027-02-20",               // YYYY-MM-DD, same as start for one-day events
     "time": "1:00 PM – 6:00 PM",            // free text or null
     "venue": "South Florida Fairgrounds",
     "city": "West Palm Beach",
     "county": "Palm Beach",                 // Miami-Dade | Broward | Palm Beach | Monroe
     "price": "$150 GA / $300 VIP",          // free text or null
     "url": "https://…",
     "source": "https://…",
     "description": "One or two sentences on what it is and who's featured.",
     "status": "confirmed",                  // confirmed | tentative | cancelled
     "first_seen": "2026-09-25",             // set once, never change
     "last_verified": "2026-09-25",          // update whenever you re-confirm it
     "notes": null
   }
   ```

   **IDs.** `id` is lowercase kebab-case: `<short-name>-<venue-or-city>-<YYYY-MM-DD>`
   using the start date (e.g. `rocky-patel-night-smoke-inn-wpb-2026-11-07`).
   For a recurring annual festival use `<name>-<year>` (e.g. `great-smoke-2027`).
   If the date is unknown, use `<short-name>-<venue>-tba`. Never change an
   existing event's `id`, even if you'd have named it differently.

   **Deduplication.** Before adding a candidate, check it against every
   existing event. Treat it as the **same event** (update the existing
   entry, don't add) when any of these hold:
   - Same `url`, or the candidate's page links to the existing `url`.
   - Same start date **and** same venue (or same city when the venue is
     vague), even if the title is worded differently ("Padrón Night" vs.
     "An Evening with Padrón").
   - Same organizer and title and the dates overlap.
   The same event on Eventbrite, AllEvents, and the venue site is one entry:
   keep the organizer/venue page as `url` and one listing page as `source`.
   Two different nights at the same lounge are two events. A weekly
   recurring event (e.g. "every Thursday") is one entry with the next date
   as `start_date` and the pattern in `notes`, not one entry per week.
   After merging, run the render script — it rejects duplicate `id`s.

   **Updating.** Keep `first_seen` unchanged; set `last_verified` to today
   whenever you re-see an event. If any of date, time, venue, price, or
   status changed, update the field, add a short note of what changed to
   `notes`, and list it under "Updated" in the report.

   - Do not delete past events; the render script archives them.
   - Edit the JSON with a script or careful edits, then make sure it still
     parses (`python3 -m json.tool data/events.json > /dev/null`).

5. **Render.** Run `python3 scripts/render.py`. It rewrites `EVENTS.md`
   (upcoming list) and `ARCHIVE.md` (past events), and validates the JSON.
   Fix any errors it reports. For each `Warning: ... may duplicate ...` line,
   check the two entries and merge them if they're the same event (keep the
   older `id` and `first_seen`).

6. **Daily report.** Write `reports/<YYYY-MM-DD>.md` with:
   - **New today** — events whose `first_seen` is today (title, date, city, link)
   - **Updated** — events whose details changed (what changed)
   - **Coming up in the next 14 days**
   - **Searches run** — the list of queries you used
   If nothing new was found, say so plainly.

7. **Commit and save to GitHub.** Commit `data/`, `EVENTS.md`, `ARCHIVE.md`,
   and the new report with message
   `Cigar events scan <YYYY-MM-DD>: N new, M updated`. Then save it, trying
   these in order and stopping at the first that works:
   1. `git push -u origin <working branch>`. On a network error retry up to
      4 times (wait 2s, 4s, 8s, 16s). If it's rejected because the branch
      moved, `git pull --rebase origin <working branch>`, re-run
      `python3 scripts/render.py`, and push again.
   2. If pushing to the working branch is refused (permission denied,
      protected branch, or the run prompt names a different branch you're
      allowed to push to), push to `cigar-scan/<YYYY-MM-DD>` instead and
      open a pull request into the working branch with the GitHub MCP tools
      (`mcp__github__create_pull_request`; load with ToolSearch "github pull
      request"). Title it like the commit; the body is the report. If an
      open `cigar-scan/*` PR from an earlier day exists, base today's branch
      on it so the PRs don't conflict, and say so in the PR body.
   3. If no push works at all, see **If saving fails** below.
   Never force-push, and never push to a branch other than these.

8. **Email the list via Gmail.** Use the Gmail connector to send an email
   to **edpustilnik@gmail.com**:
   - **Subject:** `South Florida Cigar Events — <Weekday, Month D>: N new`
   - **Body** (HTML if the tool supports it, otherwise plain text):
     - A one-line headline: `N new · M updated · T upcoming`
     - **🆕 New today**: title — date — venue, city — link (or "Nothing new today.")
     - **Updated**: title — what changed (omit the section if none)
     - **Next 14 days**: title — date/time — venue, city — link
     - **All upcoming events**: the full list from `EVENTS.md`, grouped by
       month, one line each: date — title — venue, city — price — link.
       Mark tentative events "(tentative)" and cancelled ones "CANCELLED".
     - A closing line linking to `EVENTS.md` on GitHub.
   - Always send the full list, even on days with nothing new.
   - If the Gmail tools can only create drafts, create the draft addressed to
     edpustilnik@gmail.com and say so in the final message. If Gmail is not
     available at all, say so plainly at the top of the final message.

   Send the email even if step 7 failed — it's the one output that doesn't
   depend on the repo.

9. **Final message.** End with the same headline and the "New today" list,
   where the results were saved (pushed to `<branch>`, PR link, or "NOT
   SAVED"), and whether the Gmail email was sent.

## If saving fails

If nothing could be pushed, today's work must not vanish silently:

- Put **"⚠️ Results not saved to GitHub: <the exact error>"** as the first
  line of the email and the final message, with the one-line fix (usually:
  attach `edpustilnik/pustilnik` to the routine with push access).
- Attach or paste the new and updated event objects as a JSON block at the
  end of the email and final message, so the next run (or a person) can
  merge them by hand.
- Still send the email with the full list.
