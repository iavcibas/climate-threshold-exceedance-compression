import numpy as np, p34_run as base, p34b_run as b, time
x = base.load_year(2020); ok = np.isfinite(x); a = x[ok]; N = a.size
for eps in [0.05, 0.1, 0.25, 0.5, 1.0]:
    xr = b.predictive(x, eps, 0.75, 0.25).astype(np.float32).astype(np.float64)
    # dead band: fraction where reconstruction equals prediction (k = 0); recompute pred
    e_all = xr - x
    g = np.full_like(x, np.nan); g[:, :, 1:] = x[:, :, 1:] - x[:, :, :-1]   # eastward difference
    e = e_all[ok]; gg = g[ok]
    for tau in [30, 35, 40]:
        near = np.abs(a - tau) < 0.05
        win = np.abs(a - tau) <= 2 * eps
        Fm = int(np.sum((a > tau) != (xr[ok] > tau))); dC = int(np.sum(xr[ok] > tau) - np.sum(a > tau))
        p0 = near.sum() / (0.1 * N)
        up = near & (gg > 0); dn = near & (gg < 0)
        print(f"eps {eps} tau {tau}: flips {Fm} dC {dC:+d} | E[e|x~tau] {e[near].mean():+.4f} (window {e[win].mean():+.4f}) "
              f"N p0 E[e|x~tau] {N*p0*e[near].mean():+.0f} | E|e| near {np.abs(e[near]).mean():.4f} window {np.abs(e[win]).mean():.4f} "
              f"N p0 E|e|near {N*p0*np.abs(e[near]).mean():.0f} | E[e|grad>0] {e[up].mean():+.3f} E[e|grad<0] {e[dn].mean():+.3f}", flush=True)
