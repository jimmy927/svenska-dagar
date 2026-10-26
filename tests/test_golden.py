"""Compare every field against golden fixtures fetched from the live API
(scripts/fetch_fixtures.py).  Tests never touch the network."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from svenska_dagar import day_info, holiday_name, is_workday

FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("*.json"))


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


ALL_DAYS = [d for path in FIXTURES for d in load(path)]


def expected(api: dict) -> dict:
    """The API's JSON for one day, translated to our field names."""
    return {
        "datum": date.fromisoformat(api["datum"]),
        "veckodag": api["veckodag"],
        "vecka": int(api["vecka"]),
        "arbetsfri_dag": api["arbetsfri dag"] == "Ja",
        "rod_dag": api["röd dag"] == "Ja",
        "helgdag": api.get("helgdag"),
        "helgdagsafton": api.get("helgdagsafton"),
        "klamdag": api.get("klämdag") == "Ja",
        "dag_fore_arbetsfri_helgdag": api.get("dag före arbetsfri helgdag") == "Ja",
    }


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.stem)
def test_every_field_matches_the_api(path: Path) -> None:
    mismatches = []
    for api in load(path):
        want = expected(api)
        got = day_info(want["datum"])
        got_fields = {name: getattr(got, name) for name in want}
        if got_fields != want:
            diff = {k: (got_fields[k], want[k]) for k in want if got_fields[k] != want[k]}
            mismatches.append((api["datum"], diff))
    assert not mismatches, mismatches[:10]


def test_helpers_agree_with_day_info() -> None:
    for api in ALL_DAYS:
        want = expected(api)
        assert is_workday(want["datum"]) is (not want["arbetsfri_dag"]), api["datum"]
        assert holiday_name(want["datum"]) == want["helgdag"], api["datum"]


def test_fixtures_cover_the_edge_cases() -> None:
    """Guard against a thin fixture set silently passing."""
    days = {d["datum"]: d for d in ALL_DAYS}
    names = {n for d in ALL_DAYS for n in (d.get("helgdag"), d.get("helgdagsafton")) if n}
    # Every holiday and eve the API can name (the combined Kristi himmelsfärd names included).
    for name in [
        "Nyårsdagen", "Trettondagsafton", "Trettondedag jul", "Skärtorsdagen", "Långfredagen",
        "Påskafton", "Påskdagen", "Annandag påsk", "Valborgsmässoafton", "Första Maj",
        "Kristi himmelsfärdsdag", "Kristi himmelsfärdsdag, Första Maj",
        "Kristi himmelsfärdsdag, Valborgsmässoafton", "Pingstafton", "Pingstdagen",
        "Annandag pingst", "Sveriges nationaldag", "Svenska flaggans dag", "Midsommarafton",
        "Midsommardagen", "Allhelgonaafton", "Alla helgons dag", "Julafton", "Juldagen",
        "Annandag jul", "Nyårsafton",
    ]:
        assert name in names, name
    assert days["2008-05-01"]["helgdag"] == "Kristi himmelsfärdsdag, Första Maj"
    assert days["2285-04-30"]["helgdag"] == "Kristi himmelsfärdsdag, Valborgsmässoafton"
    for edge in ["2009-06-20", "2004-06-26", "2009-10-31", "2004-11-06"]:
        assert days[edge]["veckodag"] == "Lördag"
    assert days["2009-06-20"]["helgdag"] == "Midsommardagen"
    assert days["2004-06-26"]["helgdag"] == "Midsommardagen"
    assert days["2009-10-31"]["helgdag"] == "Alla helgons dag"
    assert days["2004-11-06"]["helgdag"] == "Alla helgons dag"
    assert any(d.get("klämdag") == "Ja" for d in ALL_DAYS)
    assert any(d.get("dag före arbetsfri helgdag") == "Ja" for d in ALL_DAYS)
    assert {d["datum"][:4] for d in ALL_DAYS} >= {"1980", "1995", "2004", "2005", "2008", "2026"}


def test_history_of_the_sixth_of_june() -> None:
    assert day_info(date(1982, 6, 6)).helgdag == "Svenska flaggans dag"
    assert day_info(date(1995, 6, 6)).helgdag == "Sveriges nationaldag"
    assert not day_info(date(1995, 6, 6)).arbetsfri_dag
    assert day_info(date(2005, 6, 6)).arbetsfri_dag  # a Monday


def test_annandag_pingst_is_a_day_off_before_2005_only() -> None:
    assert day_info(date(2004, 5, 31)).arbetsfri_dag
    assert day_info(date(2024, 5, 20)).helgdag == "Annandag pingst"
    assert not day_info(date(2024, 5, 20)).arbetsfri_dag


def test_ordinary_day_has_no_holiday() -> None:
    info = day_info(date(2026, 3, 10))
    assert (info.helgdag, info.helgdagsafton) == (None, None)
    assert info.veckodag == "Tisdag"
    assert is_workday(date(2026, 3, 10))
    assert holiday_name(date(2026, 3, 10)) is None
