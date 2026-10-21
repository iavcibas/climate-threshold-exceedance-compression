#!/usr/bin/env python3
"""p34_run.py -- P34 gate: how lossy compression changes heat-day counts, predicted from one number.

Pre-registration and theory: P34_PREREGISTRATION.docx (5 October 2026), which also states the corrected law for UQ.

Data   NOAA CPC Global Daily Maximum Temperature, 0.5 deg (tmax.YYYY.nc, ~81 MB per year), land cells only.
       PILOT year 2020 (code and data check; no rule is decided on it). CONFIRMATION years 2021-2024.
Codecs (applied to daily fields)
       UQ(eps): uniform scalar quantizer, step 2*eps, grid phase drawn once per eps (seeded): |error| <= eps, the
                quantization step of SZ-type error-bounded compressors without prediction.
       ZFP(eps): zfp fixed-accuracy mode, tolerance eps (zfpy), on each 2-D daily field, ocean filled with 0.
       eps in {0.05, 0.1, 0.25, 0.5, 1.0} degC; thresholds tau in {30, 35, 40} degC; "exceedance" = value > tau.
Law (first order in the error e, P12/P25 family, threshold form)
       flipped day-cells   F  = N p0 E|e|
       net count change    dC = N ( p0 E[e] - p1 E[e^2] / 2 )
       N = number of valid day-cells, p0 = density of Tmax at tau, p1 = its slope at tau (both from the ORIGINAL
       data of the same years: h0 = 0.25 degC window for p0, h1 = 1.0 degC for p1); error moments over values
       within 2*eps of tau.
Pre-registered rules (confirmation years only)
  NOTE (5 Oct): the selftest showed that a pointwise quantizer moves all of tau's cell to one side, so for UQ the
  law is F = N p0 d_tau (d_tau = distance from tau to the cell boundary on the far side of the reconstruction point)
  and the count change is +-F; for ZFP the prediction is the plug-in sum below. Rules K1-K3 as implemented in rules().
  K1 (flips)  cells (codec, eps, tau) with >= 30 measured flips: |F_meas - F_pred| <= max(0.15 F_pred, 2 sqrt(F_pred))
              in >= 80 % of them.
  K2 (bias)   cells with >= 100 flips: |dC_meas - dC_pred| <= 2 sqrt(F_meas) + 0.15 |dC_pred| in >= 80 % of them.
  K3 (sign)   every cell where |dC_pred| > 2 sqrt(F_pred): sign(dC_meas) = sign(dC_pred).
  Reading: K1-K3 pass -> paper (threshold-count QoIs under lossy compression: a law, plus the certified alternative).
  K1 fails -> close.

Usage
  pip install netCDF4 zfpy        (zfpy optional: without it only UQ is run, and the rules apply to UQ)
  python p34_run.py --selftest    synthetic fields, no download
  python p34_run.py --pilot       needs tmax.2020.nc in ./data
  python p34_run.py --confirm     needs tmax.2021.nc ... tmax.2024.nc in ./data
"""
import argparse, json, math, os, time
import numpy as np

EPS = [0.05, 0.1, 0.25, 0.5, 1.0]
TAUS = [30.0, 35.0, 40.0]
H0, H1 = 0.25, 1.0
SEED = 20261012
ZFP_REQUIRED = False   # set by main(): True when zfpy is available
PILOT, CONFIRM = [2020], [2021, 2022, 2023, 2024]
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

lines = []
def log(s=""):
    print(s, flush=True); lines.append(s)

def load_year(y):
    from netCDF4 import Dataset
    p = os.path.join(DATA, f"tmax.{y}.nc")
    if not os.path.exists(p): raise SystemExit(f"missing {p}: see P34_INSTRUCTIONS")
    with Dataset(p) as d:
        v = d.variables["tmax"]; v.set_auto_mask(True)
        a = v[:]                                      # masked array (time, lat, lon)
    x = np.ma.filled(a.astype(np.float64), np.nan)
    x[(x < -90) | (x > 70)] = np.nan
    return x

def synthetic(ndays=60, seed=1):
    rng = np.random.default_rng(seed)
    lat = np.linspace(-89.75, 89.75, 360)[:, None]; lon = np.linspace(0, 359.5, 720)[None, :]
    base = 30 - 0.45 * np.abs(lat) + 3 * np.sin(np.radians(lon) * 3)
    land = (np.sin(np.radians(lon) * 2) + np.cos(np.radians(lat) * 3)) > 0.3
    out = []
    for t in range(ndays):
        f = base + 6 * np.sin(2 * np.pi * t / 365) + rng.normal(0, 3, base.shape)
        f = np.round(f, 2); f[~land] = np.nan; out.append(f)
    return np.stack(out)

