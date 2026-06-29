"""
The multiplicative pillar: twisted arithmetic, Hilbert monoids, and the
twisted-zeta Euler product.

Every twin product ``a (x)_phi b = phi^{-1}(phi(a) phi(b))`` is, by
construction, conjugate to ordinary multiplication; so the twisted arithmetic is
a multiplicative monoid in disguise. This module identifies *which* monoid for
an affine generator ``phi(x) = c x + d``, with a decisive correction:

* **the correct twin unit is** ``phi^{-1}(1) = (1-d)/c``, not ``1``. Using it,
  the affine arithmetic is exactly the multiplicative monoid of the arithmetic
  progression ``{ m : m == d (mod c) }`` -- a **Hilbert monoid**.

Consequences, all computable here:

* its irreducibles are the **primes in the arithmetic progression** (relabeled),
  e.g. ``(c,d) = (2,1)`` gives the odd primes, so the corrected twisted primes
  are ``{ n : 2n+1 is prime }`` (a Sophie-Germain-flavoured set);
* factorization can be **non-unique** (``(3,1)``: ``100 = 4*25 = 10*10``),
  exactly the classical failure of unique factorization in a residue class;
* the **twisted-zeta Euler product breaks** by precisely the non-uniqueness:
  :func:`euler_defect` measures ``sum (r(m)-1) m^{-s}`` where ``r(m)`` is the
  number of factorizations.

This connects the twin framework to primes in arithmetic progressions and
Dirichlet L-functions, and corrects the unit used by
:mod:`arithmetics.zeta.euler_product`.
"""

from typing import Dict, List, Optional, Tuple

__all__ = [
    "twisted_unit", "ap_is_closed", "ap_monoid", "ap_primes",
    "factorizations", "num_factorizations", "find_non_unique_factorization",
    "is_unique_factorization", "corrected_twisted_primes",
    "progression_zeta", "progression_zeta_closed", "euler_product", "euler_defect",
    "compare_to_repo_twisted_primes",
]


# ---------------------------------------------------------------------------
# The twin unit and the arithmetic-progression monoid
# ---------------------------------------------------------------------------
def twisted_unit(c: int, d: int) -> float:
    """The unit of the affine twin product: ``phi^{-1}(1) = (1-d)/c``."""
    return (1 - d) / c


def ap_is_closed(c: int, d: int) -> bool:
    """Whether ``{m == d (mod c)}`` is closed under multiplication (``d^2==d``)."""
    return (d * d - d) % c == 0


def ap_monoid(c: int, d: int, limit: int) -> List[int]:
    """Positive elements ``>= 1`` of the residue-class monoid, up to ``limit``."""
    r = d % c
    return [m for m in range(1, limit + 1) if m % c == r]


