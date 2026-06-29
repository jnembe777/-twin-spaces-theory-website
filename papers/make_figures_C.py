#!/usr/bin/env python
"""
Figures for Article C (invariants, non-invariants, new formulas).

All produced from the analytic and multiplicative layers; no synthetic data.
"""

import os
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arithmetics.symbolic.twin import (
    discover_homomorphism_types, power_mean, markov_bound, empirical_tail,
    corrected_twisted_primes, euler_defect,
)
from arithmetics.core.transfer import AffineTransfer
from arithmetics.zeta.euler_product import twisted_primes

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIGDIR, exist_ok=True)
plt.rcParams.update({"font.size": 11, "figure.dpi": 120,
                     "axes.grid": True, "grid.alpha": 0.3})
NAVY, TEAL, ROSE, GOLD, GRAY = "#1b2a38", "#0096aa", "#b45050", "#b48c28", "#888888"
TYPE_COLOR = {"+->+": NAVY, "+->*": TEAL, "*->+": ROSE, "*->*": GOLD,
              "generic": GRAY}
TYPE_LABEL = {"+->+": "+→+ (linear)", "+->*": "+→× (exp: concentration)",
              "*->+": "×→+ (log: entropy)", "*->*": "×→× (primes)",
              "generic": "generic (new)"}


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)
    print("wrote", name + ".pdf")


def figC1_frames():
    """The bijection catalogue classified by homomorphism frame."""
    rows = discover_homomorphism_types()
    names = [r["phi"] for r in rows]
    dist = [r["metric_distortion"] for r in rows]
    prim = [r["types"][0] for r in rows]            # primary frame
    colors = [TYPE_COLOR[t] for t in prim]
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    x = np.arange(len(names))
    ax.bar(x, dist, color=colors)
    for i, r in enumerate(rows):
        ax.text(i, dist[i] + 0.05, "+".join(r["types"]), ha="center",
                rotation=90, fontsize=7, va="bottom")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right")
    ax.set_ylabel("metric distortion (non-invariant)")
    ax.set_ylim(0, max(dist) * 1.5)
    ax.set_title("The four productive frames (+ generic)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c)
               for c in [NAVY, TEAL, ROSE, GOLD, GRAY]]
    ax.legend(handles, [TYPE_LABEL[t] for t in ["+->+", "+->*", "*->+", "*->*", "generic"]],
              fontsize=7, ncol=2, loc="upper left")
    save(fig, "C1_frames")


def figC2_power_means():
    """Power-mean curve M_p (quasi-arithmetic means) and the AM-GM-HM points."""
    xs = [1.0, 2.0, 4.0, 8.0]
    ps = np.linspace(-6, 6, 121)
    Ms = [power_mean(float(p), xs) for p in ps]
    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    ax.plot(ps, Ms, color=NAVY, lw=2)
    pts = {"HM ($p{=}{-}1$)": -1, "GM ($p{=}0$)": 0, "AM ($p{=}1$)": 1}
    for lab, p in pts.items():
        m = power_mean(float(p), xs)
        ax.plot(p, m, "o", color=ROSE)
        ax.annotate(lab, (p, m), textcoords="offset points", xytext=(6, -2),
                    fontsize=9)
    ax.axhline(max(xs), color=GRAY, ls=":", lw=1)
    ax.axhline(min(xs), color=GRAY, ls=":", lw=1)
    ax.set_xlabel("order $p$"); ax.set_ylabel("$M_p(x)$")
    ax.set_title("Quasi-arithmetic means: $M_p$ is non-decreasing in $p$")
    save(fig, "C2_power_means")


def figC3_concentration():
    """Tail-adaptive phi-concentration: which generator gives the tightest bound."""
    rng = np.random.default_rng(0)
    data = {"Gaussian (light tail)": rng.normal(0, 1, 200000),
            "Pareto (heavy tail)": rng.pareto(2.5, 200000) + 1.0}
    family = {f"x^{k}": (lambda x, k=k: np.abs(x) ** k) for k in (1, 2, 4, 6)}
    family.update({f"e^{t}x": (lambda x, t=t: np.exp(t * x)) for t in (0.5, 1.0, 2.0)})
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4))
    for ax, (name, X) in zip(axes, data.items()):
        a = float(np.quantile(X, 0.99))
        bounds = {k: markov_bound(X, a, phi) for k, phi in family.items()}
        names = list(bounds); vals = [bounds[n] for n in names]
        best = int(np.argmin(vals))
        colors = [TEAL if n.startswith("e") else GOLD for n in names]
        colors[best] = ROSE
        ax.bar(range(len(names)), vals, color=colors)
        ax.set_yscale("log")
        ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=45,
                                                             ha="right", fontsize=8)
        ax.axhline(empirical_tail(X, a), color=NAVY, ls="--", lw=1,
                   label="true $P(X{\\geq}a)$")
        ax.set_title(name); ax.legend(fontsize=8)
    axes[0].set_ylabel("tail bound (lower = tighter)")
    fig.suptitle("phi-concentration: the optimal generator is tail-adaptive",
                 y=1.02)
    save(fig, "C3_concentration")


