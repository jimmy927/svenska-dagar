"""Swedish holiday rules, built from the law on public holidays (1989:253) and
the de facto days off (midsommarafton, julafton, nyårsafton).

The rules are laid out as one table per year: every special date of the year
mapped to an ``_Entry``.  Where two rules hit the same date the first one added
wins, in the same order of precedence the Svenska Dagar API uses.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import NamedTuple

WEEKDAYS = ("Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag")


@dataclass(frozen=True, slots=True)
class DayInfo:
    """What the Svenska Dagar API v2.1 tells about one day."""

    datum: date
    veckodag: str
    vecka: int
    arbetsfri_dag: bool
    rod_dag: bool
    helgdag: str | None
    helgdagsafton: str | None
    klamdag: bool
    dag_fore_arbetsfri_helgdag: bool


class _Entry(NamedTuple):
    is_helgdag: bool  # reported as "helgdag" (else as "helgdagsafton")
    name: str
    free: bool  # arbetsfri dag
    red: bool  # röd dag


def easter_sunday(year: int) -> date:
    """Gregorian Easter (Meeus/Jones/Butcher computus)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    g = (b - (b + 8) // 25 + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


@lru_cache(maxsize=64)
def _year_table(year: int) -> dict[date, _Entry]:
    table: dict[date, _Entry] = {}

    def add(day: date, is_helgdag: bool, name: str, free: bool, red: bool) -> None:
        table.setdefault(day, _Entry(is_helgdag, name, free, red))

    # Midsommar: the Saturday from 20 to 26 June, and the Friday before it.
    midsummer = date(year, 6, 20)
    midsummer += timedelta(days=(5 - midsummer.weekday()) % 7)
    add(midsummer - timedelta(days=1), True, "Midsommarafton", True, False)
    add(midsummer, True, "Midsommardagen", True, True)

    # Easter and what hangs on it.
    easter = easter_sunday(year)
    ascension = easter + timedelta(days=39)
    ascension_name = "Kristi himmelsfärdsdag"
    if (ascension.month, ascension.day) == (4, 30):
        ascension_name += ", Valborgsmässoafton"
    elif (ascension.month, ascension.day) == (5, 1):
        ascension_name += ", Första Maj"
    whit_monday_off = year < 2005  # Annandag pingst stopped being a day off in 2005
    add(easter - timedelta(days=3), False, "Skärtorsdagen", False, False)
    add(easter - timedelta(days=2), True, "Långfredagen", True, True)
    add(easter - timedelta(days=1), True, "Påskafton", True, False)
    add(easter, True, "Påskdagen", True, True)
    add(easter + timedelta(days=1), True, "Annandag påsk", True, True)
    add(ascension, True, ascension_name, True, True)
    add(easter + timedelta(days=48), False, "Pingstafton", True, False)
    add(easter + timedelta(days=49), True, "Pingstdagen", True, True)
    whit_monday = easter + timedelta(days=50)
    # From 2005 Annandag pingst is no holiday, so it must not hide Sveriges nationaldag
    # (the API let it; before 2005 it is a day off and wins, as in the API).
    if whit_monday_off or (whit_monday.month, whit_monday.day) != (6, 6):
        add(whit_monday, True, "Annandag pingst", whit_monday_off, whit_monday_off)

    # Alla helgons dag: the Saturday from 31 October to 6 November, and the Friday before it.
    all_saints = date(year, 10, 31)
    all_saints += timedelta(days=(5 - all_saints.weekday()) % 7)
    add(all_saints - timedelta(days=1), False, "Allhelgonaafton", False, False)
    add(all_saints, True, "Alla helgons dag", True, True)

    # Fixed dates.
    add(date(year, 1, 1), True, "Nyårsdagen", True, True)
    add(date(year, 1, 5), False, "Trettondagsafton", False, False)
    add(date(year, 1, 6), True, "Trettondedag jul", True, True)
    add(date(year, 4, 30), False, "Valborgsmässoafton", False, False)
    add(date(year, 5, 1), True, "Första Maj", True, True)
    if year >= 2005:
        add(date(year, 6, 6), True, "Sveriges nationaldag", True, True)
    elif year >= 1983:
        add(date(year, 6, 6), True, "Sveriges nationaldag", False, False)
    else:
        add(date(year, 6, 6), True, "Svenska flaggans dag", False, False)
    add(date(year, 12, 24), True, "Julafton", True, False)
    add(date(year, 12, 25), True, "Juldagen", True, True)
    add(date(year, 12, 26), True, "Annandag jul", True, True)
    add(date(year, 12, 31), True, "Nyårsafton", True, False)
    return table


def _check_date(day: date) -> None:
    """Reject anything but a plain ``datetime.date``.

    A ``datetime`` is a ``date`` subclass, but accepting it would silently drop its time
    and time zone, so it is refused along with strings, ``None`` and the rest.
    """
    if isinstance(day, datetime) or not isinstance(day, date):
        raise TypeError(
            f"expected a datetime.date, got {type(day).__name__}"
            " (pass a datetime.datetime as .date())"
        )


def _entry(day: date) -> _Entry | None:
    return _year_table(day.year).get(day)


def _is_free(day: date) -> bool:
    entry = _entry(day)
    return day.weekday() >= 5 or (entry is not None and entry.free)


def _neighbour(day: date, days: int) -> date | None:
    try:
        return day + timedelta(days=days)
    except OverflowError:
        return None


def _free_neighbour(day: date, days: int) -> bool:
    other = _neighbour(day, days)
    return other is not None and _is_free(other)


def day_info(day: date) -> DayInfo:
    """Everything the Svenska Dagar API v2.1 says about ``day``.

    Raises ``TypeError`` unless ``day`` is a ``datetime.date``; a ``datetime.datetime`` is
    refused too, so no time or time zone is dropped silently (use ``dt.date()``).
    """
    _check_date(day)
    entry = _entry(day)
    free = _is_free(day)
    tomorrow = _neighbour(day, 1)
    tomorrow_entry = _entry(tomorrow) if tomorrow else None
    return DayInfo(
        datum=day,
        veckodag=WEEKDAYS[day.weekday()],
        vecka=day.isocalendar()[1],
        arbetsfri_dag=free,
        rod_dag=day.weekday() == 6 or (entry is not None and entry.red),
        helgdag=entry.name if entry and entry.is_helgdag else None,
        helgdagsafton=entry.name if entry and not entry.is_helgdag else None,
        klamdag=not free and _free_neighbour(day, -1) and _free_neighbour(day, 1),
        dag_fore_arbetsfri_helgdag=not free and tomorrow_entry is not None and tomorrow_entry.is_helgdag,
    )


def is_workday(day: date) -> bool:
    """True when ``day`` is not a weekend day or a day off.

    Raises ``TypeError`` for anything but a ``datetime.date`` (``datetime.datetime`` included).
    """
    _check_date(day)
    return not _is_free(day)


def holiday_name(day: date) -> str | None:
    """The API's ``helgdag`` name for ``day``, or None (eves reported only as ``helgdagsafton`` give None).

    Raises ``TypeError`` for anything but a ``datetime.date`` (``datetime.datetime`` included).
    """
    _check_date(day)
    entry = _entry(day)
    return entry.name if entry and entry.is_helgdag else None
