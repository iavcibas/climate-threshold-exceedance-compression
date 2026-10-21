# Threshold exceedances under lossy compression

Code, pre-registrations and results for

> I. Avcibas, "Lossy compression shifts heat-day counts in one direction: a predictive law and a threshold-aligned remedy," submitted to *Computers & Geosciences*, 2026.

Version 1.0.0. Licence: MIT (see `LICENSE`). Contact: ismail.avcibas@ostimteknik.edu.tr.

## What the code does

The scripts take the NOAA CPC Global Unified daily maximum temperature (0.5 degree grid, land cells), compress every daily field with a lossy codec, and count how many threshold decisions ("is the value above 30, 35 or 40 degC?") change. They compare these counts with predictions made from the original data alone.

| Script | Purpose |
|---|---|
| `code/p34_run.py` | First pre-registered test: a uniform quantizer with a random grid phase (UQ), ZFP and a threshold-aligned grid (CERT). Rules K1-K3. |
| `code/p34b_run.py` | Second pre-registered test: netCDF packing (PACK), mantissa bit rounding (BITROUND), a Lorenzo predictive quantizer (LORENZO) and a predictor with non-integer weights (NIPRED). Rules B1-B3. Imports `p34_run.py`. |
| `code/diag_nipred.py` | Diagnosis, on the pilot year, of why the NIPRED prediction fails (error depends on the local gradient and on the value). |
| `code/fig_p34.py` | Draws Fig. 1 of the paper from the two confirmation result files. |

## Installation and computational requirements

- Python 3 (the runs used Python 3.10 under WSL Ubuntu) with the packages in `requirements.txt`: `pip install -r requirements.txt`. If `zfpy` cannot be installed, `p34_run.py` runs without the ZFP arm.
- No GPU is needed. Memory: one four-year array in double precision occupies 3.0 GB; the runs were made on a laptop with 32 GB of memory. Each confirmation run takes a few minutes.

## Data (not included)

Download the yearly files into `code/data/` (about 81 MB each) from NOAA PSL:

```
cd code/data
for y in 2020 2021 2022 2023 2024; do
  wget https://psl.noaa.gov/thredds/fileServer/Datasets/cpc_global_temp/tmax.$y.nc
done
cd ..
```

2020 is the pilot year (no rule is decided on it); 2021-2024 are the confirmation years.

## Reproducing the paper

Run from `code/`:

```
python p34_run.py --selftest      # synthetic data, checks the code
python p34_run.py --pilot         # 2020
python p34_run.py --confirm       # 2021-2024 -> p34_confirm.txt / .json
python p34b_run.py --selftest
python p34b_run.py --pilot
python p34b_run.py --confirm      # -> p34b_confirm.txt / .json
python diag_nipred.py             # diagnosis on 2020
python fig_p34.py                 # Fig. 1 -> p34_fig1.pdf / .png
```

Inputs: the netCDF files in `code/data/`. Options: exactly one of `--selftest`, `--pilot`, `--confirm`. Outputs, written to the working directory: a text report ending with the pre-registered rules and a verdict, and a JSON file with every (codec, setting, threshold) cell: measured and predicted number of changed decisions, measured and predicted net change of the count, and the number of exceedances. The files in `results/` are the outputs of the runs reported in the paper; every number in the paper can be read from `results/p34_confirm.txt` and `results/p34b_confirm.txt`.

## Order of events

1. `p34_run.py` was tested on synthetic data, then the first pre-registration (`preregistrations/P34_PREREGISTRATION.md`) was written, then the pilot and the confirmation runs were made. All three rules passed.
2. `p34b_run.py` was written and registered (`P34B_PREREGISTRATION.md`) after the first test had passed and before its codecs were run on real data. B1 and B2 passed; B3 (NIPRED) failed on the pilot year and on the confirmation years. The pilot diagnosis is in `P34B_PILOT_NOTE.md`. The rules were not changed.

The pre-registration, instruction and result notes are written in Turkish; their rules are stated in English in Section 3 of the paper and in the docstrings of the scripts.

## Change made after the runs

Only line 4 of the docstring of `p34_run.py` was edited after the runs, to name the existing pre-registration document instead of a theory note that does not exist. No code was changed.
