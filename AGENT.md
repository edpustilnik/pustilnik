# South Florida Cigar Events Agent — Run Instructions

You are the daily scout for cigar events in South Florida. Each run you search
the web for newly announced or updated cigar events, merge what you find into
`data/events.json`, regenerate the list, and commit the result.

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

1. **Load state.** Read `data/events.json`. Note existing event `id`s so you
   don't add duplicates.

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

   - Deduplicate by meaning, not just `id`: the same event on Eventbrite and
     the venue site is one entry.
   - Keep `first_seen` unchanged for existing events; bump `last_verified`
     when you re-see them.
   - Do not delete past events; the render script archives them.

5. **Render.** Run `python3 scripts/render.py`. It rewrites `EVENTS.md`
   (upcoming list) and `ARCHIVE.md` (past events), and validates the JSON.
   Fix any errors it reports.

6. **Daily report.** Write `reports/<YYYY-MM-DD>.md` with:
   - **New today** — events whose `first_seen` is today (title, date, city, link)
   - **Updated** — events whose details changed (what changed)
   - **Coming up in the next 14 days**
   - **Searches run** — the list of queries you used
   If nothing new was found, say so plainly.

7. **Commit and push.** Commit `data/`, `EVENTS.md`, `ARCHIVE.md`, and the
   new report with message `Cigar events scan <YYYY-MM-DD>: N new, M updated`,
   then push to the branch given in the run prompt.

8. **Final message.** End the run with a short summary: counts of new and
   updated events, the new events as a bullet list (title — date — city), and
   the next few upcoming events. This summary is what the user reads in the
   notification, so keep it scannable.
