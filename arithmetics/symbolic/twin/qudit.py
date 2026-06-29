"""
Weyl integration for qudits: the class equation on ``SU(n)`` / ``U(n)``.

This is the qudit ($d$-level) generalisation of the ``SU(2)`` instance: for a
compact connected Lie group the class equation becomes the **Weyl integration
formula**, reducing the average of a class function to the maximal torus,
weighted by the Weyl denominator. For ``U(n)`` the eigen-phase joint density is

.. math::

    d\\mu(\\theta_1,\\dots,\\theta_n)
      = \\frac{1}{n!\\,(2\\pi)^n}\\ \\prod_{j<k}\\bigl|e^{i\\theta_j}-e^{i\\theta_k}\\bigr|^2
        \\ d\\theta_1\\cdots d\\theta_n ,

the squared Vandermonde (the CUE eigenvalue density). A *class cost* on a qudit
gate under conjugation by ``SU(d)`` is a symmetric function of the eigen-phases,
decided against this measure.

The correctness anchor is **character orthonormality**: the irreducible
characters of ``U(n)`` are the Schur polynomials ``s_λ`` of the eigenvalues, and
``⟨χ_λ, χ_μ⟩ = δ_{λμ}`` under the Weyl measure -- a checkable fact that pins the
measure down.

Provides:

* :func:`sample_unitary`, :func:`eigenphases` -- Haar sampling and spectra;
* :func:`weyl_density` -- the closed-form eigen-phase density;
* :func:`weyl_average` -- the Weyl integral of a class function (Haar
  Monte-Carlo, exact in expectation);
* :func:`schur_character`, :func:`character_inner_product`,
  :func:`verify_character_orthonormality` -- the verification;
* :func:`qudit_class_decision` -- decide a class cost over the torus;
* :func:`qudit_universality` -- a generic qudit gate has trivial kernel, so
  ``Op ≅ SU(d)`` (universality persists for qudits).
"""

import math
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "sample_unitary", "eigenphases", "weyl_density", "weyl_average",
    "schur_character", "character_inner_product",
    "verify_character_orthonormality", "qudit_class_decision",
    "qudit_universality",
]


# ---------------------------------------------------------------------------
# Haar sampling and spectra
# ---------------------------------------------------------------------------
def sample_unitary(n: int, rng, special: bool = False) -> np.ndarray:
    """Haar-random ``U(n)`` (Mezzadri QR); ``special=True`` projects to ``SU(n)``."""
    z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2.0)
    q, r = np.linalg.qr(z)
    ph = np.diagonal(r) / np.abs(np.diagonal(r))
    u = q * ph
    if special:
        u = u / np.linalg.det(u) ** (1.0 / n)
    return u


def eigenphases(U: np.ndarray) -> np.ndarray:
    """Eigen-phases ``θ_j ∈ (-π, π]`` of a unitary matrix."""
    return np.angle(np.linalg.eigvals(U))


# ---------------------------------------------------------------------------
# The Weyl (eigen-phase) measure
# ---------------------------------------------------------------------------
def weyl_density(thetas: Sequence[float]) -> float:
    r"""Closed-form ``U(n)`` eigen-phase density (squared Vandermonde).

    ``ρ(θ) = (1 / (n!\,(2π)^n)) ∏_{j<k} |e^{iθ_j} - e^{iθ_k}|²``.
    """
    th = np.asarray(thetas, dtype=float)
    n = len(th)
    z = np.exp(1j * th)
    prod = 1.0
    for j in range(n):
        for k in range(j + 1, n):
            prod *= abs(z[j] - z[k]) ** 2
    return prod / (math.factorial(n) * (2 * math.pi) ** n)


def weyl_average(f: Callable[[np.ndarray], complex], n: int,
                 samples: int = 20000, special: bool = False,
                 seed: int = 0) -> complex:
    """Weyl integral ``∫_G f dμ`` of a class function, by Haar Monte-Carlo.

    ``f`` takes the vector of eigen-phases and returns a (possibly complex)
    value. The Haar average over ``U(n)`` (or ``SU(n)``) equals the Weyl
    integral by definition, and is exact in expectation.
    """
    rng = np.random.default_rng(seed)
    total = 0.0 + 0.0j
    for _ in range(samples):
        U = sample_unitary(n, rng, special=special)
        total += f(eigenphases(U))
    return total / samples


