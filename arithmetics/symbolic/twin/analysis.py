"""
Analytic tools for twin operations: quasi-arithmetic means, phi-concentration
bounds, and the invariant / non-invariant boundary.

The single-operation twin construction is, up to isomorphism, a relabeling.
This module implements the tools that turn that relabeling into genuine
mathematics, by crossing the invariant algebra with *non-invariant* analytic
structure (metric, measure, order, a second operation):

* **quasi-arithmetic (Kolmogorov--Nagumo) means** -- the twin average
  ``M_phi(x) = phi^{-1}(mean phi(x_i))``; the power-mean family and the
  power-mean inequality live here;
* **phi-concentration bounds** -- the generalized Markov bound
  ``P(X >= a) <= E[phi(X)] / phi(a)`` and its Chernoff specialization, with
  *base selection* over a family of ``phi`` (the Article-B decision, applied to
  probability); the MGF factorization of independent sums is the twin identity;
* **the invariance report** -- which structures a bijection ``phi`` preserves
  (order, additivity, the additive-to-multiplicative homomorphism, the metric,
  convexity), operationalizing the boundary theorem ``invariant <=> preserved
  signature``;
* a bridge to **twisted primes** -- the irreducibles of the twin product, a
  non-invariant that genuinely changes the arithmetic.
"""

import math
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

__all__ = [
    "quasi_arithmetic_mean", "power_mean", "geometric_mean", "harmonic_mean",
    "power_mean_curve", "verify_power_mean_inequality",
    "mgf", "empirical_tail", "markov_bound", "polynomial_markov_bound",
    "chernoff_bound", "best_phi_bound", "mgf_factorizes",
    "additive_defect", "homomorphism_add_mul_defect", "invariance_report",
    "homomorphism_signature", "affine_twisted_prime", "affine_twisted_primes",
    "verify_affine_prime_formula",
    "discover_homomorphism_types", "discover_twin_primes",
    "twin_prime_spectrum",
]


# ---------------------------------------------------------------------------
# Quasi-arithmetic (Kolmogorov--Nagumo) means
# ---------------------------------------------------------------------------
def quasi_arithmetic_mean(phi: Callable, phi_inv: Callable,
                          xs: Sequence[float],
                          weights: Optional[Sequence[float]] = None) -> float:
    """The twin average ``M_phi(x) = phi^{-1}(sum w_i phi(x_i))``.

    With ``phi = id`` this is the arithmetic mean; ``phi = log`` the geometric
    mean; ``phi = x**p`` the power mean of order ``p``.
    """
    xs = np.asarray(xs, dtype=float)
    w = (np.ones_like(xs) if weights is None else np.asarray(weights, dtype=float))
    w = w / w.sum()
    return float(phi_inv(np.sum(w * np.array([phi(x) for x in xs]))))


def power_mean(p: float, xs: Sequence[float],
               weights: Optional[Sequence[float]] = None) -> float:
    """Power mean of order ``p`` (``p = 0`` gives the geometric mean)."""
    xs = np.asarray(xs, dtype=float)
    w = (np.ones_like(xs) if weights is None else np.asarray(weights, dtype=float))
    w = w / w.sum()
    if p == 0:
        return float(np.exp(np.sum(w * np.log(xs))))
    return float(np.sum(w * xs ** p) ** (1.0 / p))


def geometric_mean(xs, weights=None) -> float:
    return power_mean(0.0, xs, weights)


def harmonic_mean(xs, weights=None) -> float:
    return power_mean(-1.0, xs, weights)


def power_mean_curve(xs: Sequence[float],
                     ps: Sequence[float]) -> List[tuple]:
    """Return ``[(p, M_p)]`` for the given orders ``ps`` (sorted by ``p``)."""
    return [(p, power_mean(p, xs)) for p in sorted(ps)]


def verify_power_mean_inequality(xs: Sequence[float],
                                 ps: Sequence[float],
                                 tol: float = 1e-12) -> bool:
    """Check the power-mean inequality ``M_p <= M_q`` for ``p <= q``."""
    curve = power_mean_curve(xs, ps)
    return all(curve[i][1] <= curve[i + 1][1] + tol
               for i in range(len(curve) - 1))


