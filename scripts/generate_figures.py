from pathlib import Path
import csv
import shutil
import statistics
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

# The repository scientific diagrams are compact, hand-authored SVG masters.
for name in ["claim-evidence-framework.svg", "complexity-landscape.svg", "certificate-anatomy.svg"]:
    shutil.copyfile(ROOT / "docs" / "assets" / name, OUT / name)

def read_csv(name):
    with (ROOT / "results" / "frozen" / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# 1. Exhaustive versus exact tree DP on the deliberately adversarial timing family.
rows = read_csv("worst_case_timing.csv")
ns = sorted({int(r["n"]) for r in rows})
brute = [statistics.median(float(r["bruteforce_s"]) for r in rows if int(r["n"]) == n) * 1000 for n in ns]
dp = [statistics.median(float(r["tree_dp_s"]) for r in rows if int(r["n"]) == n) * 1000 for n in ns]
fig, ax = plt.subplots(figsize=(6.6, 3.6))
ax.plot(ns, brute, marker="o", label="Exhaustive alignment search")
ax.plot(ns, dp, marker="s", label="Tree dynamic program")
ax.set_yscale("log")
ax.set_xlabel("Claim vertices")
ax.set_ylabel("Median runtime (ms, log scale)")
ax.set_title("Reference implementation: exhaustive search versus tree DP")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "runtime-validation.pdf")
plt.close(fig)

# 2. Tree scalability through 5,000 claim vertices.
rows = read_csv("tree_scalability.csv")
fig, ax = plt.subplots(figsize=(6.6, 3.6))
for d in sorted({int(r["d"]) for r in rows}):
    sizes = sorted({int(r["n"]) for r in rows if int(r["d"]) == d})
    med = [statistics.median(float(r["tree_dp_s"]) for r in rows if int(r["d"]) == d and int(r["n"]) == n) * 1000 for n in sizes]
    ax.plot(sizes, med, marker="o", label=f"|D|={d}")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Claim vertices (log scale)")
ax.set_ylabel("Median tree-DP runtime (ms, log scale)")
ax.set_title("Seeded tree-algorithm scaling experiment")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "tree-scalability.pdf")
plt.close(fig)

# 3. Greedy evidence-cover ratio against exact bitmask optimum.
rows = read_csv("cover_results.csv")
ms = sorted({int(r["m"]) for r in rows})
means = [statistics.mean(float(r["ratio"]) for r in rows if int(r["m"]) == m) for m in ms]
maxima = [max(float(r["ratio"]) for r in rows if int(r["m"]) == m) for m in ms]
fig, ax = plt.subplots(figsize=(6.6, 3.6))
ax.plot(ms, means, marker="o", label="Mean greedy / optimum")
ax.plot(ms, maxima, marker="s", label="Maximum observed ratio")
ax.axhline(1.0, linewidth=1, linestyle="--")
ax.set_xlabel("Claims in source-cover universe m")
ax.set_ylabel("Cost ratio")
ax.set_title("Finite-instance evidence-cover validation")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "evidence-cover-ratio.pdf")
plt.close(fig)

print("PASS: reviewer-facing scientific figures regenerated")