# ---------------------------------------------------------------------------
# Schur characters and orthonormality (the correctness anchor)
# ---------------------------------------------------------------------------
def schur_character(partition: Sequence[int], thetas: Sequence[float]) -> complex:
    """Irreducible ``U(n)`` character ``χ_λ`` = Schur polynomial ``s_λ``.

    Uses the bialternant ``s_λ(z) = det(z_i^{λ_j + n-1-j}) / det(z_i^{n-1-j})``
    evaluated at ``z_j = e^{iθ_j}``.
    """
    th = np.asarray(thetas, dtype=float)
    n = len(th)
    z = np.exp(1j * th)
    lam = list(partition) + [0] * (n - len(partition))
    top = np.array([[z[i] ** (lam[j] + n - 1 - j) for j in range(n)]
                    for i in range(n)], dtype=complex)
    bot = np.array([[z[i] ** (n - 1 - j) for j in range(n)]
                    for i in range(n)], dtype=complex)
    return np.linalg.det(top) / np.linalg.det(bot)


def character_inner_product(lam: Sequence[int], mu: Sequence[int], n: int,
                            samples: int = 20000, special: bool = False,
                            seed: int = 0) -> complex:
    """``⟨χ_λ, χ_μ⟩`` under the Weyl measure (Haar Monte-Carlo)."""
    def f(th):
        return schur_character(lam, th) * np.conj(schur_character(mu, th))
    return weyl_average(f, n, samples=samples, special=special, seed=seed)


def verify_character_orthonormality(n: int, partitions: Sequence[Sequence[int]],
                                    samples: int = 30000, tol: float = 0.05,
                                    seed: int = 0) -> dict:
    """Check ``⟨χ_λ, χ_μ⟩ ≈ δ_{λμ}`` for a set of partitions over ``U(n)``."""
    rng_seed = seed
    gram = {}
    ok = True
    for a, lam in enumerate(partitions):
        for b, mu in enumerate(partitions):
            val = character_inner_product(lam, mu, n, samples=samples,
                                          seed=rng_seed + a * 31 + b)
            expected = 1.0 if a == b else 0.0
            gram[(tuple(lam), tuple(mu))] = complex(val)
            if abs(val - expected) > tol:
                ok = False
    return {"n": n, "gram": gram, "tol": tol, "orthonormal": ok}


# ---------------------------------------------------------------------------
# Qudit class decision
# ---------------------------------------------------------------------------
def qudit_class_decision(f: Callable[[np.ndarray], float], n: int,
                         special: bool = True, samples: int = 20000,
                         opt_samples: int = 4000, minimize: bool = True,
                         seed: int = 0) -> dict:
    """Decide a real class cost ``f(θ)`` over the conjugacy classes of ``SU(n)``.

    Returns the Weyl average of ``f`` and the optimal class (a representative
    eigen-phase configuration) found by sampling the torus.
    """
    avg = float(np.real(weyl_average(lambda th: f(th), n,
                                     samples=samples, special=special, seed=seed)))
    rng = np.random.default_rng(seed + 1)
    best_val, best_theta = None, None
    pick = (lambda a, b: a < b) if minimize else (lambda a, b: a > b)
    for _ in range(opt_samples):
        U = sample_unitary(n, rng, special=special)
        th = eigenphases(U)
        v = f(th)
        if best_val is None or pick(v, best_val):
            best_val, best_theta = v, th
    return {
        "group": f"SU({n})" if special else f"U({n})",
        "weyl_average": avg,
        "optimal_cost": float(best_val),
        "optimal_phases": np.sort(best_theta).tolist(),
    }


# ---------------------------------------------------------------------------
# Universality for qudits
# ---------------------------------------------------------------------------
def qudit_universality(d: int, samples: int = 300, seed: int = 1,
                       tol: float = 1e-9) -> dict:
    """A generic qudit gate under ``SU(d)`` has trivial kernel: ``Op ≅ SU(d)``.

    Extends the ``SU(2)`` universality instance to ``d``-level systems.
    """
    from arithmetics.symbolic.twin.lie import (
        LinearAction, Operation, kernel_profile,
    )
    gate = Operation.random_gate(d, seed=seed, field="C")
    prof = kernel_profile(gate, LinearAction.SUn(d), n_samples=samples,
                          tol=tol, seed=seed)
    prof["Op"] = (f"SU({d})" if prof["kernel_trivial"] else f"SU({d})/L")
    return prof
