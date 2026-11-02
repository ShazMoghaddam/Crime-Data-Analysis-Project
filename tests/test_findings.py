"""Checks that the data is sound and the findings hold up. Run from the repository root with `pytest`."""

import re
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "findings"), str(ROOT / "data")]

import analysis as an  # noqa: E402
import prepare  # noqa: E402

BEFORE_SWITCH = ["by_area", "by_time", "by_status", "by_reported", "by_clock", "by_day"]


def raw(date: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "DATE OCC": [date], "Date Rptd": [date], "TIME OCC": [1845], "AREA NAME": ["Central"], "Crm Cd Desc": ["ROBBERY"],
            "Premis Desc": [None], "Status Desc": ["Invest Cont"], "Mocodes": ["1"], "Vict Sex": [None], "Vict Descent": ["W"],
            "Premis Cd": [101.0], "Status": ["IC"], "Crm Cd 1": [210.0],
        }
    )


@pytest.mark.parametrize("layout", ["2020 Nov 07 12:00:00 AM", "11/07/2020 12:00:00 AM"])
def test_both_date_layouts_are_read(layout):
    row = prepare.tidy(raw(layout)).iloc[0]
    assert (row["date"], row["hour"], row["dow"]) == ("2020-11-07", 18, "Saturday")


def test_a_blank_victim_field_fails_the_old_filter():
    assert not prepare.tidy(raw("2020 Nov 07 12:00:00 AM")).iloc[0]["old_kept"]


def test_summaries_agree_with_each_other():
    assert an.monthly().sum() == 1_004_894
    totals = {name: an.read(name)["crimes"].sum() for name in BEFORE_SWITCH}
    assert len(set(totals.values())) == 1
    assert totals["by_area"] < an.monthly().sum()


def test_nothing_after_the_switch_reaches_the_sample():
    crimes = an.sample()
    assert len(crimes) == 200_000
    assert crimes["date"].max() < prepare.SWITCH


def test_private_details_stay_out_of_the_repo():
    for path in an.DATA.glob("*.csv*"):
        header = pd.read_csv(path, nrows=0).columns.str.lower()
        for column in ("location", "lat", "lon", "cross street", "dr_no", "vict descent"):
            assert column not in header, f"{column} in {path.name}"


def test_stolen_vehicles_survive_the_new_cleaning():
    assert an.before_switch_totals().index[0] == an.STOLEN
    damage = an.cleaning_damage().loc[an.STOLEN]
    assert damage["rank_all"] == 1 and damage["lost"] > 0.99


def test_the_cliff_is_after_the_switch():
    months = an.monthly()
    assert months[(2024, 2)] > 0.85 * months[2023].mean()
    assert an.the_cliff()["drop"] > 0.7


def test_model_trains_only_on_the_past():
    train, test = an.split(an.sample())
    assert train["year"].max() == 2022 and set(test["year"]) == {2023}


def test_writing_has_no_broken_values():
    for path in (ROOT / "README.md", ROOT / "findings" / "README.md"):
        text = path.read_text(encoding="utf-8")
        assert not re.findall(r"\bnan\b", text)
        assert "Filled in by" not in text


def test_every_chart_in_the_writing_exists():
    for path in (ROOT / "README.md", ROOT / "findings" / "README.md"):
        for link in re.findall(r"!\[[^\]]*\]\(([^)]+\.svg)\)", path.read_text(encoding="utf-8")):
            if not link.startswith("http"):
                assert (path.parent / link).resolve().exists(), link


def test_readme_text_written_by_hand_matches_the_data():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"{an.monthly().sum():,} crime reports" in text
    assert f"{an.the_cliff()['december']:,} in December" in text
    assert f"{an.overall_outcomes()['arrest'] * 100:.1f} percent of crimes" in text
    assert f"{an.crime_by_year(an.STOLEN)[2023]:,} in 2023" in text
    assert f"The {an.the_cliff()['drop']:.0%} fall" in text
