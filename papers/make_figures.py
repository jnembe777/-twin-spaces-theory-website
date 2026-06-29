#!/usr/bin/env python
"""
Generate all figures for the two twin-spaces preprints from computed data.

Every figure is produced from the actual modules in arithmetics.symbolic.twin
(no synthetic data). Outputs vector PDFs into papers/figures/.
"""

import os
import math

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arithmetics.symbolic.twin import (
    PermutationAction, candidate_base_operations, twin_decision,
    FiniteGroup, class_equation,
    sample_unitary, eigenphases, weyl_average, character_inner_product,
    TransformedTotal, Bijection, total_error, op_count,
    linearization_rmse, LinearAction, Operation, kernel_profile,
    qudit_universality,
)

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIGDIR, exist_ok=True)
plt.rcParams.update({"font.size": 11, "figure.dpi": 120,
                     "axes.grid": True, "grid.alpha": 0.3})
NAVY, TEAL, ROSE, GOLD = "#1b2a38", "#0096aa", "#b45050", "#b48c28"


def save(fig, name):
    path = os.path.join(FIGDIR, name)
    fig.tight_layout()
    fig.savefig(path + ".pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path + ".pdf")


# ===========================================================================
# Article A — scientific
# ===========================================================================
def figA1_reduction():
    """Operations vs decision cells across finite (group, base) pairs."""
    cases = [("C_4", PermutationAction.cyclic(4), 4),
             ("D_4", PermutationAction.dihedral(4), 4),
             ("S_4", PermutationAction.symmetric(4), 4),
             ("C_6", PermutationAction.cyclic(6), 6),
             ("D_3", PermutationAction.dihedral(3), 3),
             ("S_3", PermutationAction.symmetric(3), 3)]
    labels, ops, cells = [], [], []
    for name, G, m in cases:
        base = candidate_base_operations(m)[0]      # + mod m
        r = twin_decision(base, G)
        labels.append(f"{name}\n+mod{m}")
        ops.append(r["num_operations"])
        cells.append(r["num_decision_cells"])
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.bar(x - 0.2, ops, 0.4, label="twin operations |Op|", color=TEAL)
    ax.bar(x + 0.2, cells, 0.4, label="decision cells", color=NAVY)
    for i, (o, c) in enumerate(zip(ops, cells)):
        ax.text(i - 0.2, o + 0.2, str(o), ha="center", fontsize=9)
        ax.text(i + 0.2, c + 0.2, str(c), ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("count")
    ax.set_title("Reduction of the decision space (normalizer orbits)")
    ax.legend()
    save(fig, "A1_reduction")


def figA2_class_spectrum():
    """Class-equation 'symmetry spectrum': conjugacy-class sizes per group."""
    groups = [("S_3", FiniteGroup.from_permutation_action(PermutationAction.symmetric(3))),
              ("D_4", FiniteGroup.dihedral(4)),
              ("Q_8", FiniteGroup.quaternion8()),
              ("S_4", FiniteGroup.from_permutation_action(PermutationAction.symmetric(4)))]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for y, (name, G) in enumerate(groups):
        sizes = sorted(len(c) for c in G.conjugacy_classes())
        left = 0
        for s in sizes:
            color = GOLD if s == 1 else TEAL
            ax.barh(y, s, left=left, height=0.6, color=color,
                    edgecolor="white")
            if s >= 2:
                ax.text(left + s / 2, y, str(s), ha="center", va="center",
                        color="white", fontsize=9)
            left += s
        ax.text(left + 0.3, y, f"|G|={G.order}", va="center", fontsize=9)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([n for n, _ in groups])
    ax.set_xlabel("class sizes  (gold = centre, |Z|)")
    ax.set_title("Class equation as a symmetry spectrum")
    ax.grid(False)
    save(fig, "A2_class_spectrum")


def figA3_weyl():
    """SU(2) class-angle density and CUE moment convergence."""
    rng = np.random.default_rng(0)
    # panel a: SU(2) class angle vs (2/pi) sin^2 theta
    angles = []
    for _ in range(40000):
        U = sample_unitary(2, rng, special=True)
        th = np.abs(eigenphases(U))
        angles.append(max(th))            # class angle in [0, pi]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4))
    axes[0].hist(angles, bins=60, density=True, color=TEAL, alpha=0.6,
                 label="sampled")
    t = np.linspace(0, math.pi, 200)
    axes[0].plot(t, (2 / math.pi) * np.sin(t) ** 2, color=NAVY, lw=2,
                 label=r"$(2/\pi)\sin^2\theta$")
    axes[0].set_xlabel(r"class angle $\theta$"); axes[0].set_ylabel("density")
    axes[0].set_title("SU(2) Weyl measure"); axes[0].legend()
    # panel b: running estimate of E|tr U|^2 -> 1
    for n, col in [(2, TEAL), (3, NAVY), (4, ROSE)]:
        rng2 = np.random.default_rng(n)
        run, s = [], 0.0
        for k in range(1, 6001):
            U = sample_unitary(n, rng2)
            s += abs(np.trace(U)) ** 2
            if k % 50 == 0:
                run.append((k, s / k))
        ks, vs = zip(*run)
        axes[1].plot(ks, vs, color=col, lw=1.3, label=f"U({n})")
    axes[1].axhline(1.0, color="gray", ls="--", lw=1)
    axes[1].set_xlabel("Haar samples"); axes[1].set_ylabel(r"$\mathbb{E}|\mathrm{tr}\,U|^2$")
    axes[1].set_title("CUE moment convergence"); axes[1].legend()
    save(fig, "A3_weyl")


def figA4_orthonormality():
    """Gram matrix of Schur characters over U(3): approx identity."""
    parts = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 0, 0), (2, 1, 0)]
    names = ["triv", "fund", r"$\Lambda^2$", r"Sym$^2$", "(2,1)"]
    n = len(parts)
    G = np.zeros((n, n))
    for i, lam in enumerate(parts):
        for j, mu in enumerate(parts):
            G[i, j] = character_inner_product(lam, mu, 3, samples=30000,
                                              seed=100 + i * 7 + j).real
    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    im = ax.imshow(G, cmap="cividis", vmin=0, vmax=1)
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{G[i, j]:.2f}", ha="center", va="center",
                    color="white" if G[i, j] < 0.6 else "black", fontsize=8)
    ax.set_xticks(range(n)); ax.set_xticklabels(names)
    ax.set_yticks(range(n)); ax.set_yticklabels(names)
    ax.set_title(r"$\langle\chi_\lambda,\chi_\mu\rangle$ on $U(3)$")
    fig.colorbar(im, fraction=0.046, pad=0.04)
    ax.grid(False)
    save(fig, "A4_orthonormality")


