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

The rules follow the API, history included: *Annandag pingst* is a day off before 2005 only,
*Sveriges nationaldag* is a day off from 2005 (and *Svenska flaggans dag* before 1983), and when
Kristi himmelsfärdsdag falls on 30 April or 1 May the name is combined, e.g.
`"Kristi himmelsfärdsdag, Första Maj"`.

Known quirk, kept on purpose for compatibility: when *Annandag pingst* falls on 6 June (2022,
2033, 2044, ...) the API reports that day as an ordinary working day, although the law makes
the national day a public holiday. We return the API's answer.

## Credit

Inspired by, and compatible with the answers of, the original Svenska Dagar service by
[dryg.net](https://api.dryg.net/) (Johan Blomgren, GitHub user drygnet; PHP source at
[drygnet/svenska-dagar-PHP](https://github.com/drygnet/svenska-dagar-PHP)). This package is an
independent reimplementation written from the rules (lag (1989:253) om allmänna helgdagar plus the
de facto days off), not a port of that code. Golden test fixtures were recorded from the live
service while it was up (`scripts/fetch_fixtures.py`).

## Development

```
uv run pytest
```

The tests compare every field against recorded API answers in `tests/fixtures/` and
cross-check `arbetsfri_dag` with the [`holidays`](https://pypi.org/project/holidays/) package
for 1990-2100.

## License

MIT, see `LICENSE`.
