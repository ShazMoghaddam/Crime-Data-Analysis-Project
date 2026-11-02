"""The analysis behind every finding. Plain functions, no charts and no files written.

Monthly totals cover the whole file. Everything else stops before 7 March 2024, when LAPD changed records systems
and this dataset became incomplete.
"""

from __future__ import annotations

import warnings
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

DATA = Path(__file__).resolve().parent.parent / "data"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
FULL_YEARS = [2020, 2021, 2022, 2023]
STOLEN = "VEHICLE - STOLEN"
IDENTITY = "THEFT OF IDENTITY"
FIRST_VERSION_ACCURACY = 0.10  # Saved in the original notebook's output
ARRESTS = ["Adult Arrest", "Juv Arrest"]
OPEN = "Invest Cont"

NAMES = {
    "VEHICLE - STOLEN": "Stolen vehicle",
    "BATTERY - SIMPLE ASSAULT": "Simple assault",
    "BURGLARY FROM VEHICLE": "Burglary from vehicle",
    "THEFT OF IDENTITY": "Identity theft",
    "VANDALISM - FELONY ($400 & OVER, ALL CHURCH VANDALISMS)": "Felony vandalism",
    "BURGLARY": "Burglary",
    "THEFT PLAIN - PETTY ($950 & UNDER)": "Petty theft",
    "ASSAULT WITH DEADLY WEAPON, AGGRAVATED ASSAULT": "Aggravated assault",
    "INTIMATE PARTNER - SIMPLE ASSAULT": "Partner assault",
    "THEFT FROM MOTOR VEHICLE - PETTY ($950 & UNDER)": "Petty theft from vehicle",
    "THEFT FROM MOTOR VEHICLE - GRAND ($950.01 AND OVER)": "Grand theft from vehicle",
    "THEFT-GRAND ($950.01 & OVER)EXCPT,GUNS,FOWL,LIVESTK,PROD": "Grand theft",
    "ROBBERY": "Robbery",
    "SHOPLIFTING - PETTY THEFT ($950 & UNDER)": "Shoplifting",
    "VANDALISM - MISDEAMEANOR ($399 OR UNDER)": "Minor vandalism",
}


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv")


def sample() -> pd.DataFrame:
    return pd.read_csv(DATA / "crime_sample.csv.gz")


def monthly() -> pd.Series:
    """Crimes per month across the whole file, keyed by (year, month)."""
    return read("by_month").groupby(["year", "month"])["crimes"].sum()


# Finding 1: what the first version's cleaning deleted -----------------------------------------------

def cleaning_damage() -> pd.DataFrame:
    table = read("by_month")
    every = table.groupby("crime")["crimes"].sum()
    kept = table[table["old_kept"]].groupby("crime")["crimes"].sum().reindex(every.index, fill_value=0)
    result = pd.DataFrame({"all": every, "kept": kept})
    result["lost"] = 1 - result["kept"] / result["all"]
    result["rank_all"] = result["all"].rank(ascending=False).astype(int)
    result["rank_kept"] = result["kept"].rank(ascending=False, method="min").astype(int)
    return result.sort_values("all", ascending=False)


# Finding 2: the fall that isn't one ------------------------------------------------------------------

def the_cliff() -> dict:
    months = monthly()
    return {
        "february": int(months[(2024, 2)]),
        "december": int(months[(2024, 12)]),
        "drop": 1 - months[(2024, 12)] / months[(2024, 2)],
        "average_2023": float(months[2023].mean()),
    }


# Finding 3 and 4: the reliable years, and which crimes -------------------------------------------------

def yearly() -> pd.Series:
    return read("by_month").groupby("year")["crimes"].sum().loc[FULL_YEARS]


def before_switch_totals() -> pd.Series:
    """Crimes of each type from January 2020 to just before the switch."""
    return read("by_status").groupby("crime")["crimes"].sum().sort_values(ascending=False)


