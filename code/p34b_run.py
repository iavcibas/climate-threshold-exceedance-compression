#!/usr/bin/env python3
"""p34b_run.py -- P34b: the codecs climate archives actually use.

P34 tested a fixed-grid uniform quantizer (UQ, grid phase drawn at random), ZFP and a threshold-aligned grid.
P34b adds, on the same data (pilot 2020; confirmation 2021-2024):
  PACK(s)     netCDF/GRIB-style packing with scale s and offset 0: x_hat = s * round(x / s),
              s in {0.01, 0.05, 0.1, 0.25, 0.5} degC. Thresholds 30/35/40 degC are grid points.
  BITROUND(k) round-to-nearest (ties to even) of the float32 mantissa to k bits (as numcodecs BitRound / Kloewer et
              al.), k in {5, 6, 7, 8, 9}. Grid spacing at tau: h = 2**(floor(log2 tau) - k); tau is representable.
  LORENZO(eps) SZ-1-style predictive quantizer along longitude: prediction = previous reconstructed land value in
              the row (0 at the row start), residual quantized with step 2*eps. eps in {0.05, 0.1, 0.25, 0.5, 1.0}.
              Integer predictor weights keep every reconstruction on the lattice 2*eps*Z (found in the selftest).
  NIPRED(eps)  same with the non-integer prediction 0.75 r[j-1] + 0.25 r[j-2]: the lattice refines, errors random.
Predictions (from the original data and the codec's definition only)
  PACK, BITROUND: tau is a reconstruction point, its cell is [tau - h/2, tau + h/2] (h = s or the bit-rounding step),
     so exactly the values in (tau, tau + h/2] lose their exceedance: F = N p0 h/2, all downward (dC = -F).
  LORENZO: lattice 2*eps*Z, same rule as PACK with h = 2*eps (direction from where tau sits on the lattice).
  NIPRED: errors behave as random: F from the P34 plug-in crossing sum; net change two-way (|dC| small against F).
Pre-registered rules (confirmation years only)
  B1  PACK, BITROUND, LORENZO cells with >= 30 flips: F within max(0.15 F_pred, 2 sqrt(F_pred)) of the lattice law in >= 80 %.
  B2  the same cells: every flip in one direction, the predicted one (|dC| = F, sign as predicted), in all of them.
  B3  NIPRED cells with >= 30 flips: F within the B1 tolerance of the plug-in sum in >= 80 %, AND |dC| <= 0.2 F in
      >= 80 % (no one-way bias).
All decompressed fields are cast to float32, as stored in an archive (this also removes float64 round-off in
the predictive codecs, which otherwise decides comparisons with a threshold that lies on the lattice).
Usage: python p34b_run.py --pilot | --confirm | --selftest
"""
import argparse, json, math, time
import numpy as np
import p34_run as base

PACK_S = [0.01, 0.05, 0.1, 0.25, 0.5]
KEEP = [5, 6, 7, 8, 9]
EPS = [0.05, 0.1, 0.25, 0.5, 1.0]
TAUS = base.TAUS
lines = []
def log(s=""):
    print(s, flush=True); lines.append(s)

def bitround(x, k):
    a = x.astype(np.float32); m = np.isnan(a)
    b = a.view(np.uint32).copy(); mb = 23 - k
    b += ((b >> mb) & 1) + np.uint32((1 << (mb - 1)) - 1)
    b &= np.uint32(~((1 << mb) - 1) & 0xFFFFFFFF)
    r = b.view(np.float32).astype(np.float64); r[m] = np.nan
    return r

def predictive(x, eps, w1=1.0, w2=0.0):
    """x: (T, lat, lon); predictive quantization along lon, per (T, lat) row, prediction w1*r[j-1] + w2*r[j-2]
    over the previous reconstructed land values (0 before the first); residual quantized with step 2*eps.
    w1 = 1, w2 = 0 is 1-D Lorenzo (integer weights: reconstructions stay on the lattice 2*eps*Z);
    w1 = 0.75, w2 = 0.25 is a non-integer predictor (the lattice refines at every step)."""
    d = 2 * eps; T, H, W = x.shape
    out = np.full_like(x, np.nan); p1 = np.zeros((T, H)); p2 = np.zeros((T, H))
    for j in range(W):
        col = x[:, :, j]; ok = np.isfinite(col); pred = w1 * p1 + w2 * p2
        rec = pred + d * np.round((np.where(ok, col, pred) - pred) / d)
        out[:, :, j] = np.where(ok, rec, np.nan)
        p2 = np.where(ok, p1, p2); p1 = np.where(ok, rec, p1)
    return out

def lattice_pred(N, p0, tau, d, c=0.0):
    """pointwise rounding to the lattice c + d Z: the reconstruction point r nearest to tau collects the cell
    [r - d/2, r + d/2]; returns (flips, signed count change)"""
    r = c + d * round((tau - c) / d)
    if abs(r - tau) < 1e-9 * d: F = N * p0 * d / 2; return F, -F          # tau representable: (tau, tau+d/2] lost
    if r > tau: F = N * p0 * (tau - (r - d / 2)); return F, F             # [r-d/2, tau] gained
    F = N * p0 * (r + d / 2 - tau); return F, -F                          # (tau, r+d/2) lost

