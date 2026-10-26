"""Shape of the public API: field types, immutability, exports and input validation."""
from __future__ import annotations

import dataclasses
from datetime import date, datetime, timedelta, timezone

import pytest

import svenska_dagar
from svenska_dagar import day_info, easter_sunday, holiday_name, is_workday

WEEKDAY_NAMES = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]


def test_frozen():
    info = day_info(date(2026, 1, 1))
    with pytest.raises(dataclasses.FrozenInstanceError):
        info.klamdag = True  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        info.helgdag = "x"  # type: ignore[misc]


@pytest.mark.parametrize("day", [date(2026, 1, 1), date(2026, 3, 9), date(2026, 6, 19), date(2026, 5, 15)])
def test_field_types(day):
    info = day_info(day)
    assert type(info.datum) is date
    assert type(info.veckodag) is str
    assert type(info.vecka) is int
    assert 1 <= info.vecka <= 53
    for flag in (info.arbetsfri_dag, info.rod_dag, info.klamdag, info.dag_fore_arbetsfri_helgdag):
        assert type(flag) is bool
    for name in (info.helgdag, info.helgdagsafton):
        assert name is None or type(name) is str


def test_field_names_and_order():
    assert [f.name for f in dataclasses.fields(svenska_dagar.DayInfo)] == [
        "datum", "veckodag", "vecka", "arbetsfri_dag", "rod_dag",
        "helgdag", "helgdagsafton", "klamdag", "dag_fore_arbetsfri_helgdag",
    ]


def test_shortcut_types():
    assert type(is_workday(date(2026, 3, 9))) is bool
    assert type(holiday_name(date(2026, 3, 9))) is type(None)
    assert type(holiday_name(date(2026, 1, 1))) is str
    assert type(easter_sunday(2026)) is date


@pytest.mark.parametrize(
    "day, week",
    [
        (date(2026, 12, 31), 53),
        (date(2027, 1, 1), 53),  # still ISO week 53 of 2026
        (date(2020, 12, 31), 53),
        (date(2021, 1, 4), 1),
        (date(2026, 1, 1), 1),
    ],
)
def test_iso_week(day, week):
    assert day.isocalendar()[1] == week  # the expectation itself, from the stdlib
    assert day_info(day).vecka == week


def test_veckodag_in_order_across_a_week():
    monday = date(2026, 3, 9)
    assert monday.weekday() == 0
    names = [day_info(monday + timedelta(days=i)).veckodag for i in range(7)]
    assert names == WEEKDAY_NAMES
    assert [day_info(monday + timedelta(days=i)).vecka for i in range(7)] == [11] * 7


def test_helgdag_none_on_ordinary_days():
    for day in (date(2026, 3, 9), date(2026, 3, 14), date(2026, 3, 15)):
        info = day_info(day)
        assert info.helgdag is None
        assert info.helgdagsafton is None
        assert holiday_name(day) is None


def test_public_api_is_exactly_all():
    assert sorted(svenska_dagar.__all__) == ["DayInfo", "day_info", "easter_sunday", "holiday_name", "is_workday"]
    for name in svenska_dagar.__all__:
        assert hasattr(svenska_dagar, name)
    namespace: dict[str, object] = {}
    exec("from svenska_dagar import *", namespace)
    assert set(svenska_dagar.__all__) <= set(namespace)


BAD_INPUTS = [
    pytest.param("2026-01-01", id="str"),
    pytest.param(None, id="None"),
    pytest.param(20260101, id="int"),
    pytest.param(datetime(2026, 1, 1), id="naive datetime"),
    pytest.param(datetime(2026, 1, 1, 23, 30, tzinfo=timezone.utc), id="aware datetime"),
]


@pytest.mark.parametrize("func", [day_info, is_workday, holiday_name])
@pytest.mark.parametrize("bad", BAD_INPUTS)
def test_invalid_input_raises_type_error(func, bad):
    with pytest.raises(TypeError):
        func(bad)


def test_datetime_error_points_at_date():
    with pytest.raises(TypeError, match="datetime"):
        day_info(datetime(2026, 1, 1))
