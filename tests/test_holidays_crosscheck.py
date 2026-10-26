"""Cross-check ``arbetsfri_dag`` against the ``holidays`` package (dev dependency only)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

holidays = pytest.importorskip("holidays")

from svenska_dagar import day_info  # noqa: E402

FIRST, LAST = date(1990, 1, 1), date(2100, 12, 31)

# The only justified divergence (a weekday, so the weekend rule cannot hide it): 6 June in a
# year from 2005 when Annandag pingst (Whit Monday) falls on it (2022, 2033, 2044, ...).
# The Svenska Dagar API names that day "Annandag pingst" and not a day off, so the national
# day is lost.  The law makes 6 June a public holiday and `holidays` is right; we keep the
# API's answer on purpose, to stay a drop-in replacement.  Everything else, including the
# de facto days off and the pre-2005 national day, agrees.


def whit_monday_on_national_day(day: date) -> bool:
    return day.month == day.day == 6 and day.year >= 2005 and day_info(day).helgdag == "Annandag pingst"


def test_arbetsfri_dag_matches_holidays_package() -> None:
    from holidays.constants import DE_FACTO, PUBLIC

    sweden = holidays.Sweden(years=range(FIRST.year, LAST.year + 1), categories=(PUBLIC, DE_FACTO))
    differences = []
    day = FIRST
    while day <= LAST:
        ours = day_info(day).arbetsfri_dag
        theirs = day.weekday() >= 5 or day in sweden
        if ours != theirs and not whit_monday_on_national_day(day):
            differences.append((day.isoformat(), day_info(day).helgdag, ours, theirs, sweden.get(day)))
        day += timedelta(days=1)
    assert not differences, differences[:20]


def test_the_known_divergence_exists() -> None:
    """Pin the divergence so it is not silently widened or forgotten."""
    from holidays.constants import DE_FACTO, PUBLIC

    sweden = holidays.Sweden(years=2022, categories=(PUBLIC, DE_FACTO))
    assert date(2022, 6, 6) in sweden
    assert not day_info(date(2022, 6, 6)).arbetsfri_dag
