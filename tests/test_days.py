"""Specific days, written out by hand and independent of the golden fixtures.

Every weekday below was checked against ``datetime``/``calendar`` and every holiday date
against Swedish law (lag 1989:253 om allmänna helgdagar) and the Easter computus
(Easter Sunday 2026 is 5 April), not against this package's output.

Columns: date, veckodag, arbetsfri_dag, rod_dag, helgdag, helgdagsafton, klamdag,
dag_fore_arbetsfri_helgdag.
"""
from __future__ import annotations

from datetime import date

import pytest

from svenska_dagar import day_info, holiday_name, is_workday

D = date
# fmt: off
DAYS = [
    # --- new year, epiphany ---
    pytest.param(D(2026, 1, 1), "Torsdag", True, True, "Nyårsdagen", None, False, False, id="2026-01-01 Nyårsdagen"),
    # Monday between Sunday and Trettondedag jul (Tuesday): a klämdag.
    pytest.param(D(2026, 1, 5), "Måndag", False, False, None, "Trettondagsafton", True, True, id="2026-01-05 Trettondagsafton (klämdag)"),
    pytest.param(D(2026, 1, 6), "Tisdag", True, True, "Trettondedag jul", None, False, False, id="2026-01-06 Trettondedag jul"),
    # --- Easter 2026 (Easter Sunday = 5 April) ---
    pytest.param(D(2026, 4, 2), "Torsdag", False, False, None, "Skärtorsdagen", False, True, id="2026-04-02 Skärtorsdagen"),
    pytest.param(D(2026, 4, 3), "Fredag", True, True, "Långfredagen", None, False, False, id="2026-04-03 Långfredagen"),
    pytest.param(D(2026, 4, 4), "Lördag", True, False, "Påskafton", None, False, False, id="2026-04-04 Påskafton"),
    pytest.param(D(2026, 4, 5), "Söndag", True, True, "Påskdagen", None, False, False, id="2026-04-05 Påskdagen"),
    pytest.param(D(2026, 4, 6), "Måndag", True, True, "Annandag påsk", None, False, False, id="2026-04-06 Annandag påsk"),
    # --- Valborg, 1 May, Ascension ---
    pytest.param(D(2026, 4, 30), "Torsdag", False, False, None, "Valborgsmässoafton", False, True, id="2026-04-30 Valborgsmässoafton"),
    pytest.param(D(2026, 5, 1), "Fredag", True, True, "Första Maj", None, False, False, id="2026-05-01 Första Maj"),
    pytest.param(D(2026, 5, 13), "Onsdag", False, False, None, None, False, True, id="2026-05-13 day before Kristi himmelsfärd"),
    pytest.param(D(2026, 5, 14), "Torsdag", True, True, "Kristi himmelsfärdsdag", None, False, False, id="2026-05-14 Kristi himmelsfärdsdag"),
    pytest.param(D(2026, 5, 15), "Fredag", False, False, None, None, True, False, id="2026-05-15 klämdag"),
    # Ascension Day 2008 fell on 1 May (Easter 23 March 2008 + 39 days): combined name.
    pytest.param(D(2008, 5, 1), "Torsdag", True, True, "Kristi himmelsfärdsdag, Första Maj", None, False, False, id="2008-05-01 Kristi himmelsfärdsdag + Första Maj"),
    # --- Pentecost ---
    pytest.param(D(2026, 5, 23), "Lördag", True, False, None, "Pingstafton", False, False, id="2026-05-23 Pingstafton"),
    pytest.param(D(2026, 5, 24), "Söndag", True, True, "Pingstdagen", None, False, False, id="2026-05-24 Pingstdagen"),
    # Annandag pingst was a day off until 2004; from 2005 it is an ordinary working day.
    # (The name is still reported, as the original API did.)
    pytest.param(D(2004, 5, 31), "Måndag", True, True, "Annandag pingst", None, False, False, id="2004-05-31 Annandag pingst (day off)"),
    pytest.param(D(2005, 5, 16), "Måndag", False, False, "Annandag pingst", None, False, False, id="2005-05-16 Annandag pingst (no day off)"),
    # --- national day: from 2005 always a day off, also on Annandag pingst (2022-06-06) ---
    pytest.param(D(2026, 6, 6), "Lördag", True, True, "Sveriges nationaldag", None, False, False, id="2026-06-06 Sveriges nationaldag"),
    pytest.param(D(2022, 6, 6), "Måndag", True, True, "Sveriges nationaldag", None, False, False, id="2022-06-06 Sveriges nationaldag (Annandag pingst)"),
    # --- midsummer: Friday 19 and Saturday 20 June 2026 ---
    pytest.param(D(2026, 6, 19), "Fredag", True, False, "Midsommarafton", None, False, False, id="2026-06-19 Midsommarafton"),
    pytest.param(D(2026, 6, 20), "Lördag", True, True, "Midsommardagen", None, False, False, id="2026-06-20 Midsommardagen"),
    # --- All Saints: 31 October 2026 is a Saturday, so Alla helgons dag is that day ---
    pytest.param(D(2026, 10, 30), "Fredag", False, False, None, "Allhelgonaafton", False, True, id="2026-10-30 Allhelgonaafton"),
    pytest.param(D(2026, 10, 31), "Lördag", True, True, "Alla helgons dag", None, False, False, id="2026-10-31 Alla helgons dag"),
    # --- Christmas ---
    pytest.param(D(2026, 12, 23), "Onsdag", False, False, None, None, False, True, id="2026-12-23 day before Julafton"),
    pytest.param(D(2026, 12, 24), "Torsdag", True, False, "Julafton", None, False, False, id="2026-12-24 Julafton"),
    pytest.param(D(2026, 12, 25), "Fredag", True, True, "Juldagen", None, False, False, id="2026-12-25 Juldagen"),
    pytest.param(D(2026, 12, 26), "Lördag", True, True, "Annandag jul", None, False, False, id="2026-12-26 Annandag jul"),
    pytest.param(D(2026, 12, 31), "Torsdag", True, False, "Nyårsafton", None, False, False, id="2026-12-31 Nyårsafton"),
    # --- ordinary days ---
    pytest.param(D(2026, 3, 9), "Måndag", False, False, None, None, False, False, id="2026-03-09 ordinary Monday"),
    pytest.param(D(2026, 3, 14), "Lördag", True, False, None, None, False, False, id="2026-03-14 ordinary Saturday"),
    pytest.param(D(2026, 3, 15), "Söndag", True, True, None, None, False, False, id="2026-03-15 ordinary Sunday"),
]
# fmt: on


@pytest.mark.parametrize(
    "day, veckodag, arbetsfri, rod, helgdag, helgdagsafton, klamdag, dag_fore", DAYS
)
def test_day(day, veckodag, arbetsfri, rod, helgdag, helgdagsafton, klamdag, dag_fore):
    info = day_info(day)
    assert info.datum == day
    assert info.veckodag == veckodag
    assert info.arbetsfri_dag is arbetsfri
    assert info.rod_dag is rod
    assert info.helgdag == helgdag
    assert info.helgdagsafton == helgdagsafton
    assert info.klamdag is klamdag
    assert info.dag_fore_arbetsfri_helgdag is dag_fore


@pytest.mark.parametrize(
    "day, veckodag, arbetsfri, rod, helgdag, helgdagsafton, klamdag, dag_fore", DAYS
)
def test_shortcuts_agree(day, veckodag, arbetsfri, rod, helgdag, helgdagsafton, klamdag, dag_fore):
    assert is_workday(day) is (not arbetsfri)
    assert holiday_name(day) == helgdag
