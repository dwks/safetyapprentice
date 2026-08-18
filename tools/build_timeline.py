#!/usr/bin/env python3
"""Regenerate the event cards in templates/pages/timeline.html from
timeline-events.json. The JSON is the source of truth for the events; the
page's CSS, hero, filters and script stay hand-maintained in the template.

    python3 tools/build_timeline.py            # rewrite the template
    python3 tools/build_timeline.py --check    # exit 1 if it is out of date

Descriptions and titles carry intentional inline markup (<strong>, <em>) and
are emitted verbatim, so the JSON is trusted input — treat it like template
source, not like user data.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
DATA = ROOT / "timeline-events.json"
PAGE = ROOT / "templates" / "pages" / "timeline.html"

# The generated region is everything inside <div class="timeline" id="timeline">.
OPEN = '  <div class="timeline" id="timeline">\n'
# Leading newline matters: a bare '  </div>' also matches inside a card's
# '      </div>', which would bind the close anchor to the first card.
CLOSE = '\n  </div>\n'

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

BANNER = "    <!-- ============ {year} ============ -->\n"


def date_key(event: dict) -> tuple:
    """(year, month, day) — day is 0 when the date names only a month.

    Only used to sanity-check ordering. A month-only date carries no day, so
    it cannot be placed against a dated event in the same month ("May 2023"
    is the 30th; "9 May 2023" is the 9th) — the JSON's order is the authority.
    """
    m = re.fullmatch(r"(?:(\d{1,2})\s+)?([A-Za-z]+)\s+(\d{4})", event["date"].strip())
    if not m:
        sys.exit(f"unparseable date {event['date']!r} on {event['id']}")
    day, month, year = m.groups()
    if month not in MONTHS:
        sys.exit(f"unknown month {month!r} on {event['id']}")
    if int(year) != event["year"]:
        sys.exit(f"{event['id']}: date says {year}, year field says {event['year']}")
    return int(year), MONTHS.index(month) + 1, int(day or 0)


def card(event: dict) -> str:
    """One .tl-item block, matching the markup the page already uses."""
    meta = (f'<div class="tl-meta"><span class="tl-date">{event["date"]}</span>'
            f'<span class="tl-type">{event["badge"]}</span></div>')
    body = [f'        {meta}\n',
            f'        <h3 class="tl-title">{event["title"]}</h3>\n',
            f'        <p class="tl-desc">{event["description"]}</p>\n']

    out = [f'    <div class="tl-item {event["category"]} fade-in">\n']
    if event["url"]:
        href = html.escape(event["url"], quote=True)
        out.append(f'      <a class="tl-card" href="{href}" target="_blank" rel="noopener noreferrer">\n')
        out += body
        if event["link_text"]:
            out.append(f'        <span class="tl-src">{event["link_text"]}</span>\n')
        out.append('      </a>\n')
    else:
        out.append('      <div class="tl-card">\n')
        out += body
        out.append('      </div>\n')
    out.append('    </div>\n')
    return "".join(out)


def render(events: list) -> str:
    out, year = [], None
    for event in events:
        if event["year"] != year:
            year = event["year"]
            out.append(BANNER.format(year=year))
            out.append(f'    <h2 class="tl-year">{year}</h2>\n\n')
        out.append(card(event))
        out.append("\n")
    return "".join(out)


def validate(events: list) -> None:
    seen = set()
    for e in events:
        missing = [k for k in ("id", "year", "date", "badge", "category", "title",
                               "description") if not e.get(k)]
        if missing:
            sys.exit(f"{e.get('id', '?')}: missing {', '.join(missing)}")
        if e["id"] in seen:
            sys.exit(f"duplicate id: {e['id']}")
        seen.add(e["id"])
        if e["link_text"] and not e["url"]:
            sys.exit(f"{e['id']}: has link_text but no url")
        for field in ("title", "description"):
            text = e[field]
            for tag in ("strong", "em"):
                if text.count(f"<{tag}>") != text.count(f"</{tag}>"):
                    sys.exit(f"{e['id']}: unbalanced <{tag}> in {field}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="do not write; exit 1 if the template is out of date")
    args = ap.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    events = data["events"]
    validate(events)

    # Emit in JSON order: it is hand-curated, and month-only dates cannot be
    # ordered against dated ones automatically. Years must still ascend, or the
    # year headings would repeat.
    ordered = events
    years = [e["year"] for e in ordered]
    if years != sorted(years):
        sys.exit("events are not grouped in ascending year order — fix the JSON")
    for prev, cur in zip(ordered, ordered[1:]):
        if prev["year"] == cur["year"] and date_key(prev)[1] > date_key(cur)[1]:
            print(f"note: {cur['id']} ({cur['date']}) precedes {prev['id']} "
                  f"({prev['date']}) by month", file=sys.stderr)

    page = PAGE.read_text(encoding="utf-8")
    head, sep, rest = page.partition(OPEN)
    if not sep:
        sys.exit(f"could not find the timeline container in {PAGE}")
    body, sep, tail = rest.partition(CLOSE)
    if not sep:
        sys.exit(f"could not find the end of the timeline container in {PAGE}")

    updated = head + OPEN + "\n" + render(ordered).rstrip("\n") + "\n" + CLOSE + tail

    if args.check:
        if updated != page:
            sys.exit(f"{PAGE.relative_to(ROOT)} is out of date — "
                     f"run python3 tools/build_timeline.py")
        print(f"{PAGE.relative_to(ROOT)} is up to date ({len(events)} events)")
        return

    if updated == page:
        print(f"{PAGE.relative_to(ROOT)} already up to date ({len(events)} events)")
        return

    PAGE.write_text(updated, encoding="utf-8")
    years = sorted({e["year"] for e in events})
    print(f"wrote {PAGE.relative_to(ROOT)}: {len(events)} events, "
          f"{len(years)} years ({years[0]}–{years[-1]})")


if __name__ == "__main__":
    main()
