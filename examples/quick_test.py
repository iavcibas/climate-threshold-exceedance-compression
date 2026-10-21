#!/usr/bin/env python3
"""Quick test (about 10 seconds, NumPy only, no data download).

It builds a small synthetic daily-maximum-temperature field (30 days on a 0.5-degree global grid, smooth in
longitude, with a land mask) and checks the central result of the paper on it, using the codec and prediction
functions of the scripts in ../code:

  1. Packing with scale s and offset 0 (x_hat = s * round(x / s)) puts the threshold tau on the grid. The paper
     predicts that exactly the values in (tau, tau + s/2] lose their exceedance: F = N p0 s/2 changed decisions,
     all downward, where N is the number of values and p0 the density of the ORIGINAL data at tau.
  2. Bit rounding of the float32 mantissa to k bits: the same law with the grid step h = 2**(floor(log2 tau) - k).
  3. A one-dimensional Lorenzo predictive quantizer with error bound eps: the same law with h = 2 eps.
  4. Packing with offset s/2 (the threshold-aligned remedy): tau is a cell boundary, no decision changes.
     Cells are right-closed, (b, b + s], so a stored value exactly equal to tau is resolved downward, as in
     Section 2.4 of the paper (the synthetic values are stored with 0.01 degC resolution, so such ties occur).

For each case the script prints the measured and predicted number of changed decisions and the count change,
and applies the tolerance of the paper's rule B1: |F_meas - F_pred| <= max(0.15 F_pred, 2 sqrt(F_pred)).
It ends with "QUICK TEST PASSED" (exit code 0) or "QUICK TEST FAILED" (exit code 1).

Run from the repository root or from this folder:
    python examples/quick_test.py
Expected output: examples/expected_output.txt (the numbers are reproducible; the timing line may differ).
"""
import math, os, sys, time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import p34_run as base      # noqa: E402  (imports NumPy only; netCDF4 is needed only to read the real data)
import p34b_run as b        # noqa: E402

TAUS = [30.0, 35.0]


def synthetic_field(ndays=30, seed=7):
    """Smooth-in-longitude synthetic Tmax (degC), stored with 0.01 degC resolution, ocean = NaN."""
    rng = np.random.default_rng(seed)
    lat = np.linspace(-89.75, 89.75, 360)[:, None]
    lon = np.linspace(0, 359.5, 720)[None, :]
    clim = 31 - 0.45 * np.abs(lat) + 4 * np.sin(np.radians(lon) * 3)
    land = (np.sin(np.radians(lon) * 2) + np.cos(np.radians(lat) * 3)) > 0.3
    out = []
    for t in range(ndays):
        noise = np.cumsum(rng.normal(0, 0.35, (360, 720)), axis=1)          # random walk along longitude
        noise -= noise.mean(axis=1, keepdims=True)
        f = clim + 3 * np.sin(2 * np.pi * t / 30) + 0.5 * noise + rng.normal(0, 0.3, (360, 720))
        f = np.round(f, 2)
        f[~land] = np.nan
        out.append(f)
    return np.stack(out)


def tol_ok(F_meas, F_pred):
    return abs(F_meas - F_pred) <= max(0.15 * F_pred, 2 * math.sqrt(max(F_pred, 1)))


def main():
    t0 = time.time()
    x = synthetic_field()
    ok = np.isfinite(x)
    a = x[ok]
    N = a.size
    p0 = {t: float(np.sum(np.abs(a - t) < base.H0)) / (2 * base.H0 * N) for t in TAUS}
    print(f"Synthetic field: {x.shape[0]} days x 360 x 720, N = {N} valid values")
    print("Density of the original data at tau: " + ", ".join(f"p0({t:.0f}) = {p0[t]:.5f} /degC" for t in TAUS))

    cases = [
        ("PACK s=0.25, offset 0", lambda z: 0.25 * np.round(z / 0.25), 0.25, True),
        ("BITROUND k=7", lambda z: b.bitround(z, 7), None, True),
        ("LORENZO eps=0.25", lambda z: b.predictive(z, 0.25), 0.5, True),
        ("PACK s=0.25, aligned (offset s/2)", lambda z: 0.25 * (np.ceil(z / 0.25) - 0.5), None, False),
    ]
    all_pass = True
    print()
    print(f"{'codec':<36}{'tau':>5}{'F measured':>12}{'F predicted':>13}{'count change':>14}   check")
    for name, codec, h, on_grid in cases:
        xr = codec(x).astype(np.float32).astype(np.float64)       # stored as float32, as in an archive
        r = xr[ok]
        for tau in TAUS:
            Fm = int(np.sum((a > tau) != (r > tau)))
            dCm = int(np.sum(r > tau)) - int(np.sum(a > tau))
            if on_grid:
                step = h if h is not None else 2.0 ** (math.floor(math.log2(tau)) - 7)
                Fp, dCp = b.lattice_pred(N, p0[tau], tau, step)
                passed = tol_ok(Fm, Fp) and dCm == -Fm and Fm > 0       # law holds, every change downward
            else:
                Fp, dCp = 0.0, 0.0
                passed = Fm == 0                                         # aligned grid: no decision changes
            all_pass &= passed
            print(f"{name:<36}{tau:>5.0f}{Fm:>12d}{Fp:>13.1f}{dCm:>+14d}   {'ok' if passed else 'FAIL'}")
    print()
    print(f"Elapsed: {time.time() - t0:.1f} s")
    if all_pass:
        print("QUICK TEST PASSED: on-grid codecs lose the predicted number of exceedances (all downward);")
        print("the threshold-aligned grid changes no decision.")
        return 0
    print("QUICK TEST FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