# ---------------------------------------------------------------------------
# phi-concentration bounds
# ---------------------------------------------------------------------------
def mgf(samples: Sequence[float], t: float) -> float:
    """Empirical moment generating function ``E[e^{tX}]``."""
    return float(np.mean(np.exp(t * np.asarray(samples, dtype=float))))


def empirical_tail(samples: Sequence[float], a: float) -> float:
    """Empirical tail probability ``P(X >= a)``."""
    return float(np.mean(np.asarray(samples, dtype=float) >= a))


def markov_bound(samples: Sequence[float], a: float, phi: Callable) -> float:
    """Generalized Markov bound ``E[phi(X)] / phi(a)`` for increasing ``phi >= 0``.

    Valid whenever ``phi`` is non-decreasing and non-negative on the support.
    """
    x = np.asarray(samples, dtype=float)
    num = float(np.mean(phi(x)))
    den = phi(a)
    return num / den if den > 0 else float("inf")


def polynomial_markov_bound(samples: Sequence[float], a: float,
                            k: float) -> float:
    """Order-``k`` Markov bound ``E[X^k] / a^k`` (for ``X >= 0``, ``a > 0``)."""
    return markov_bound(samples, a, lambda x: np.abs(x) ** k)


def chernoff_bound(samples: Sequence[float], a: float,
                   ts: Optional[Sequence[float]] = None) -> dict:
    """Chernoff bound ``inf_{t>0} e^{-ta} E[e^{tX}]`` (optimized over ``t``)."""
    ts = ts if ts is not None else np.linspace(0.01, 5.0, 200)
    best_t, best = None, float("inf")
    for t in ts:
        val = math.exp(-t * a) * mgf(samples, t)
        if val < best:
            best, best_t = val, float(t)
    return {"bound": best, "t": best_t}


def best_phi_bound(samples: Sequence[float], a: float,
                   family: Optional[Dict[str, Callable]] = None) -> dict:
    """Select the tightest valid ``phi``-bound over a family (base selection).

    The family mixes polynomial generators ``x^k`` (good for heavy tails) and
    exponential generators ``e^{tx}`` (good for light tails); the optimum is
    tail-adaptive.
    """
    if family is None:
        family = {f"x^{k}": (lambda x, k=k: np.abs(x) ** k) for k in (1, 2, 4, 6)}
        family.update({f"e^{t}x": (lambda x, t=t: np.exp(t * x))
                       for t in (0.5, 1.0, 2.0)})
    results = {name: markov_bound(samples, a, phi) for name, phi in family.items()}
    best_name = min(results, key=results.get)
    return {"best": best_name, "bound": results[best_name], "all": results}


def mgf_factorizes(samples_x: Sequence[float], samples_y: Sequence[float],
                   t: float, tol: float = 0.05) -> dict:
    """Test the twin identity ``MGF_{X+Y}(t) = MGF_X(t) MGF_Y(t)`` (independent).

    The MGF turns the sum of independent variables into a product -- the
    additive-to-multiplicative twin identity that powers Chernoff bounds.
    """
    x = np.asarray(samples_x, dtype=float)
    y = np.asarray(samples_y, dtype=float)
    n = min(len(x), len(y))
    lhs = float(np.mean(np.exp(t * (x[:n] + y[:n]))))  # independent pairing
    rhs = mgf(x, t) * mgf(y, t)
    return {"lhs": lhs, "rhs": rhs,
            "factorizes": abs(lhs - rhs) / abs(rhs) < tol}


# ---------------------------------------------------------------------------
# The invariant / non-invariant boundary
# ---------------------------------------------------------------------------
def additive_defect(phi: Callable, sample: Sequence[float]) -> float:
    """Max ``|phi(x+y) - (phi(x)+phi(y))|`` over pairs (0 iff phi is additive)."""
    s = np.asarray(sample, dtype=float)
    return float(max(abs(phi(x + y) - (phi(x) + phi(y))) for x in s for y in s))