# ===========================================================================
# Article B — technological
# ===========================================================================
def figB1_logdomain():
    """Log-likelihood: original-domain underflow vs transformed-domain stability."""
    task = TransformedTotal(Bijection.logarithm())
    rng = np.random.default_rng(0)
    Ns = list(range(10, 2001, 40))
    err_o, err_t = [], []
    for N in Ns:
        xs = [10 ** rng.uniform(-3, -1) for _ in range(N)]
        eo = total_error(task, xs, "original")
        et = total_error(task, xs, "transformed")
        err_o.append(min(eo, 1e6) if math.isfinite(eo) else 1e6)
        err_t.append(max(et, 1e-17))
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.semilogy(Ns, err_o, color=ROSE, lw=1.8, label="original domain ($\\prod$ then $\\log$)")
    ax.semilogy(Ns, err_t, color=TEAL, lw=1.8, label=r"transformed domain ($\sum\log$)")
    ax.axhline(1.0, color="gray", ls=":", lw=1)
    ax.set_xlabel("number of factors $N$"); ax.set_ylabel("relative error of log-likelihood")
    ax.set_title("Log-domain stability (underflow of the product)")
    ax.legend()
    save(fig, "B1_logdomain")


def figB2_optimal_base():
    """Linearization RMSE per base for power/exponential/linear data."""
    xs = [float(i) for i in range(1, 21)]
    datasets = {
        "power $3x^2$": [3.0 * x ** 2 for x in xs],
        "exp $2e^{0.3x}$": [2.0 * math.exp(0.3 * x) for x in xs],
        "linear $2x{+}1$": [2.0 * x + 1.0 for x in xs],
    }
    bases = ["linear", "loglog", "semilogy", "semilogx"]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    width = 0.2
    xpos = np.arange(len(datasets))
    colors = [NAVY, TEAL, ROSE, GOLD]
    for bi, base in enumerate(bases):
        vals = [max(linearization_rmse(base, xs, ys), 1e-16)
                for ys in datasets.values()]
        ax.bar(xpos + (bi - 1.5) * width, vals, width, label=base,
               color=colors[bi])
    ax.set_yscale("log")
    ax.set_xticks(xpos); ax.set_xticklabels(list(datasets.keys()))
    ax.set_ylabel("back-transformed RMSE")
    ax.set_title("Optimal base selection (lower = better)")
    ax.legend(ncol=4, fontsize=9)
    save(fig, "B2_optimal_base")


