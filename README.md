# Threshold exceedances under lossy compression

Code, pre-registrations and results for

> I. Avcibas, "Lossy compression shifts heat-day counts in one direction: a predictive law and a threshold-aligned remedy," submitted to *Computers & Geosciences*, 2026.

Version 1.0.1 (code identical to v1.0.0; a quick test and this README were added). Licence: MIT (see `LICENSE`).
Developer and contact: Ismail Avcibas, OSTIM Technical University, ismail.avcibas@ostimteknik.edu.tr.
Archived copy of v1.0.0: Zenodo, https://doi.org/10.5281/zenodo.23173071

## Purpose

Climate archives store data with lossy codecs: netCDF/GRIB packing, mantissa bit rounding, SZ-type predictive quantizers, ZFP. Users then count threshold exceedances, for example the number of days with a maximum temperature above 35 °C. This code measures how a codec changes such counts and compares the change with a prediction made from the original data alone.

The main result it tests: for every codec that rounds to a fixed grid, the threshold falls in one grid cell, and that whole cell moves to one side. When the threshold is itself a grid point (round thresholds with zero offset), exactly the values in (τ, τ + h/2] lose their exceedance, so the count drops by N·p0·h/2, where N is the number of values, p0 the density of the data at τ and h the grid step. Shifting the grid so that τ is a cell boundary removes the change.

## Requirements

- Python 3 (the runs in the paper used Python 3.10 under WSL Ubuntu; the quick test and self-tests were also checked with Python 3.13 and NumPy 2).
- Quick test and self-tests: NumPy only.
- Full runs: NumPy, netCDF4, zfpy (optional; without it the ZFP arm is skipped) and Matplotlib for the figure: `pip install -r requirements.txt`.
- No GPU. The full runs hold a four-year array in double precision (3.0 GB); they were made on a laptop with 32 GB of memory and take a few minutes each.

## Quick test (about 10 seconds, no download)

From the repository root:

```
pip install numpy
python examples/quick_test.py
```

The script builds a synthetic temperature field (30 days on a 0.5° global grid with a land mask), compresses it with packing (scale 0.25 °C, offset 0), bit rounding (7 mantissa bits), a one-dimensional Lorenzo predictive quantizer (error bound 0.25 °C) and the threshold-aligned packing, and compares the measured number of changed exceedance decisions at 30 °C and 35 °C with the prediction of the paper, using the functions in `code/`. It must end with

```
QUICK TEST PASSED: on-grid codecs lose the predicted number of exceedances (all downward);
the threshold-aligned grid changes no decision.
```

and exit with code 0. The full expected output is in `examples/expected_output.txt`; only the elapsed-time line may differ.

## Self-tests of the two experiment scripts (NumPy only, under a minute)

```
cd code
python p34_run.py --selftest     # writes p34_selftest.txt / .json
python p34b_run.py --selftest    # writes p34b_selftest.txt / .json
```

Each ends with the pre-registered rules evaluated on synthetic data (all PASS). Reference outputs: `results/p34_selftest.txt` and `results/p34b_selftest.txt` (those were made with zfpy installed; without it the ZFP lines are absent).

## Reproducing the paper

1. Download the NOAA CPC Global Unified daily maximum temperature, 0.5°, years 2020–2024 (about 81 MB per year), into `code/data/`:

   ```
   cd code/data
   for y in 2020 2021 2022 2023 2024; do
     wget https://psl.noaa.gov/thredds/fileServer/Datasets/cpc_global_temp/tmax.$y.nc
   done
   cd ..
   ```

   2020 is the pilot year (no rule is decided on it); 2021–2024 are the confirmation years.

2. Run from `code/`:

   ```
   python p34_run.py --pilot        # 2020
   python p34_run.py --confirm      # 2021-2024 -> p34_confirm.txt / .json
   python p34b_run.py --pilot
   python p34b_run.py --confirm     # -> p34b_confirm.txt / .json
   python diag_nipred.py            # diagnosis of the failed NIPRED prediction, on 2020
   python fig_p34.py                # Fig. 1 -> p34_fig1.pdf / .png (needs the two *_confirm.json files)
   ```

Each run script takes exactly one of `--selftest`, `--pilot`, `--confirm`. Outputs, written to the working directory: a text report ending with the pre-registered rules and a verdict, and a JSON file with every (codec, setting, threshold) cell: measured and predicted number of changed decisions, measured and predicted net change of the count, and the number of exceedances. The files in `results/` are the outputs of the runs reported in the paper; every number in the paper can be read from `results/p34_confirm.txt` and `results/p34b_confirm.txt`.

## Repository layout

| Path | Content |
|---|---|
| `code/p34_run.py` | First pre-registered test: uniform quantizer with a random grid phase (UQ), ZFP, and the threshold-aligned grid (CERT). Rules K1–K3. |
| `code/p34b_run.py` | Second pre-registered test: netCDF packing (PACK), mantissa bit rounding (BITROUND), Lorenzo predictive quantizer (LORENZO), predictor with non-integer weights (NIPRED). Rules B1–B3. Imports `p34_run.py`. |
| `code/diag_nipred.py` | Diagnosis, on the pilot year, of why the NIPRED prediction fails. |
| `code/fig_p34.py` | Draws Fig. 1 of the paper from the two confirmation result files. |
| `code/data/` | Place for the downloaded netCDF files (not included). |
| `examples/quick_test.py`, `examples/expected_output.txt` | Quick test and its expected output. |
| `results/` | Outputs of the self-tests, pilot and confirmation runs reported in the paper, and the result notes. |
| `preregistrations/` | Pre-registration, run instructions, literature scan and pilot note, as written before the runs. |
| `figures/` | Fig. 1 of the paper. |

## Order of events

1. `p34_run.py` was tested on synthetic data, then the first pre-registration (`preregistrations/P34_PREREGISTRATION.md`) was written, then the pilot and the confirmation runs were made. All three rules passed.
2. `p34b_run.py` was written and registered (`P34B_PREREGISTRATION.md`) after the first test had passed and before its codecs were run on real data. B1 and B2 passed; B3 (NIPRED) failed on the pilot year and on the confirmation years. The pilot diagnosis is in `P34B_PILOT_NOTE.md`. The rules were not changed.

The pre-registration, instruction and result notes are written in Turkish and kept as written (including the local paths of the author's machine); their rules are stated in English in Section 3 of the paper and in the docstrings of the scripts.

## Changes after the runs

- v1.0.0: only line 4 of the docstring of `p34_run.py` was edited after the runs, to name the existing pre-registration document instead of a theory note that does not exist. No code was changed.
- v1.0.1: `examples/` (quick test), `CITATION.cff`, `.gitignore` and this README added. No code in `code/` was changed.

## Citation

See `CITATION.cff`. Please cite the paper and the archived code (https://doi.org/10.5281/zenodo.23173071).