def uq(x, eps, phase):
    d = 2 * eps
    return d * (np.floor((x - phase) / d) + 0.5) + phase

def cert(x, eps, tau):
    """threshold-aligned quantizer for one tau: tau is a cell boundary, cells are right-closed (b, b + d], so a
    value equal to tau stays at or below tau (not an exceedance) and every exceedance stays an exceedance"""
    d = 2 * eps
    return d * (np.ceil((x - tau) / d) - 0.5) + tau

def zfp_day(f, eps):
    import zfpy
    m = np.isnan(f); g = np.where(m, 0.0, f)
    r = zfpy.decompress_numpy(zfpy.compress_numpy(g, tolerance=eps))
    r = r.astype(np.float64); r[m] = np.nan
    return r

def analyse(x, tag, use_zfp):
    v = x[np.isfinite(x)]; N = v.size
    gran = np.diff(np.unique(np.round(v[:200000], 4)))
    gran = float(np.median(gran[gran > 0])) if gran.size else float("nan")
    log(f"  {tag}: N = {N} valid day-cells; value granularity (median spacing of distinct values) {gran:.4f} degC")
    dens = {}
    for tau in TAUS:
        p0 = float(np.sum(np.abs(v - tau) < H0)) / (2 * H0 * N)
        p1 = (float(np.sum((v >= tau) & (v < tau + H1))) - float(np.sum((v < tau) & (v >= tau - H1)))) / (H1 ** 2 * N)
        ex = int(np.sum(v > tau))
        dens[tau] = (p0, p1)
        log(f"    tau {tau:.0f}: exceedances {ex}, p0 = {p0:.5f} /degC, p1 = {p1:.6f} /degC^2")
    rng = np.random.default_rng(SEED)
    codecs = [("UQ", e) for e in EPS] + [("CERT", e) for e in EPS] + ([("ZFP", e) for e in EPS] if use_zfp else [])
    cells = []
    for name, eps in codecs:
        t0 = time.time()
        phase = None
        if name == "UQ":
            phase = float(rng.uniform(0, 2 * eps)); xr = uq(x, eps, phase)
        elif name == "CERT":
            xr = None                                     # built per threshold below
        else:
            xr = np.stack([zfp_day(x[t], eps) for t in range(x.shape[0])])
        ok = np.isfinite(x)
        a = x[ok]
        if xr is not None:
            b = xr[ok]; e = b - a; maxerr = float(np.max(np.abs(e)))
        for tau in TAUS:
            if name == "CERT":
                b = cert(a, eps, tau); e = b - a; maxerr = float(np.max(np.abs(e)))
            p0, p1 = dens[tau]
            near = np.abs(a - tau) <= 2 * eps
            en = e[near] if near.any() else e
            Eabs, Ee, Ee2 = float(np.mean(np.abs(en))), float(np.mean(en)), float(np.mean(en ** 2))
            Fm = int(np.sum((a > tau) != (b > tau))); dCm = int(np.sum(b > tau)) - int(np.sum(a > tau))
            if name in ("UQ", "CERT"):
                # pointwise quantizer: the cell holding tau maps to one side; flips = values between tau and the
                # nearest cell boundary on the far side of the reconstruction point, all in one direction
                d = 2 * eps; ph = phase if name == "UQ" else (tau % d) - 1e-12
                lo = d * math.floor((tau - ph) / d) + ph; r = lo + eps
                dist = (tau - lo) if r > tau else (lo + d - tau)
                Fp = N * p0 * dist; dCp = Fp if r > tau else -Fp
            else:
                # plug-in law: each original value x near tau crosses with probability P(e > tau - x) (x <= tau) or
                # P(e <= tau - x) (x > tau), e drawn from the codec's errors near tau, taken independent of x.
                # Handles data stored on a finite grid (ties at tau) without a density estimate.
                es = np.sort(en); m = len(es); w = np.abs(a - tau) <= float(np.max(np.abs(es)))
                xv = a[w]; u = tau - xv
                up = (m - np.searchsorted(es, u[xv <= tau], side="right")) / m        # P(e > tau - x)
                dn = np.searchsorted(es, u[xv > tau], side="right") / m               # P(e <= tau - x)
                Fp = float(up.sum() + dn.sum()); dCp = float(up.sum() - dn.sum())
                F_closed = N * p0 * Eabs
            cells.append(dict(codec=name, eps=eps, tau=tau, F_meas=Fm, F_pred=Fp, F_closed=(F_closed if name == "ZFP" else Fp), dC_meas=dCm, dC_pred=dCp,
                              Eabs=Eabs, Ee=Ee, Ee2=Ee2, maxerr=maxerr, exceed=int(np.sum(a > tau))))
        log(f"    {name}({eps}): max |e| {maxerr:.4f}, {time.time() - t0:.0f} s")
    return N, gran, dens, cells