def figB3_tradeoff():
    """Speed/stability trade-off: transcendental op counts vs N."""
    Ns = np.arange(2, 1001)
    naive = [op_count(int(n))["naive_fold"]["transcendental"] for n in Ns]
    trans = [op_count(int(n))["transformed_domain"]["transcendental"] for n in Ns]
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.plot(Ns, naive, color=ROSE, lw=1.8, label="naive twin-fold  $3(N{-}1)$")
    ax.plot(Ns, trans, color=TEAL, lw=1.8, label="transformed domain  $N{+}1$")
    ax.set_xlabel("number of elements $N$")
    ax.set_ylabel("transcendental calls")
    ax.set_title("Speed/stability trade-off of the domain choice")
    ax.legend()
    save(fig, "B3_tradeoff")


def figB5_lse():
    """Softmax / log-sum-exp: naive overflow vs the stable (max-shift) domain."""
    import mpmath
    rng = np.random.default_rng(0)
    z0 = rng.standard_normal(200)
    scales = np.linspace(1, 800, 40)
    err_naive, err_stable = [], []
    for s in scales:
        z = s + z0
        with mpmath.workdps(60):
            ref = float(mpmath.log(mpmath.fsum(mpmath.e ** mpmath.mpf(zi) for zi in z)))
        try:
            naive = math.log(sum(math.exp(zi) for zi in z))
        except OverflowError:
            naive = float("inf")
        m = float(np.max(z))
        stable = m + math.log(sum(math.exp(zi - m) for zi in z))
        err_naive.append(min(abs(naive - ref) / abs(ref), 1e6)
                         if math.isfinite(naive) else 1e6)
        err_stable.append(max(abs(stable - ref) / abs(ref), 1e-17))
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.semilogy(scales, err_naive, color=ROSE, lw=1.8,
                label=r"naive $\log\sum e^{z_i}$")
    ax.semilogy(scales, err_stable, color=TEAL, lw=1.8,
                label=r"stable domain (max-shift $\oplus_{\exp}$)")
    ax.set_xlabel(r"magnitude of $z_i$")
    ax.set_ylabel("relative error of log-sum-exp")
    ax.set_title(r"Softmax stability: the $\oplus_{\exp}$ reduction")
    ax.legend()
    save(fig, "B5_lse")


def figB4_universality():
    """Qudit universality: rigid addition vs trivial-kernel generic gate."""
    ds = [2, 3, 4, 5, 6]
    rigid, generic = [], []
    for d in ds:
        act = LinearAction.SUn(d)
        radd = kernel_profile(Operation.addition(d, "C"), act,
                              n_samples=120, seed=0)["fraction"]
        rgen = qudit_universality(d, samples=120, seed=1)["fraction"]
        rigid.append(radd); generic.append(rgen)
    x = np.arange(len(ds))
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.bar(x - 0.2, rigid, 0.4, color=GOLD, label="addition (rigid, $L=G$)")
    ax.bar(x + 0.2, generic, 0.4, color=TEAL, label="generic gate (trivial $L$)")
    ax.set_xticks(x); ax.set_xticklabels([f"SU({d})" for d in ds])
    ax.set_ylabel("fraction of $G$ preserving $\\odot$")
    ax.set_title(r"Qudit universality: $\mathrm{Op}\cong SU(d)$ for generic gates")
    ax.set_ylim(0, 1.15); ax.legend()
    save(fig, "B4_universality")


def main():
    figA1_reduction()
    figA2_class_spectrum()
    figA3_weyl()
    figA4_orthonormality()
    figB1_logdomain()
    figB2_optimal_base()
    figB3_tradeoff()
    figB5_lse()
    figB4_universality()
    print("all figures written to", FIGDIR)


if __name__ == "__main__":
    main()
