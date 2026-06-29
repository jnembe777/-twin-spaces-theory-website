#!/usr/bin/env python
"""
HMM forward log-likelihood benchmark: linear domain vs log domain.

The forward recursion alpha_t(j) = [sum_i alpha_{t-1}(i) a_ij] b_j(o_t) is the
canonical place where products of probabilities underflow. We compare:

  * direct (linear domain, float64) -- underflows to 0, log-likelihood -> -inf;
  * log domain (log-sum-exp / the twin (+)_exp reduction) -- stable;
  * mpmath high-precision reference.

We report the relative error of the log-likelihood and the wall-clock time, as
the sequence length T grows. Produces a table and figure papers/figures/B6_hmm.
"""

import os
import time
import math

import numpy as np
import mpmath
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
NAVY, TEAL, ROSE = "#1b2a38", "#0096aa", "#b45050"


def random_hmm(n_states, n_sym, rng):
    A = rng.random((n_states, n_states)); A /= A.sum(1, keepdims=True)
    B = rng.random((n_states, n_sym));    B /= B.sum(1, keepdims=True)
    pi = rng.random(n_states); pi /= pi.sum()
    return A, B, pi


def sample_obs(A, B, pi, T, rng):
    n = len(pi)
    s = rng.choice(n, p=pi)
    obs = []
    for _ in range(T):
        obs.append(rng.choice(B.shape[1], p=B[s]))
        s = rng.choice(n, p=A[s])
    return obs


def forward_linear(A, B, pi, obs):
    """Unscaled forward in the linear domain (underflows for large T)."""
    alpha = pi * B[:, obs[0]]
    for o in obs[1:]:
        alpha = (alpha @ A) * B[:, o]
    total = alpha.sum()
    return math.log(total) if total > 0 else float("-inf")


def _lse(v):
    m = np.max(v)
    if not np.isfinite(m):
        return m
    return m + np.log(np.sum(np.exp(v - m)))


def forward_log(A, B, pi, obs):
    """Forward in the log domain (log-sum-exp = the (+)_exp reduction)."""
    logA, logB, logpi = np.log(A), np.log(B), np.log(pi)
    la = logpi + logB[:, obs[0]]
    for o in obs[1:]:
        la = np.array([_lse(la + logA[:, j]) for j in range(len(pi))]) + logB[:, o]
    return _lse(la)


def forward_reference(A, B, pi, obs, dps=80):
    """High-precision reference (mpmath, unscaled but exponent-safe)."""
    mpmath.mp.dps = dps
    n = len(pi)
    Am = [[mpmath.mpf(A[i, j]) for j in range(n)] for i in range(n)]
    Bm = [[mpmath.mpf(B[i, j]) for j in range(B.shape[1])] for i in range(n)]
    alpha = [mpmath.mpf(pi[i]) * Bm[i][obs[0]] for i in range(n)]
    for o in obs[1:]:
        alpha = [sum(alpha[i] * Am[i][j] for i in range(n)) * Bm[j][o]
                 for j in range(n)]
    return float(mpmath.log(mpmath.fsum(alpha)))


def main():
    rng = np.random.default_rng(7)
    A, B, pi = random_hmm(8, 6, rng)
    Ts = [50, 100, 150, 200, 300, 400, 500, 600]
    rows = []
    for T in Ts:
        obs = sample_obs(A, B, pi, T, rng)
        ref = forward_reference(A, B, pi, obs)

        t0 = time.perf_counter(); lin = forward_linear(A, B, pi, obs)
        t_lin = time.perf_counter() - t0
        t0 = time.perf_counter(); lg = forward_log(A, B, pi, obs)
        t_log = time.perf_counter() - t0
        t0 = time.perf_counter(); _ = forward_reference(A, B, pi, obs)
        t_ref = time.perf_counter() - t0

        err_lin = (abs(lin - ref) / abs(ref) if math.isfinite(lin) else float("inf"))
        err_log = abs(lg - ref) / abs(ref)
        rows.append((T, err_lin, err_log, t_lin, t_log, t_ref))
        print(f"T={T:4d}  err_lin={err_lin:.2e}  err_log={err_log:.2e}  "
              f"t_lin={t_lin*1e3:7.2f}ms  t_log={t_log*1e3:7.2f}ms  "
              f"t_ref={t_ref*1e3:8.2f}ms")

    # Figure: error and time vs T.
    Ts_ = [r[0] for r in rows]
    el = [min(r[1], 1e3) if math.isfinite(r[1]) else 1e3 for r in rows]
    eg = [max(r[2], 1e-17) for r in rows]
    tl = [r[3] * 1e3 for r in rows]; tg = [r[4] * 1e3 for r in rows]
    tr = [r[5] * 1e3 for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.4))
    ax[0].semilogy(Ts_, el, color=ROSE, lw=1.8, marker="o", ms=3,
                   label="linear domain")
    ax[0].semilogy(Ts_, eg, color=TEAL, lw=1.8, marker="s", ms=3,
                   label="log domain")
    ax[0].set_xlabel("sequence length $T$"); ax[0].set_ylabel("rel. error of log-likelihood")
    ax[0].set_title("HMM forward: accuracy"); ax[0].legend(); ax[0].grid(alpha=.3)
    ax[1].plot(Ts_, tl, color=ROSE, lw=1.6, marker="o", ms=3, label="linear")
    ax[1].plot(Ts_, tg, color=TEAL, lw=1.6, marker="s", ms=3, label="log domain")
    ax[1].plot(Ts_, tr, color=NAVY, lw=1.6, marker="^", ms=3, label="mpmath ref")
    ax[1].set_xlabel("sequence length $T$"); ax[1].set_ylabel("wall time (ms)")
    ax[1].set_title("HMM forward: cost"); ax[1].legend(); ax[1].grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "B6_hmm.pdf"), bbox_inches="tight")
    print("wrote", os.path.join(FIGDIR, "B6_hmm.pdf"))

    # LaTeX-ready rows.
    print("\n% --- LaTeX table rows ---")
    for T, el_, eg_, tl_, tg_, tr_ in rows:
        elx = "\\infty" if not math.isfinite(el_) else f"{el_:.1e}"
        print(f"{T} & ${elx}$ & ${eg_:.1e}$ & {tl_*1e3:.2f} & {tg_*1e3:.2f} & {tr_*1e3:.1f} \\\\")


if __name__ == "__main__":
    main()
