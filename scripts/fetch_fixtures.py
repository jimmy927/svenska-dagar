"""One-off: fetch golden fixtures from the live Svenska Dagar API (v2.1).

Tests never run this. Usage: python scripts/fetch_fixtures.py [YEAR ...] [extra]
Writes tests/fixtures/<year>.json (whole years, via the month endpoint) and
tests/fixtures/extra.json (the single days in EXTRA_DAYS).

Only the holiday-related fields are kept; name days and flag days are dropped.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://sholiday.faboul.se/dagar/v2.1"
FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
KEEP = (
    "datum",
    "veckodag",
    "arbetsfri dag",
    "röd dag",
    "vecka",
    "helgdag",
    "helgdagsafton",
    "klämdag",
    "dag före arbetsfri helgdag",
)

# Pre-2005 and the flag-day era (1980, 1982, 1983), the 2005 switch, Kristi
# himmelsfärd on 1 May (2008), midsummer edges (20 and 26 June on a Saturday:
# 2009/2015/2020/2026 and 2004/2010/2021), All Saints edges (31 Oct and 6 Nov
# on a Saturday: 2009/2015/2020 and 2004/2010/2021), Easter at its latest
# (2038), and recent years.
YEARS = [1980, 1982, 1983, 1995, 2004, 2005, 2008, 2009, 2010, 2015,
         2020, 2021, 2022, 2024, 2025, 2026, 2027, 2038]

# Single days that whole-year fixtures do not reach: Kristi himmelsfärd on
# 30 April (Easter on 22 March, 2285), and Whitsun days that fall on 6 June
# (Pingstafton, Pingstdagen, Annandag pingst shadow the national day; 2022 is
# in the year fixtures).
EXTRA_DAYS = [
    "2285-04-29", "2285-04-30", "2285-05-01",
    "1981-06-06", "1987-06-06", "1992-06-06",  # Pingstafton
    "2033-06-06", "2044-06-06",  # Annandag pingst
    "2049-06-06", "2060-06-06",  # Pingstdagen
    "2071-06-06",  # Pingstafton
]


def get(path: str) -> dict:
    request = urllib.request.Request(BASE + path, headers={"User-Agent": "svenska-dagar fixture fetch"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    time.sleep(0.5)
    # Working days come with a PHP notice before the JSON.
    return json.loads(body[body.index("{"):])


def keep(day: dict) -> dict:
    return {k: day[k] for k in KEEP if k in day}


def dump(name: str, days: list[dict]) -> None:
    (FIXTURES / name).write_text(json.dumps(days, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(name, len(days), "days", flush=True)


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    args = sys.argv[1:]
    years = [int(a) for a in args if a.isdigit()] or ([] if "extra" in args else YEARS)
    for year in years:
        days: list[dict] = []
        for month in range(1, 13):
            days += [keep(d) for d in get(f"/{year}/{month:02d}")["dagar"]]
        dump(f"{year}.json", days)
    if not args or "extra" in args:
        extra: list[dict] = []
        for iso in EXTRA_DAYS:
            year, month, day = iso.split("-")
            extra += [keep(d) for d in get(f"/{year}/{month}/{day}")["dagar"]]
        dump("extra.json", extra)


if __name__ == "__main__":
    main()
