"""Figure 1 of the P34 paper, from p34_confirm.json and p34b_confirm.json (confirmation years 2021-2024)."""
import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
a = json.load(open("p34_confirm.json"))["cells"]; b = json.load(open("p34b_confirm.json"))["cells"]
for c in a: c["par"] = c["eps"]
cells = [c for c in a if c["codec"] != "CERT"] + b
style = {"UQ": ("#1f77b4", "o", "UQ (fixed grid)"), "PACK": ("#ff7f0e", "s", "Packing"),
         "BITROUND": ("#2ca02c", "^", "Bit rounding"), "LORENZO": ("#9467bd", "D", "SZ-type Lorenzo"),
         "ZFP": ("#7f7f7f", "v", "ZFP"), "NIPRED": ("#d62728", "x", "Non-integer predictor")}
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.4))
lo, hi = 1e3, 5e6
ax[0].fill_between([lo, hi], [0.85 * lo, 0.85 * hi], [1.15 * lo, 1.15 * hi], color="0.9", lw=0)
ax[0].plot([lo, hi], [lo, hi], color="0.4", lw=0.8)
for k, (col, m, lab) in style.items():
    s = [c for c in cells if c["codec"] == k and c["F_meas"] >= 30]
    ax[0].scatter([c["F_pred"] for c in s], [c["F_meas"] for c in s], s=14, marker=m, color=col, label=lab,
                  facecolors="none" if m in "osD^v" else None, linewidths=0.9)
ax[0].set(xscale="log", yscale="log", xlim=(lo, hi), ylim=(lo, hi), xlabel="Predicted changed decisions $F$",
          ylabel="Measured changed decisions $F$")
ax[0].legend(fontsize=6.5, frameon=False, loc="upper left"); ax[0].set_title("(a)", fontsize=9, loc="left")
for k, (col, m, lab) in style.items():
    s = sorted([c for c in cells if c["codec"] == k and c["tau"] == 35.0], key=lambda c: c["maxerr"])
    ax[1].plot([c["maxerr"] for c in s], [100 * c["dC_meas"] / c["exceed"] for c in s], marker=m, ms=4, lw=0.9,
               color=col, mfc="none" if m in "osD^v" else col, label=lab)
ax[1].axhline(0, color="0.4", lw=0.6); ax[1].set_xscale("log")
ax[1].set(xlabel="Maximum absolute error ($^\\circ$C)", ylabel="Change in days above 35 $^\\circ$C (%)")
ax[1].set_title("(b)", fontsize=9, loc="left")
for x in ax: x.tick_params(labelsize=7); x.xaxis.label.set_size(8); x.yaxis.label.set_size(8)
fig.tight_layout(); fig.savefig("p34_fig1.pdf"); fig.savefig("p34_fig1.png", dpi=200)
print(len(cells), sum(c["F_meas"] >= 30 for c in cells))