def homomorphism_add_mul_defect(phi: Callable, sample: Sequence[float]) -> float:
    """Max ``|phi(x+y) - phi(x)phi(y)|`` (0 iff phi maps ``+`` to ``*``)."""
    s = np.asarray(sample, dtype=float)
    return float(max(abs(phi(x + y) - phi(x) * phi(y)) for x in s for y in s))


def invariance_report(phi: Callable, sample: Sequence[float],
                      tol: float = 1e-9) -> dict:
    """Report which structures the bijection ``phi`` preserves on a sample.

    Distinguishes invariants (preserved) from non-invariants (the source of new
    tools): order, additivity (``+ -> +``), the additive-to-multiplicative
    homomorphism (``+ -> *``), the metric (isometry), and convexity.
    """
    s = np.sort(np.asarray(sample, dtype=float))
    vals = np.array([phi(x) for x in s])

    monotone = bool(np.all(np.diff(vals) > -tol) or np.all(np.diff(vals) < tol))
    add_def = additive_defect(phi, s)
    hom_def = homomorphism_add_mul_defect(phi, s)

    # Metric distortion: spread of |phi(x)-phi(y)| / |x-y|.
    ratios = []
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            if abs(s[j] - s[i]) > tol:
                ratios.append(abs(vals[j] - vals[i]) / abs(s[j] - s[i]))
    ratios = np.array(ratios)
    isometry = bool(ratios.size and (ratios.max() - ratios.min()) < tol)
    distortion = float(ratios.max() / ratios.min()) if ratios.size else 1.0

    # Convexity via second differences on the (sorted) sample.
    convex = bool(len(vals) >= 3 and np.all(np.diff(vals, 2) > -tol))

    return {
        "monotone (order)": monotone,
        "additive (+ -> +)": add_def < tol,
        "homomorphism (+ -> *)": hom_def < tol,
        "isometry (metric)": isometry,
        "convex": convex,
        "additive_defect": add_def,
        "metric_distortion": distortion,
    }


# ---------------------------------------------------------------------------
# Twisted primes: a non-invariant of the twin product
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Homomorphism signature: the four productive frames
# ---------------------------------------------------------------------------
def homomorphism_signature(phi: Callable, sample: Sequence[float],
                           tol: float = 1e-9) -> dict:
    """Classify ``phi`` by which homomorphism, if any, it realizes.

    The four vanishing defects label the four \"coherent\" frames, each tied to
    an application:

    * ``+ -> +`` (linear) -- addition preserved (rigid);
    * ``+ -> *`` (exp) -- MGF / Chernoff / concentration;
    * ``* -> +`` (log) -- entropy / log-domain;
    * ``* -> *`` (power) -- multiplication / classical primes.

    A ``phi`` realizing none is ``generic`` -- the source of genuinely new
    twin arithmetic.
    """
    s = [float(x) for x in sample]
    defects = {
        "+->+": max(abs(phi(x + y) - (phi(x) + phi(y))) for x in s for y in s),
        "+->*": max(abs(phi(x + y) - phi(x) * phi(y)) for x in s for y in s),
        "*->+": max(abs(phi(x * y) - (phi(x) + phi(y))) for x in s for y in s),
        "*->*": max(abs(phi(x * y) - phi(x) * phi(y)) for x in s for y in s),
    }
    types = [k for k, v in defects.items() if v < tol]
    return {"defects": {k: float(v) for k, v in defects.items()},
            "types": types or ["generic"]}


# ---------------------------------------------------------------------------
# Affine twisted primes: a closed-form characterization
# ---------------------------------------------------------------------------
def affine_twisted_prime(c: int, d: int, n: int) -> bool:
    r"""Whether ``n`` is prime for the affine twin product of ``phi(x)=cx+d``.

    The twin product is
    ``a (x)_phi b = ((ca+d)(cb+d) - d)/c``, so ``n`` is composite iff
    ``cn+d`` factors as ``(ca+d)(cb+d)`` with integer ``a,b >= 2``. Hence ``n``
    is twisted-prime iff ``cn+d`` admits no such factorization -- a divisibility
    condition on ``cn+d`` (e.g. for ``c=2,d=1``: ``2n+1`` not a product of two
    odd factors ``>= 5``).
    """
    if n <= 1:
        return False
    M = c * n + d
    a = 2
    while True:
        fa = c * a + d
        if fa * fa > M:
            break
        if M % fa == 0:
            fb = M // fa
            if (fb - d) % c == 0 and (fb - d) // c >= 2:
                return False
        a += 1
    return True


