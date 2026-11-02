"""Turn the full Los Angeles crime download into small files that can live in this repo.

The original file is about 300 MB, so it isn't committed. Download it, then run:

    curl -fL -o crime.csv 'https://data.lacity.org/api/v3/views/2nrs-mtv8/export.csv?accessType=DOWNLOAD'
    python data/prepare.py crime.csv

Monthly totals cover the whole file. Every other table and the sample stop before 7 March 2024, when LAPD changed
records systems and this dataset became incomplete. Addresses, coordinates, record numbers and victim descent are
left out of everything written here.
"""

import sys
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent
SWITCH = "2024-03-07"
USE = ["Date Rptd", "DATE OCC", "TIME OCC", "AREA NAME", "Part 1-2", "Crm Cd Desc", "Mocodes", "Vict Age", "Vict Sex",
       "Vict Descent", "Premis Cd", "Premis Desc", "Weapon Desc", "Status", "Status Desc", "Crm Cd 1"]
OLD_REQUIRED = ["Mocodes", "Vict Sex", "Vict Descent", "Premis Cd", "Premis Desc", "Status", "Crm Cd 1"]
# The city has published dates both ways over time
FORMATS = ["%Y %b %d %I:%M:%S %p", "%m/%d/%Y %I:%M:%S %p"]
LAG_BINS = [-100000, 0, 7, 30, 365, 100000]
LAG_LABELS = ["Same day", "1 to 7 days", "8 to 30 days", "31 to 365 days", "Over a year"]

WHOLE_FILE = {"by_month": ["year", "month", "crime", "old_kept"]}
BEFORE_SWITCH = {
    "by_area": ["area", "crime"],
    "by_time": ["hour", "dow", "crime"],
    "by_status": ["crime", "status"],
    "by_reported": ["crime", "reported"],
    "by_clock": ["time"],
    "by_day": ["day"],
}
SAMPLE = ["date", "year", "month", "dow", "hour", "area", "crime", "premise"]


def parse_dates(values):
    for layout in FORMATS:
        try:
            return pd.to_datetime(values, format=layout)
        except ValueError:
            continue
    raise ValueError(f"Unknown date layout, for example {values.iloc[0]!r}")


def tidy(raw):
    d = pd.DataFrame()
    occurred, reported = parse_dates(raw["DATE OCC"]), parse_dates(raw["Date Rptd"])
    d["date"] = occurred.dt.strftime("%Y-%m-%d")
    d["year"], d["month"], d["day"] = occurred.dt.year, occurred.dt.month, occurred.dt.day
    d["dow"] = occurred.dt.day_name()
    d["time"] = raw["TIME OCC"]
    d["hour"] = raw["TIME OCC"] // 100
    d["reported"] = pd.cut((reported - occurred).dt.days, LAG_BINS, labels=LAG_LABELS).astype(str)
    d["area"] = raw["AREA NAME"]
    d["crime"] = raw["Crm Cd Desc"]
    d["premise"] = raw["Premis Desc"].fillna("Not recorded")
    d["status"] = raw["Status Desc"]
    d["old_kept"] = raw[OLD_REQUIRED].notna().all(axis=1)
    return d


def table(rows, name, keys):
    rows.groupby(keys).size().rename("crimes").reset_index().to_csv(DATA / f"{name}.csv", index=False)


def write(d):
    for name, keys in WHOLE_FILE.items():
        table(d, name, keys)
    before = d[d["date"] < SWITCH]
    for name, keys in BEFORE_SWITCH.items():
        table(before, name, keys)
    sample = before.sample(n=min(200_000, len(before)), random_state=42).sort_values("date")
    sample[SAMPLE].to_csv(DATA / "crime_sample.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})


if __name__ == "__main__":
    source = Path(sys.argv[1])
    print(f"Reading {source.name}...")
    crimes = tidy(pd.read_csv(source, usecols=USE, low_memory=False))
    write(crimes)
    print(f"{len(crimes):,} crimes, {crimes['date'].min()} to {crimes['date'].max()}")