def rules(cells):
    k0 = [c for c in cells if c["codec"] == "CERT"]
    K0 = all(c["F_meas"] == 0 for c in k0)
    k1 = [c for c in cells if c["codec"] == "UQ" and c["F_meas"] >= 30]
    k1_in = [abs(c["F_meas"] - c["F_pred"]) <= max(0.15 * c["F_pred"], 2 * math.sqrt(max(c["F_pred"], 1))) for c in k1]
    k2 = [c for c in cells if c["codec"] == "ZFP" and c["F_meas"] >= 30]
    k2_in = [abs(c["F_meas"] - c["F_pred"]) <= max(0.15 * c["F_pred"], 2 * math.sqrt(max(c["F_pred"], 1))) for c in k2]
    k3 = [c for c in cells if c["codec"] == "UQ" and c["F_meas"] >= 30]
    k3_in = [np.sign(c["dC_meas"]) == np.sign(c["dC_pred"]) and abs(c["dC_meas"]) == c["F_meas"] for c in k3]
    K1 = len(k1) > 0 and sum(k1_in) >= math.ceil(0.8 * len(k1))
    K2 = (len(k2) == 0 and not ZFP_REQUIRED) or (len(k2) > 0 and sum(k2_in) >= math.ceil(0.8 * len(k2)))
    K3 = all(k3_in) and K0
    return K1, K2, K3, (sum(k1_in), len(k1)), (sum(k2_in), len(k2)), (sum(k3_in), len(k3))

def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--pilot", action="store_true"); g.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    try:
        import zfpy  # noqa
        use_zfp = True
    except Exception:
        use_zfp = False
    global ZFP_REQUIRED; ZFP_REQUIRED = use_zfp
    tag = "selftest" if a.selftest else ("pilot" if a.pilot else "confirm")
    log(f"P34 gate ({tag}), seed {SEED}, zfp {'available' if use_zfp else 'NOT available (UQ only)'}")
    if a.selftest: x = synthetic()
    else: x = np.concatenate([load_year(y) for y in (PILOT if a.pilot else CONFIRM)])
    N, gran, dens, cells = analyse(x, tag, use_zfp)
    log("\n==== cells ====")
    for c in cells:
        log(f"  {c['codec']:<3} eps {c['eps']:<4} tau {c['tau']:.0f} | flips {c['F_meas']:7d} pred {c['F_pred']:9.1f} | "
            f"count change {c['dC_meas']:+7d} pred {c['dC_pred']:+9.1f} | exceedances {c['exceed']}")
    K1, K2, K3, r1, r2, r3 = rules(cells)
    log("\n==== Pre-registered rules" + (" (decided on the confirmation years only)" if tag == "confirm" else " (NOT decided: " + tag + ")") + " ====")
    log(f"K1 (UQ flips = N p0 d_tau within max(15 %, 2 sqrt)): {r1[0]}/{r1[1]} -> {'PASS' if K1 else 'FAIL'} (rule: at least 80 %)")
    log(f"K2 (ZFP flips = plug-in crossing sum within max(15 %, 2 sqrt)): {r2[0]}/{r2[1]} -> {'PASS' if K2 else 'FAIL'} (rule: at least 80 %)")
    log(f"K3 (UQ: all flips one-way with the predicted sign; CERT: zero flips): {r3[0]}/{r3[1]} -> {'PASS' if K3 else 'FAIL'} (rule: all)")
    if tag == "confirm":
        v = "Both flip laws and the one-way bias hold; the aligned grid removes every flip -> paper." if (K1 and K2 and K3) else ("Flip law fails -> close." if not (K1 or K2) else "Mixed -> reported per rule.")
        log("Verdict: " + v)
    json.dump({"tag": tag, "N": N, "granularity": gran, "density": {str(k): v for k, v in dens.items()}, "cells": cells,
               "K": [K1, K2, K3], "counts": [r1, r2, r3], "zfp": use_zfp}, open(f"p34_{tag}.json", "w"), indent=1, default=float)
    open(f"p34_{tag}.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n"); log(f"written p34_{tag}.json / .txt")

if __name__ == "__main__":
    main()