def figC4_multiplicative():
    """The multiplicative pillar: prime sparsity and the Euler-product defect."""
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.4))
    # (a) corrected (2,1) primes are sparse (prime-like) vs the repo's dense set
    Ns = list(range(10, 121, 10))
    corr = [len(corrected_twisted_primes(2, 1, N)) for N in Ns]
    repo = [len(twisted_primes(AffineTransfer(2, 1), N)) for N in Ns]
    axes[0].plot(Ns, repo, color=ROSE, lw=1.8, marker="o", ms=3,
                 label="repo (unit = 1)")
    axes[0].plot(Ns, corr, color=TEAL, lw=1.8, marker="s", ms=3,
                 label="corrected (unit $=\\varphi^{-1}(1)$)")
    axes[0].set_xlabel("$N$"); axes[0].set_ylabel("# twisted primes $\\leq N$")
    axes[0].set_title("Affine(2,1): the unit correction"); axes[0].legend(fontsize=8)
    # (b) Euler-product defect vs limit: 0 iff unique factorization
    lims = list(range(50, 451, 50))
    for (c, d), col, mk in [((2, 1), TEAL, "s"), ((3, 1), ROSE, "o"),
                            ((4, 1), GOLD, "^")]:
        ys = [abs(euler_defect(c, d, 2.0, L)) for L in lims]
        axes[1].plot(lims, ys, color=col, lw=1.6, marker=mk, ms=3,
                     label=f"({c},{d})")
    axes[1].set_yscale("symlog", linthresh=1e-7)
    axes[1].set_xlabel("truncation limit")
    axes[1].set_ylabel(r"$|\sum (r(m){-}1) m^{-2}|$")
    axes[1].set_title("Euler-product defect (0 $\\Leftrightarrow$ UFD)")
    axes[1].legend(fontsize=8)
    save(fig, "C4_multiplicative")


def figC5_dirichlet():
    """Twisted-prime density (PNT in progression) and the L-function identity."""
    import mpmath
    from arithmetics.zeta.euler_product import sieve_primes
    from arithmetics.symbolic.twin import progression_zeta, progression_zeta_closed
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.4))
    # (a) density: pi_phi(N) = pi(2N+1) - 1, vs Li(2N+1)-1 and leading 2N/log 2N
    Ns = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
    primes = set(sieve_primes(200001))
    pi_phi = [sum(1 for n in range(1, N + 1) if (2 * n + 1) in primes) for N in Ns]
    li_est = [float(mpmath.li(2 * N + 1)) - 1 for N in Ns]
    lead = [2 * N / math.log(2 * N) for N in Ns]
    axes[0].plot(Ns, pi_phi, color=TEAL, lw=1.8, marker="s", ms=4,
                 label=r"$\pi_\varphi(N)=\pi(2N{+}1){-}1$")
    axes[0].plot(Ns, li_est, color=NAVY, lw=1.4, ls="--",
                 label=r"$\mathrm{Li}(2N{+}1){-}1$")
    axes[0].plot(Ns, lead, color=GRAY, lw=1.2, ls=":",
                 label=r"$2N/\log 2N$")
    axes[0].set_xscale("log"); axes[0].set_yscale("log")
    axes[0].set_xlabel("$N$"); axes[0].set_ylabel("count")
    axes[0].set_title("Twisted primes: PNT in progression")
    axes[0].legend(fontsize=8)
    # (b) twisted zeta partial sum -> closed Hurwitz form
    Ls = [10, 30, 100, 300, 1000, 3000, 10000, 30000]
    for (c, d), col, mk in [((2, 1), TEAL, "s"), ((3, 1), ROSE, "o")]:
        closed = float(progression_zeta_closed(c, d, 2.0))
        ys = [abs(complex(progression_zeta(c, d, 2.0, L)).real + 1 - closed)
              for L in Ls]
        axes[1].loglog(Ls, ys, color=col, lw=1.6, marker=mk, ms=3,
                       label=f"({c},{d})")
    axes[1].set_xlabel("truncation"); axes[1].set_ylabel("error vs closed form")
    axes[1].set_title(r"Twisted zeta $\to$ Hurwitz/$L$ form")
    axes[1].legend(fontsize=8)
    save(fig, "C5_dirichlet")


def main():
    figC1_frames()
    figC2_power_means()
    figC3_concentration()
    figC4_multiplicative()
    figC5_dirichlet()
    print("Article C figures done.")


if __name__ == "__main__":
    main()
