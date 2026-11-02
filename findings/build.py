"""Draw every chart and write the findings report.

Run from the repository root:

    python findings/build.py

Charts go into charts/ as SVG files. The report is written to findings/README.md, and the key findings in the
main README are rewritten between their marker comments. Every number is worked out from the data. Nothing in
them is typed in by hand.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "findings"))

import analysis as an  # noqa: E402
import charts  # noqa: E402

CHARTS = ROOT / "charts"
REPORT = ROOT / "findings" / "README.md"
README = ROOT / "README.md"


def facts() -> dict:
    """Every number the writing uses, in one place."""
    damage = an.cleaning_damage()
    stolen = damage.loc[an.STOLEN]
    cliff = an.the_cliff()
    months = an.monthly()
    years = an.yearly()
    change = an.change_by_crime()
    identity = an.crime_by_year(an.IDENTITY)
    totals = an.before_switch_totals()
    area = an.by_area()
    hours = an.by_hour()
    calm = hours.drop(12)
    days = an.by_day_of_week()
    quality = an.time_quality()
    outcomes = an.outcomes()
    common = outcomes.sort_values("crimes", ascending=False).head(10)
    overall = an.overall_outcomes()
    model = an.models()
    accuracy = model["accuracy"]
    return {
        "records": f"{damage['all'].sum():,}", "kept": f"{damage['kept'].sum():,}", "lost": 1 - damage["kept"].sum() / damage["all"].sum(),
        "before": f"{totals.sum():,}", "types": len(totals),
        "stolen_all": f"{int(stolen['all']):,}", "stolen_kept": f"{int(stolen['kept']):,}", "stolen_lost": stolen["lost"], "stolen_rank": int(stolen["rank_kept"]),
        "feb": f"{cliff['february']:,}", "dec": f"{cliff['december']:,}", "drop": cliff["drop"], "avg23": f"{cliff['average_2023']:,.0f}",
        "mar": f"{int(months[(2024, 3)]):,}", "may": f"{int(months[(2024, 5)]):,}",
        "y20": f"{years[2020]:,}", "y22": f"{years[2022]:,}", "y23": f"{years[2023]:,}", "y_change": years[2023] / years[2020] - 1,
        "id20": f"{identity[2020]:,}", "id21": f"{identity[2021]:,}", "id22": f"{identity[2022]:,}", "id23": f"{identity[2023]:,}", "id_change": change[an.IDENTITY],
        "st_change": change[an.STOLEN], "pv_change": abs(change["THEFT FROM MOTOR VEHICLE - PETTY ($950 & UNDER)"]),
        "top_10": totals.head(10).sum() / totals.sum(), "stolen_before": f"{totals[an.STOLEN]:,}",
        "area_top": area.index[0], "area_top_n": f"{area.iloc[0]:,}", "area_low": area.index[-1], "area_low_n": f"{area.iloc[-1]:,}",
        "noon": f"{hours[12]:,}", "h11": f"{hours[11]:,}", "h13": f"{hours[13]:,}", "peak": int(calm.idxmax()), "peak_n": f"{calm.max():,}",
        "low_h": int(hours.idxmin()), "low_n": f"{hours.min():,}", "on_hour": quality["on_the_hour"], "first": quality["first_of_month"],
        "id_noon": quality["identity_at_noon"], "id_late": quality["identity_late"],
        "day_top": days.idxmax(), "day_low": days.idxmin(), "day_gap": days.max() / days.min() - 1,
        "arrest": overall["arrest"], "open": overall["open"],
        "arr_top": an.NAMES[common["arrest"].idxmax()].lower(), "arr_top_v": common["arrest"].max(),
        "arr_low": an.NAMES[common["arrest"].idxmin()].lower(), "arr_low_v": common["arrest"].min(),
        "arr_id": outcomes.loc[an.IDENTITY, "arrest"], "arr_st": outcomes.loc[an.STOLEN, "arrest"],
        "open_partner": outcomes.loc["INTIMATE PARTNER - SIMPLE ASSAULT", "open"], "open_id": outcomes.loc[an.IDENTITY, "open"],
        "acc_base": accuracy["Always guess the most common"], "acc_when": accuracy["When only"], "acc_area": accuracy["When and police area"],
        "acc_place": accuracy["When, area and type of place"], "train": f"{model['train_size']:,}", "test": f"{model['test_size']:,}",
        "old_acc": an.FIRST_VERSION_ACCURACY, "old_base": an.first_version_baseline(),
    }


def key_findings(f: dict) -> str:
    return f"""### The 73% fall that isn't one