def run(x, tag):
    v = x[np.isfinite(x)]; N = v.size
    p0 = {t: float(np.sum(np.abs(v - t) < base.H0)) / (2 * base.H0 * N) for t in TAUS}
    log(f"  {tag}: N = {N}; p0 = " + ", ".join(f"{t:.0f}: {p0[t]:.5f}" for t in TAUS))
    cells = []
    codecs = [("PACK", s) for s in PACK_S] + [("BITROUND", k) for k in KEEP] + [("LORENZO", e) for e in EPS] + [("NIPRED", e) for e in EPS]
    ok = np.isfinite(x); a = x[ok]
    for name, par in codecs:
        t0 = time.time()
        if name == "PACK": xr = par * np.round(x / par)
        elif name == "BITROUND": xr = bitround(x, par)
        elif name == "LORENZO": xr = predictive(x, par)
        else: xr = predictive(x, par, 0.75, 0.25)
        xr = xr.astype(np.float32).astype(np.float64)        # archives store the decompressed field as float32
        b = xr[ok]; e = b - a; maxerr = float(np.nanmax(np.abs(e)))
        for tau in TAUS:
            Fm = int(np.sum((a > tau) != (b > tau))); dCm = int(np.sum(b > tau)) - int(np.sum(a > tau))
            if name in ("PACK", "BITROUND", "LORENZO"):
                d = par if name == "PACK" else (2.0 ** (math.floor(math.log2(tau)) - par) if name == "BITROUND" else 2 * par)
                Fp, dCp = lattice_pred(N, p0[tau], tau, d)
            else:
                win = np.abs(a - tau) <= 2 * par; en = np.sort(e[win]); m = len(en)
                w = np.abs(a - tau) <= float(np.max(np.abs(en))); xv = a[w]; u = tau - xv
                up = (m - np.searchsorted(en, u[xv <= tau], side="right")) / m
                dn = np.searchsorted(en, u[xv > tau], side="right") / m
                Fp = float(up.sum() + dn.sum()); dCp = float(up.sum() - dn.sum())
            cells.append(dict(codec=name, par=par, tau=tau, F_meas=Fm, F_pred=Fp, dC_meas=dCm, dC_pred=dCp,
                              exceed=int(np.sum(a > tau)), maxerr=maxerr))
        log(f"    {name}({par}): max |e| {maxerr:.4f}, {time.time() - t0:.0f} s")
    return N, cells

def rules(cells):
    tol = lambda c: abs(c["F_meas"] - c["F_pred"]) <= max(0.15 * c["F_pred"], 2 * math.sqrt(max(c["F_pred"], 1)))
    fixed = [c for c in cells if c["codec"] in ("PACK", "BITROUND", "LORENZO") and c["F_meas"] >= 30]
    lor = [c for c in cells if c["codec"] == "NIPRED" and c["F_meas"] >= 30]
    b1 = sum(tol(c) for c in fixed); b2 = sum(abs(c["dC_meas"]) == c["F_meas"] and np.sign(c["dC_meas"]) == np.sign(c["dC_pred"]) for c in fixed)
    b3a = sum(tol(c) for c in lor); b3b = sum(abs(c["dC_meas"]) <= 0.2 * c["F_meas"] for c in lor)
    B1 = len(fixed) > 0 and b1 >= math.ceil(0.8 * len(fixed)); B2 = len(fixed) > 0 and b2 == len(fixed)
    B3 = len(lor) > 0 and b3a >= math.ceil(0.8 * len(lor)) and b3b >= math.ceil(0.8 * len(lor))
    return B1, B2, B3, (b1, len(fixed)), (b2, len(fixed)), (b3a, b3b, len(lor))

def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--pilot", action="store_true"); g.add_argument("--confirm", action="store_true")
    a = ap.parse_args(); tag = "selftest" if a.selftest else ("pilot" if a.pilot else "confirm")
    log(f"P34b ({tag})")
    if a.selftest:
        rng = np.random.default_rng(3); x = base.synthetic() + rng.uniform(-0.005, 0.005, (60, 360, 720))
    else:
        x = np.concatenate([base.load_year(y) for y in (base.PILOT if a.pilot else base.CONFIRM)])
    N, cells = run(x, tag)
    log("\n==== cells ====")
    for c in cells:
        log(f"  {c['codec']:<8} {c['par']:<5} tau {c['tau']:.0f} | flips {c['F_meas']:8d} pred {c['F_pred']:10.1f} | count change {c['dC_meas']:+9d} pred {c['dC_pred']:+10.1f} | exceedances {c['exceed']}")
    B1, B2, B3, r1, r2, r3 = rules(cells)
    log("\n==== Pre-registered rules" + (" (decided on the confirmation years only)" if tag == "confirm" else f" (NOT decided: {tag})") + " ====")
    log(f"B1 (lattice codecs PACK/BITROUND/LORENZO: flips = lattice law): {r1[0]}/{r1[1]} -> {'PASS' if B1 else 'FAIL'} (rule: at least 80 %)")
    log(f"B2 (lattice codecs: all flips one-way, predicted sign): {r2[0]}/{r2[1]} -> {'PASS' if B2 else 'FAIL'} (rule: all)")
    log(f"B3 (NIPRED: plug-in flips {r3[0]}/{r3[2]}, two-way |dC| <= 0.2 F {r3[1]}/{r3[2]}) -> {'PASS' if B3 else 'FAIL'} (rule: both at least 80 %)")
    json.dump({"tag": tag, "N": N, "cells": cells, "B": [B1, B2, B3]}, open(f"p34b_{tag}.json", "w"), indent=1, default=float)
    open(f"p34b_{tag}.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n"); log(f"written p34b_{tag}.json / .txt")

if __name__ == "__main__":
    main()
