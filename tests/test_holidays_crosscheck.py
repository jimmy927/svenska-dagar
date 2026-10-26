"""Cross-check ``arbetsfri_dag`` against the ``holidays`` package (dev dependency only)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

holidays = pytest.importorskip("holidays")

from svenska_dagar import day_info  # noqa: E402

FIRST, LAST = date(1990, 1, 1), date(2100, 12, 31)

# No exceptions: including the de facto days off, the pre-2005 national day and 6 June
# falling on Annandag pingst (the API gets that one wrong; we do not).


def test_arbetsfri_dag_matches_holidays_package() -> None:
    from holidays.constants import DE_FACTO, PUBLIC

    sweden = holidays.Sweden(years=range(FIRST.year, LAST.year + 1), categories=(PUBLIC, DE_FACTO))
    differences = []
    day = FIRST
    while day <= LAST:
        ours = day_info(day).arbetsfri_dag
        theirs = day.weekday() >= 5 or day in sweden
        if ours != theirs:
            differences.append((day.isoformat(), day_info(day).helgdag, ours, theirs, sweden.get(day)))
        day += timedelta(days=1)
    assert not differences, differences[:20]
