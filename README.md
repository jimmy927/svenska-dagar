[![CI](https://github.com/jimmy927/svenska-dagar/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/jimmy927/svenska-dagar/actions/workflows/ci.yml)
![python 3.10 | 3.11 | 3.12 | 3.13 | 3.14](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Typed](https://img.shields.io/badge/typed-mypy%20--strict-blue)

# svenska-dagar

Svenska helgdagar, röda dagar, aftnar och klämdagar per datum: offline, utan beroenden.

Swedish public holidays, days off, eves and squeeze days (*klämdagar*) for any `datetime.date`.
Offline, pure Python, no runtime dependencies, fully typed. MIT licensed.

It answers the same holiday questions as the "Svenska Dagar" web API at
`sholiday.faboul.se` / `api.dryg.net` (v2.1), which is gone, so code that used that API can
call a function instead of making an HTTP request. Holidays only: no name days, no flag days.

## Install

```
pip install git+https://github.com/jimmy927/svenska-dagar
```

Python 3.10 or newer.

## Usage

```python
from datetime import date
from svenska_dagar import day_info, holiday_name, is_workday

is_workday(date(2026, 6, 19))      # False: Midsommarafton
holiday_name(date(2026, 6, 19))    # "Midsommarafton"

info = day_info(date(2026, 5, 15))
info.veckodag                      # "Fredag"
info.klamdag                       # True: Kristi himmelsfärdsdag is the day before, the weekend after
```

`day_info()` returns a frozen `DayInfo` dataclass:

| Field | Type | Meaning |
|---|---|---|
| `datum` | `date` | The date asked for |
| `veckodag` | `str` | `Måndag`, `Tisdag`, `Onsdag`, `Torsdag`, `Fredag`, `Lördag`, `Söndag` |
| `vecka` | `int` | ISO week number |
| `arbetsfri_dag` | `bool` | Weekend or day off (includes midsommarafton, julafton, nyårsafton) |
| `rod_dag` | `bool` | Sunday or public holiday (*röd dag*) |
| `helgdag` | `str \| None` | Name of the holiday, including *Midsommarafton*, *Påskafton*, *Julafton*, *Nyårsafton* |
| `helgdagsafton` | `str \| None` | Name of an eve that is not a `helgdag`: *Trettondagsafton*, *Skärtorsdagen*, *Valborgsmässoafton*, *Pingstafton*, *Allhelgonaafton* |
| `klamdag` | `bool` | A working day between two days off |
| `dag_fore_arbetsfri_helgdag` | `bool` | A working day followed by a `helgdag` |

`is_workday(d)` is `not day_info(d).arbetsfri_dag`; `holiday_name(d)` is `day_info(d).helgdag`.

All three take a `datetime.date`. Anything else raises `TypeError`, a `datetime.datetime`
included (it would silently drop the time and time zone): pass `dt.date()`.

The rules follow the API, history included: *Annandag pingst* is a day off before 2005 only,
*Sveriges nationaldag* is a day off from 2005 (and *Svenska flaggans dag* before 1983), and when
Kristi himmelsfärdsdag falls on 30 April or 1 May the name is combined, e.g.
`"Kristi himmelsfärdsdag, Första Maj"`.

One deliberate difference: when *Annandag pingst* falls on 6 June from 2005 (2022, 2033, 2044,
...) the original API reported an ordinary working day and lost the national day. Here it is
*Sveriges nationaldag*, a day off, as the law says. Before 2005 the API's answers are kept.

## Credit

Inspired by, and compatible with the answers of, the original Svenska Dagar service by
[dryg.net](https://api.dryg.net/) (Johan Blomgren, GitHub user drygnet; PHP source at
[drygnet/svenska-dagar-PHP](https://github.com/drygnet/svenska-dagar-PHP)). This package is an
independent reimplementation written from the rules (lag (1989:253) om allmänna helgdagar plus the
de facto days off), not a port of that code. Golden test fixtures were recorded from the live
service while it was up (`scripts/fetch_fixtures.py`).

## Tests

- Golden fixtures: every field for every day of 18 years, recorded from the original API.
- Specific-day tests (`tests/test_days.py`): hand-written rows for named holidays, eves,
  klämdagar and the history rules, checked against a calendar and the law.
- Format tests (`tests/test_format.py`): field types, frozen dataclass, ISO weeks, `__all__`,
  input validation.
- Cross-check of `arbetsfri_dag` against the [`holidays`](https://pypi.org/project/holidays/)
  package for 1990-2100.
- `mypy --strict src` is clean.

```
uv run --with pytest --with holidays pytest
uv run --with mypy mypy --strict src
```

## License

MIT, see `LICENSE`.