def change_by_crime(top: int = 10) -> pd.Series:
    """Percentage change from 2020 to 2023 for the most common crimes."""
    table = read("by_month")
    by_year = table[table["year"].isin(FULL_YEARS)].groupby(["crime", "year"])["crimes"].sum().unstack(fill_value=0)
    common = by_year.sum(axis=1).sort_values(ascending=False).head(top).index
    return ((by_year.loc[common, 2023] / by_year.loc[common, 2020] - 1) * 100).sort_values(ascending=False)


def crime_by_year(crime: str) -> pd.Series:
    table = read("by_month")
    return table[(table["crime"] == crime) & table["year"].isin(FULL_YEARS)].groupby("year")["crimes"].sum()


def by_area() -> pd.Series:
    return read("by_area").groupby("area")["crimes"].sum().sort_values(ascending=False)


# Finding 5: when, and how much of "when" is a guess --------------------------------------------------

def by_hour() -> pd.Series:
    return read("by_time").groupby("hour")["crimes"].sum()


def by_day_of_week() -> pd.Series:
    return read("by_time").groupby("dow")["crimes"].sum()[DAYS]


def time_quality() -> dict:
    clock = read("by_clock").set_index("time")["crimes"]
    days = read("by_day").set_index("day")["crimes"]
    table = read("by_time")
    identity = table[table["crime"] == IDENTITY].groupby("hour")["crimes"].sum()
    reported = read("by_reported")
    late = reported[reported["crime"] == IDENTITY].set_index("reported")["crimes"]
    return {
        "on_the_hour": clock[clock.index % 100 == 0].sum() / clock.sum(),
        "first_of_month": days[1] / days.loc[2:28].mean() - 1,
        "identity_at_noon": identity[12] / identity.sum(),
        "identity_late": late[["31 to 365 days", "Over a year"]].sum() / late.sum(),
    }


# Finding 6: arrests ------------------------------------------------------------------------------------

def outcomes() -> pd.DataFrame:
    """Arrest and still-open shares for the most common crimes, lowest arrest share first."""
    table = read("by_status")
    every = table.groupby("crime")["crimes"].sum()
    arrests = table[table["status"].isin(ARRESTS)].groupby("crime")["crimes"].sum().reindex(every.index, fill_value=0)
    still_open = table[table["status"] == OPEN].groupby("crime")["crimes"].sum().reindex(every.index, fill_value=0)
    return pd.DataFrame({"crimes": every, "arrest": arrests / every, "open": still_open / every})


def overall_outcomes() -> dict:
    table = read("by_status")
    whole = table["crimes"].sum()
    return {
        "arrest": table[table["status"].isin(ARRESTS)]["crimes"].sum() / whole,
        "open": table[table["status"] == OPEN]["crimes"].sum() / whole,
    }


# Finding 7: can the type of crime be predicted? --------------------------------------------------------

def split(crimes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train on 2020 to 2022 and test on 2023, the last full year before the switch."""
    return crimes[crimes["year"] <= 2022], crimes[crimes["year"] == 2023]


@lru_cache(maxsize=1)
def models() -> dict:
    train, test = split(sample())
    feature_sets = {
        "When only": ["hour", "dow", "month"],
        "When and police area": ["hour", "dow", "month", "area"],
        "When, area and type of place": ["hour", "dow", "month", "area", "premise"],
    }
    most_common = train["crime"].value_counts().index[0]
    accuracy = {"Always guess the most common": (test["crime"] == most_common).mean()}
    for name, columns in feature_sets.items():
        model = make_pipeline(
            OneHotEncoder(handle_unknown="ignore", min_frequency=50), LogisticRegression(max_iter=60, tol=1e-3)
        )
        # A longer fit takes minutes and only moves the score in the first decimal place
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            model.fit(train[columns], train["crime"])
        accuracy[name] = model.score(test[columns], test["crime"])
    return {"accuracy": pd.Series(accuracy), "train_size": len(train), "test_size": len(test), "most_common": most_common}


def first_version_baseline() -> float:
    """How often always guessing the most common crime is right, on the first version's filtered rows."""
    return float(cleaning_damage().pipe(lambda t: t["kept"].max() / t["kept"].sum()))
