# Changelog

All notable changes to this project are listed here. Versions are dated by month, like `v2026.11`.

## v2026.11 · November 2026

A full rebuild, from a single notebook into a tested, reproducible analysis.

### Fixed

- Dropping rows with blank fields deleted 99.5% of stolen vehicle reports, the most common crime in the data. Those rows
  are now kept, and a test guards them
- Yearly charts treated 2024 as a real fall. Trends now stop at 7 March 2024, when LAPD changed records systems
- The model's 10% accuracy was never compared with simply guessing. It now is, using a test on later crimes
- The crimes-by-year chart had the wrong axis labels
- The data wasn't in the repo, so the notebook couldn't run. The repo now holds summaries and a fixed sample

### Added

- A findings report with seven findings, every number worked out from the data
- Eight charts and three headline tiles, all drawn with [bezel-charts](https://pypi.org/project/bezel-charts/)
- `data/prepare.py` to rebuild the data from the full download, leaving out addresses, coordinates, record numbers and
  victim descent
- Tests, an automatic check on every pull request, Dependabot and a security policy
- Social preview image in `assets/social-preview.png`

### Changed

- New folder structure: `data/`, `findings/`, `notebooks/`, `charts/` and `tests/`
- README rewritten around the findings
- Notebook rewritten and moved to `notebooks/crime_data_analysis.ipynb`

## January 2026

- First version: one notebook and a README