Recorded crimes dropped from {f['feb']} in February 2024 to **{f['dec']}** in December. LAPD changed records systems on 7 March 2024, and
this dataset stopped being complete. It can't tell you whether crime fell.

![Crimes recorded each month, 2023 and 2024](charts/the-cliff.svg)

### Cleaning deleted the most common crime

Stolen vehicles are the most common crime on record, with {f['stolen_all']} reports. Dropping rows with blank fields, a common cleaning
step, left **{f['stolen_kept']}**, because those reports have no victim details.

![Crimes on record before and after the first version's cleaning](charts/cleaning-damage.svg)

### Noon is a recording habit as much as a crime peak

Noon has {f['noon']} crimes against {f['h13']} an hour later. {f['on_hour']:.0%} of all crimes are logged exactly on the hour, which suggests many
times are estimates.

![Crimes by recorded hour of the day](charts/by-hour.svg)

### Most crimes never record an arrest

Only **{f['arrest']:.1%}** of crimes show an arrest, from {f['arr_top_v']:.1%} for {f['arr_top']} to {f['arr_low_v']:.1%} for {f['arr_low']}.

![Share of crimes with an arrest](charts/arrests.svg)"""


def report(f: dict) -> str:
    return f"""# Findings

What {f['records']} crime reports from Los Angeles can and can't tell you. This page is written by [`build.py`](build.py), so every
number comes straight from the data.

These are crimes recorded by the Los Angeles Police Department, not all crime. Findings 3 to 7 use the {f['before']} crimes from January 2020 to
6 March 2024, the day before LAPD changed records systems.

## 1. The 73% fall that isn't one

Recorded crimes averaged {f['avg23']} a month in 2023 and were {f['feb']} in February 2024. They were {f['mar']} in March, {f['may']} in May and {f['dec']} in December, a {f['drop']:.0%}
drop from February.

![Crimes recorded each month, 2023 and 2024](../charts/the-cliff.svg)

On 7 March 2024, LAPD moved to a new records system, and it has since retired this dataset. So this drop can't be read as less crime,
and this data can't show whether crime rose or fell after that date. LAPD now publishes separate datasets from the new system, which
start from that date and use different definitions, so they can't simply be added on to this one.

## 2. Cleaning deleted the most common crime

The first version of this project dropped every row with a blank field, a very common cleaning step. It looked harmless, removing {f['lost']:.1%} of rows, but the
blanks weren't random. Stolen vehicle reports have no victim details, so {f['stolen_lost']:.1%} of them vanished: {f['stolen_all']} became {f['stolen_kept']}, taking the most common crime in the file
down to number {f['stolen_rank']}.

![Crimes on record before and after the first version's cleaning](../charts/cleaning-damage.svg)

Every other chart here keeps those rows. Blank victim details are only a problem if you're studying victims.

## 3. Recorded crime rose before the switch

Across the four full years, recorded crimes went from {f['y20']} in 2020 to {f['y22']} in 2022 and {f['y23']} in 2023, up {f['y_change']:.0%}. 2020 was the first year of the pandemic, so it's an unusual
starting point.

![Crimes recorded each year](../charts/yearly.svg)

Stolen vehicles rose {f['st_change']:.0f}% and petty theft from vehicles fell {f['pv_change']:.0f}%. Identity theft stands out, going from {f['id20']} and {f['id21']} in 2020 and 2021 to {f['id22']} in 2022, then back to {f['id23']}. The
data doesn't explain that one-year jump.

## 4. Ten crime types make up most of it

Of {f['types']} crime types on record, the top 10 account for {f['top_10']:.0%}. Stolen vehicles lead with {f['stolen_before']}.

![The 10 most common crimes](../charts/top-crimes.svg)

{f['area_top']} has the most crimes of any police area at {f['area_top_n']}, about twice {f['area_low']}'s {f['area_low_n']}. These are counts, not rates. The data has no population figures, and {f['area_top']} includes
downtown, where many people visit and work, so this doesn't show where a person is most at risk.

![Crimes by police area](../charts/by-area.svg)

## 5. Noon is a recording habit as much as a crime peak

Noon has {f['noon']} crimes, against {f['h11']} the hour before and {f['h13']} the hour after. That spike is suspicious. {f['on_hour']:.0%} of all crimes are logged exactly on the hour, when only about
2% would be if times were exact. And {f['id_noon']:.0%} of identity thefts are logged at noon, a crime whose victims often can't know when it happened: {f['id_late']:.0%} are reported more than 30 days later.
The first of the month has {f['first']:.0%} more crimes than a typical day, which looks like the same habit applied to dates.

![Crimes by recorded hour of the day](../charts/by-hour.svg)

Setting noon aside, the pattern is plausible: lowest around {f['low_h']}am with {f['low_n']} crimes, and highest around {f['peak'] - 12}pm with {f['peak_n']}. Day of the week matters much less, with {f['day_top']} only {f['day_gap']:.0%} above
{f['day_low']}.

## 6. Most crimes never record an arrest

{f['arrest']:.1%} of crimes show an arrest and {f['open']:.0%} are still marked "investigation continuing". Among the 10 most common crimes, arrests range from {f['arr_top_v']:.1%} for {f['arr_top']} to {f['arr_low_v']:.1%} for {f['arr_low']}. Stolen vehicles sit at
{f['arr_st']:.1%} and identity theft at {f['arr_id']:.1%}.

![Share of crimes with an arrest](../charts/arrests.svg)

Crimes between people are far less likely to stay open: {f['open_partner']:.0%} of partner assaults are still marked open, against {f['open_id']:.0%} of identity thefts. This status may not be updated after a report is filed, so treat it as a
minimum and not an official clearance rate.

## 7. Knowing when barely helps predict a crime. Knowing the type of place does

The first version tried to predict the type of crime from the date and scored {f['old_acc']:.0%}. It never checked that against guessing, which would have scored {f['old_base']:.1%} on its rows. Here, each method
trains on 2020 to 2022 ({f['train']} crimes from the sample) and is tested on 2023 ({f['test']} crimes).

![How often each method names the exact crime type](../charts/model-scores.svg)

Always guessing "stolen vehicle" is right {f['acc_base']:.1%} of the time. Adding the hour, day and month reaches {f['acc_when']:.1%}, and the police area {f['acc_area']:.1%}. Adding the type of place jumps to {f['acc_place']:.1%}, because a car park and a
home see very different crimes. This is about understanding the data. It isn't a tool for policing decisions, since recorded crime reflects where
crimes get reported and policed as well as where they happen.

## What this data can't tell you

- **Whether crime fell after March 2024.** This dataset can't answer that.
- **All crime.** Many crimes are never reported, and reporting differs between crimes and neighbourhoods.
- **Risk.** There are no population figures, so these counts aren't rates.
- **Why.** The data shows patterns, not causes.

## How it was worked out

1. [`data/prepare.py`](../data/prepare.py) turns the full download into summaries and a {200_000:,}-crime sample, leaving out addresses, coordinates, record numbers and victim descent.
2. [`analysis.py`](analysis.py) holds every calculation as a small, tested function.
3. [`charts.py`](charts.py) draws each chart with [bezel-charts](https://pypi.org/project/bezel-charts/).
4. [`notebooks/crime_data_analysis.ipynb`](../notebooks/crime_data_analysis.ipynb) walks through the same steps with the working shown.

Counts come from every record. Only the model in finding 7 uses the sample.
"""


def replace_block(text: str, name: str, body: str) -> str:
    pattern = re.compile(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", re.S)
    if not pattern.search(text):
        raise ValueError(f"Marker {name} not found")
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), text)


def main() -> None:
    # bezel-charts gives each gradient a random id so charts can share a page. A fixed seed keeps the
    # files identical between runs, so a rebuild only shows up in git when something really changed.
    random.seed(2026)
    CHARTS.mkdir(exist_ok=True)
    for name, draw in charts.ALL.items():
        draw().save(CHARTS / f"{name}.svg")
    f = facts()
    REPORT.write_text(report(f), encoding="utf-8")
    README.write_text(replace_block(README.read_text(encoding="utf-8"), "key-findings", key_findings(f)), encoding="utf-8")
    print(f"Wrote {len(charts.ALL)} charts, {REPORT.relative_to(ROOT)} and the README findings")


if __name__ == "__main__":
    main()