def ap_primes(c: int, d: int, limit: int) -> List[int]:
    """Irreducibles ("Hilbert primes") of the residue-class monoid up to ``limit``.

    ``m > 1`` is irreducible iff it has no divisor ``a`` in the monoid with
    ``1 < a < m`` and ``m/a`` also in the monoid.
    """
    r = d % c
    monoid = set(ap_monoid(c, d, limit))
    primes = []
    for m in sorted(monoid):
        if m == 1:
            continue
        reducible = False
        a = 2
        while a * a <= m:
            if m % a == 0 and a % c == r and (m // a) % c == r:
                reducible = True
                break
            a += 1
        if not reducible:
            primes.append(m)
    return primes


# ---------------------------------------------------------------------------
# Factorization (possibly non-unique)
# ---------------------------------------------------------------------------
def factorizations(c: int, d: int, m: int,
                   primes: Optional[List[int]] = None) -> List[Tuple[int, ...]]:
    """All factorizations of ``m`` into monoid primes (canonical, non-decreasing)."""
    if primes is None:
        primes = ap_primes(c, d, m)
    P = [p for p in primes if p <= m]

    def rec(rem: int, start: int) -> List[Tuple[int, ...]]:
        if rem == 1:
            return [()]
        out = []
        for i in range(start, len(P)):
            p = P[i]
            if p > rem:
                break
            if rem % p == 0:
                for tail in rec(rem // p, i):
                    out.append((p,) + tail)
        return out

    return rec(m, 0)


def num_factorizations(c: int, d: int, m: int,
                       primes: Optional[List[int]] = None) -> int:
    """Number of distinct factorizations of ``m`` into monoid primes."""
    return len(factorizations(c, d, m, primes))


def find_non_unique_factorization(c: int, d: int, limit: int) -> Optional[dict]:
    """Smallest monoid element with more than one factorization (or ``None``)."""
    primes = ap_primes(c, d, limit)
    for m in ap_monoid(c, d, limit):
        if m == 1:
            continue
        facs = factorizations(c, d, m, primes)
        if len(facs) > 1:
            return {"m": m, "factorizations": facs,
                    "twisted_n": (m - d) // c}
    return None


def is_unique_factorization(c: int, d: int, limit: int) -> bool:
    """Whether factorization is unique for every monoid element up to ``limit``."""
    return find_non_unique_factorization(c, d, limit) is None


def corrected_twisted_primes(c: int, d: int, limit: int) -> List[int]:
    """Corrected affine-twisted primes ``n`` (using the proper unit ``(1-d)/c``).

    These are ``n = (m - d)/c`` for the monoid primes ``m = c n + d``.
    """
    return [(m - d) // c for m in ap_primes(c, d, c * limit + d)
            if (m - d) % c == 0 and 1 <= (m - d) // c <= limit]


# ---------------------------------------------------------------------------
# The twisted zeta and its Euler product
# ---------------------------------------------------------------------------
def progression_zeta(c: int, d: int, s: complex, limit: int) -> complex:
    """Partial Dirichlet series of the monoid: ``sum_{m == d (c), m<=limit} m^{-s}``.

    The full series is a finite combination of Hurwitz zetas / Dirichlet
    L-functions for the modulus ``c`` (see :func:`progression_zeta_closed`).
    """
    return sum(complex(m) ** (-s) for m in ap_monoid(c, d, limit) if m > 1)


def progression_zeta_closed(c: int, d: int, s):
    """Closed form ``sum_{n>=1, n==d (c)} n^{-s} = c^{-s} * zeta(s, r/c)`` (Hurwitz).

    Here ``r`` is the residue of ``d`` in ``{1,...,c}``. For ``(c,d)=(2,1)`` this
    is ``(1-2^{-s}) zeta(s)``; for ``(3,1)`` it is ``3^{-s} zeta(s, 1/3)``. The
    twisted zeta of the affine multiplicative frame is thus an explicit
    Dirichlet/Hurwitz object.
    """
    import mpmath
    r = d % c
    if r == 0:
        r = c
    return mpmath.mpf(c) ** (-s) * mpmath.zeta(s, mpmath.mpf(r) / c)


def euler_product(c: int, d: int, s: complex, limit: int) -> complex:
    """Truncated Euler product ``prod_{p prime in monoid, p<=limit}(1-p^{-s})^{-1}``."""
    out = 1.0 + 0j
    for p in ap_primes(c, d, limit):
        out *= 1.0 / (1.0 - complex(p) ** (-s))
    return out


def euler_defect(c: int, d: int, s: complex, limit: int) -> complex:
    """The Euler-product defect ``sum_{m<=limit} (r(m)-1) m^{-s}``.

    Zero iff factorization is unique; non-zero by exactly the multiplicity of
    non-unique factorizations (the twisted-zeta Euler product overcounts).
    """
    primes = ap_primes(c, d, limit)
    total = 0.0 + 0j
    for m in ap_monoid(c, d, limit):
        if m == 1:
            continue
        r = num_factorizations(c, d, m, primes)
        if r != 1:
            total += (r - 1) * complex(m) ** (-s)
    return total


# ---------------------------------------------------------------------------
# Comparison with the repository's (uncorrected) twisted primes
# ---------------------------------------------------------------------------
def compare_to_repo_twisted_primes(c: int, d: int, limit: int) -> dict:
    """Contrast the corrected twisted primes with the repo's (unit = 1) version."""
    from arithmetics.core.transfer import AffineTransfer
    from arithmetics.zeta.euler_product import twisted_primes

    corrected = corrected_twisted_primes(c, d, limit)
    repo = twisted_primes(AffineTransfer(c, d), limit)
    return {
        "twin_unit": twisted_unit(c, d),
        "corrected": corrected,
        "repo_uncorrected": repo,
        "agree": corrected == repo,
    }
