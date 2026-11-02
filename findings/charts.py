"""Every chart in the project, drawn with bezel-charts (https://pypi.org/project/bezel-charts/).

Each function returns a chart, which shows up in a notebook and saves as an SVG.
"""

from __future__ import annotations

import pandas as pd

import bezel_charts as bc

try:
    from . import analysis as an
except ImportError:
    import analysis as an

WIDE = {"theme": "light", "width": 760}
TILE = {"theme": "light", "width": 270}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# The library's default order puts pink next to green, which look alike with red-green colour blindness.
PAIR = ["#6E70F0", "#D99A0E"]
MUTED, STRONG = "#B7B8F7", "#6E70F0"


def named(values: pd.Series) -> pd.Series:
    values = values.copy()
    values.index = [an.NAMES.get(name, name) for name in values.index]
    return values


def cleaning_damage():
    table = an.cleaning_damage()
    picks = ["VEHICLE - STOLEN", "BATTERY - SIMPLE ASSAULT", "BURGLARY FROM VEHICLE", "THEFT OF IDENTITY",
             "THEFT FROM MOTOR VEHICLE - PETTY ($950 & UNDER)"]
    frame = pd.DataFrame(
        {"Every record": table.loc[picks, "all"] / 1000, "After the first version's cleaning": table.loc[picks, "kept"] / 1000}
    ).round(1)
    frame.index = ["Stolen vehicle", "Simple assault", "Burglary from car", "Identity theft", "Petty theft from car"]
    return bc.bars(
        frame, heading="Crimes on record, thousands, 2020 to 2024", stat="none", show_values=True, suffix="k", decimals=1,
        height=230, color=PAIR, **WIDE,
    )


def the_cliff():
    months = an.monthly().loc[2023:2024]
    series = pd.Series(months.to_numpy() / 1000, index=[f"{MONTHS[m - 1]} {str(y)[2:]}" for y, m in months.index]).round(1)
    return bc.line(
        series, heading="Crimes recorded each month. LAPD changed records systems in March 2024", stat="none", zero=True,
        height=240, straight=True, suffix="k", decimals=0, notes={"Mar 24": "New system"}, **WIDE,
    )


def yearly():
    totals = an.yearly() / 1000
    totals.index = totals.index.astype(str)
    return bc.bars(
        totals.round(1), heading="Crimes recorded each year, the four full years before the switch", stat="none",
        show_values=True, suffix="k", decimals=0, height=190, **WIDE,
    )


def top_crimes():
    return bc.bars(
        named(an.before_switch_totals().head(10)) / 1000, heading="The 10 most common crimes, January 2020 to March 2024, thousands",
        horizontal=True, stat="none", show_values=True, suffix="k", decimals=0, **WIDE,
    )


def by_area():
    return bc.bars(
        an.by_area() / 1000, heading="Crimes by police area, January 2020 to March 2024, thousands. Not adjusted for population",
        horizontal=True, stat="none", show_values=True, suffix="k", decimals=0, **WIDE,
    )


def by_hour():
    hours = an.by_hour() / 1000
    hours.index = hours.index.astype(str)
    return bc.bars(
        hours.round(1), heading="Crimes by recorded hour of the day, thousands. Noon is inflated, see below", stat="none",
        show_values=True, suffix="k", decimals=0, height=220, **WIDE,
    )


def arrests():
    table = an.outcomes()
    picks = table.sort_values("crimes", ascending=False).head(10).sort_values("arrest", ascending=False)
    return bc.bars(
        named(picks["arrest"] * 100).round(1), heading="Share of crimes with an arrest, the 10 most common crimes", horizontal=True,
        stat="none", show_values=True, suffix="%", decimals=1, **WIDE,
    )


def model_scores():
    return bc.bars(
        (an.models()["accuracy"] * 100).round(1), heading="How often each method names the exact crime type, 2023 crimes",
        horizontal=True, stat="none", show_values=True, suffix="%", decimals=1, **WIDE,
    )


# Headline tiles ------------------------------------------------------------------------------------

def tile_december():
    months = an.monthly()
    series = pd.Series(months.to_numpy(), index=[f"{y}-{m:02d}" for y, m in months.index])
    return bc.spark(series, heading="Recorded, Dec 2024", delta="none", straight=True, height=86, decimals=0, **TILE)


def tile_arrests():
    return bc.gauge(round(an.overall_outcomes()["arrest"] * 100, 1), label="led to an arrest", heading="Arrests", suffix="%", **TILE)


def tile_stolen():
    table = an.read("by_month")
    rows = table[(table["crime"] == an.STOLEN) & (table["year"] <= 2023)].groupby("year")["crimes"].sum()
    rows.index = rows.index.astype(str)
    return bc.spark(rows, heading="Stolen vehicles, 2023", delta="none", straight=True, height=86, decimals=0, **TILE)


ALL = {
    "cleaning-damage": cleaning_damage,
    "the-cliff": the_cliff,
    "yearly": yearly,
    "top-crimes": top_crimes,
    "by-area": by_area,
    "by-hour": by_hour,
    "arrests": arrests,
    "model-scores": model_scores,
    "tile-december": tile_december,
    "tile-arrests": tile_arrests,
    "tile-stolen": tile_stolen,
}