def affine_twisted_primes(c: int, d: int, limit: int) -> List[int]:
    """The affine-twisted primes up to ``limit`` via the closed-form predicate."""
    return [n for n in range(2, limit + 1) if affine_twisted_prime(c, d, n)]


def verify_affine_prime_formula(c: int, d: int, limit: int) -> bool:
    """Check the closed form against the brute-force ``twisted_primes``."""
    from arithmetics.core.transfer import AffineTransfer
    from arithmetics.zeta.euler_product import twisted_primes
    return affine_twisted_primes(c, d, limit) == twisted_primes(
        AffineTransfer(c, d), limit)


# ---------------------------------------------------------------------------
# Discovery sweeps
# ---------------------------------------------------------------------------
def discover_homomorphism_types(
        sample: Optional[Sequence[float]] = None,
        catalog: Optional[Dict[str, Callable]] = None) -> List[dict]:
    """Sweep a catalog of bijections and classify each by homomorphism type.

    Surfaces the four-frame structure automatically: which ``phi`` carry
    ``+ -> *`` (concentration), ``* -> +`` (entropy), ``* -> *`` (primes), and
    which are generic (new arithmetic).
    """
    if sample is None:
        sample = [1.2, 1.5, 2.0, 2.5, 3.0]
    if catalog is None:
        catalog = {
            "identity": lambda x: x,
            "2x": lambda x: 2 * x,
            "2x+1": lambda x: 2 * x + 1,
            "exp": np.exp,
            "log": np.log,
            "x^2": lambda x: x ** 2,
            "x^3": lambda x: x ** 3,
            "sqrt": np.sqrt,
            "1/x": lambda x: 1.0 / x,
            "x^2+x": lambda x: x ** 2 + x,
        }
    rows = []
    for name, phi in catalog.items():
        sig = homomorphism_signature(phi, sample)
        rep = invariance_report(phi, sample)
        rows.append({"phi": name, "types": sig["types"],
                     "metric_distortion": rep["metric_distortion"],
                     "convex": rep["convex"]})
    return rows


def discover_twin_primes(limit: int = 30) -> List[dict]:
    """Twisted-prime spectrum with an automatic classification of each outcome.

    Each transfer's twisted primes are labelled ``classical`` (= the identity's),
    ``additive-collapse`` (the product becomes addition, primes ``{2,3}``), or
    ``new`` (a genuinely different set).
    """
    spectrum = twin_prime_spectrum(limit)
    classical = spectrum["identity"]
    rows = []
    for name, primes in spectrum.items():
        if primes == classical:
            kind = "classical"
        elif primes == [2, 3]:
            kind = "additive-collapse"
        else:
            kind = "new"
        rows.append({"transfer": name, "kind": kind,
                     "count": len(primes), "primes": primes})
    return rows


def twin_prime_spectrum(limit: int = 30,
                        transfers: Optional[Dict] = None) -> Dict[str, List[int]]:
    """Twisted primes (``otimes_phi``-irreducibles) for several transfers.

    Demonstrates that primality is *not* invariant: it depends on which
    operation plays the role of multiplication. Defaults compare the identity,
    a coherent power transfer, the exponential transfer (where ``otimes``
    collapses to addition), and an affine transfer (a genuinely new prime set).
    """
    from arithmetics.core.transfer import (
        IdentityTransfer, ExponentialTransfer, AffineTransfer,
        CoherentTwistTransfer,
    )
    from arithmetics.zeta.euler_product import twisted_primes

    if transfers is None:
        transfers = {
            "identity": IdentityTransfer(),
            "square x^2": CoherentTwistTransfer.square_transfer(),
            "exponential 2^n": ExponentialTransfer(2.0),
            "affine 2n+1": AffineTransfer(2, 1),
        }
    return {name: twisted_primes(phi, limit) for name, phi in transfers.items()}
