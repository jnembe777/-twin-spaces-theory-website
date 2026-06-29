"""
Real arithmetic-task cost functionals for twin operations.

This module makes the decision framework *operational*: it attaches genuine,
measurable costs --- numerical accuracy, dynamic range, transcendental-op count
--- to concrete computational tasks, so the "optimal base before computing" can
be chosen by measurement rather than assertion.

The bridge to arithmetic is the reduction under the twin sum
``⊕_φ`` of a bijection ``φ``:

.. math::

    \\bigoplus_{\\varphi} x_i \;=\; \\varphi^{-1}\\Bigl(\\sum_i \\varphi(x_i)\\Bigr).

For ``φ = \\log`` this is the **product** ``∏ x_i``, and the transformed total
``Σ \\log x_i`` is the **log-likelihood** --- which stays representable when the
product itself underflows. Computing a target in the *transformed domain* (the
twin/conjugated arithmetic) versus the *original domain* is exactly the
log-domain trick of numerical computing; here it is measured and decided.

Two well-posed decisions are provided:

* **Domain of computation** (fixed target): transformed vs original domain for
  the transformed total ``T = Σ φ(x_i)`` --- see :class:`TransformedTotal`,
  :func:`total_error`, :func:`recommend_domain`.
* **Optimal base** (representation/approximation): choose the bijection that
  best linearises data --- see :func:`linearization_rmse`, :func:`optimal_base`.

There is also an honest **speed/stability trade-off**: the transformed domain
costs more transcendental calls (:func:`op_count`) but controls dynamic range.
"""

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import mpmath

__all__ = [
    "Bijection", "TransformedTotal", "relative_error", "total_error",
    "dynamic_range", "recommend_domain", "op_count",
    "linearization_rmse", "optimal_base", "arithmetic_task_report",
]


# ---------------------------------------------------------------------------
# Bijections (the computational domains / twin bases)
# ---------------------------------------------------------------------------
class Bijection:
    """A monotone bijection ``φ`` defining a twin arithmetic on its domain.

    Carries float and mpmath evaluations of ``φ``, the inverse ``φ⁻¹``, and ---
    when known --- the closed-form original-domain operation ``⊕_φ`` (so a
    reduction can be performed without leaving the original domain).
    """

    def __init__(self, name: str, f: Callable, f_inv: Callable, f_mp: Callable,
                 original_op: Optional[Callable] = None, op_symbol: str = ""):
        self.name = name
        self.f = f
        self.f_inv = f_inv
        self.f_mp = f_mp
        self.original_op = original_op
        self.op_symbol = op_symbol

    @classmethod
    def identity(cls) -> "Bijection":
        return cls("identity", lambda x: x, lambda x: x,
                   lambda x: mpmath.mpf(x),
                   original_op=lambda a, b: a + b, op_symbol="+")

    @classmethod
    def logarithm(cls) -> "Bijection":
        return cls("log", math.log, math.exp, mpmath.log,
                   original_op=lambda a, b: a * b, op_symbol="*")

    @classmethod
    def sqrt(cls) -> "Bijection":
        return cls("sqrt", math.sqrt, lambda x: x * x,
                   lambda x: mpmath.sqrt(x), op_symbol="(sqrt)")

    def __repr__(self):
        return f"Bijection({self.name!r})"


# ---------------------------------------------------------------------------
# Decision A: domain of computation for a fixed transformed total
# ---------------------------------------------------------------------------
class TransformedTotal:
    r"""The transformed total ``T = Σ_i φ(x_i)`` of a reduction under ``⊕_φ``.

    For ``φ = log`` this is the log-likelihood ``Σ log x_i``; the result of the
    reduction itself is ``φ⁻¹(T) = ∏ x_i``. The transformed total is what one
    actually keeps in stable computation.
    """

    def __init__(self, bijection: Bijection):
        self.phi = bijection

    def via_transformed_domain(self, xs: Sequence[float]) -> float:
        """Stable: sum ``φ(x_i)`` directly in the transformed domain."""
        return math.fsum(self.phi.f(x) for x in xs)

    def via_original_domain(self, xs: Sequence[float]) -> float:
        """Reduce in the original domain (``⊕_φ``), then transform the result.

        Exhibits overflow/underflow: e.g. for ``φ = log`` this multiplies the
        ``x_i`` (which may underflow to 0) before taking the log.
        """
        if self.phi.original_op is None:
            raise NotImplementedError(f"no closed-form ⊕ for {self.phi.name}")
        r = xs[0]
        for x in xs[1:]:
            r = self.phi.original_op(r, x)
        if r == 0:
            return float("-inf")
        try:
            return self.phi.f(r)
        except (OverflowError, ValueError):
            return float("inf")

    def reference(self, xs: Sequence[float], dps: int = 60) -> float:
        """High-precision reference for ``T`` via mpmath."""
        prev = mpmath.mp.dps
        mpmath.mp.dps = dps
        try:
            total = mpmath.fsum(self.phi.f_mp(mpmath.mpf(x)) for x in xs)
            return float(total)
        finally:
            mpmath.mp.dps = prev


def relative_error(approx: float, reference: float) -> float:
    """Relative error ``|approx - reference| / |reference|`` (robust to inf)."""
    if math.isinf(approx) or math.isnan(approx):
        return float("inf")
    denom = abs(reference) if reference != 0 else 1.0
    return abs(approx - reference) / denom


def total_error(task: TransformedTotal, xs: Sequence[float],
                method: str = "transformed", dps: int = 60) -> float:
    """Relative error of computing ``T`` by the given method."""
    ref = task.reference(xs, dps=dps)
    approx = (task.via_transformed_domain(xs) if method == "transformed"
              else task.via_original_domain(xs))
    return relative_error(approx, ref)


def dynamic_range(xs: Sequence[float]) -> float:
    """Decadic spread ``log10(max|x|) - log10(min|x|)`` of the data."""
    mags = [abs(x) for x in xs if x != 0]
    if not mags:
        return 0.0
    return math.log10(max(mags)) - math.log10(min(mags))


def recommend_domain(xs: Sequence[float], headroom: float = 250.0) -> str:
    """Pre-computation rule: pick the computational domain from the data range.

    If the product's decadic magnitude would exceed float64 headroom (~308),
    recommend the transformed (log) domain; otherwise either is safe.
    """
    total_decades = sum(abs(math.log10(abs(x))) for x in xs if x != 0)
    return "transformed" if total_decades > headroom else "either"


def op_count(n: int) -> Dict[str, Dict[str, int]]:
    """Transcendental / arithmetic op counts for an ``n``-element reduction.

    The transformed-domain method is more stable but uses more transcendental
    calls than the naive fold --- the honest speed/stability trade-off.
    """
    return {
        "naive_fold": {"transcendental": 3 * (n - 1), "arithmetic": n - 1},
        "transformed_domain": {"transcendental": n + 1, "arithmetic": n - 1},
    }


# ---------------------------------------------------------------------------
# Decision B: optimal base for representation / approximation
# ---------------------------------------------------------------------------
# Axis transforms (x-transform, y-transform, inverse-y-transform).
_AXIS_TRANSFORMS = {
    "linear":   (lambda x: x,        lambda y: y,        lambda v: v),
    "loglog":   (math.log,           math.log,           math.exp),
    "semilogy": (lambda x: x,        math.log,           math.exp),
    "semilogx": (math.log,           lambda y: y,        lambda v: v),
}


def _linear_fit(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, float]:
    """Least-squares slope/intercept of ``y ≈ m x + c``."""
    n = len(xs)
    sx = math.fsum(xs)
    sy = math.fsum(ys)
    sxx = math.fsum(x * x for x in xs)
    sxy = math.fsum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    m = (n * sxy - sx * sy) / denom
    c = (sy - m * sx) / n
    return m, c


def linearization_rmse(transform: str, xs: Sequence[float],
                       ys: Sequence[float]) -> float:
    """RMSE (in original ``y`` units) of the best twin-linear fit under a base.

    Fits a line in the transformed coordinates, predicts, back-transforms to
    ``y``, and measures the error against the data --- legitimate model
    selection across computational bases.
    """
    fx, fy, fy_inv = _AXIS_TRANSFORMS[transform]
    tx = [fx(x) for x in xs]
    ty = [fy(y) for y in ys]
    m, c = _linear_fit(tx, ty)
    sq = [(fy_inv(m * fx(x) + c) - y) ** 2 for x, y in zip(xs, ys)]
    return math.sqrt(math.fsum(sq) / len(xs))


def optimal_base(xs: Sequence[float], ys: Sequence[float],
                 transforms: Optional[Sequence[str]] = None) -> dict:
    """Select the base (axis transform) minimising back-transformed RMSE.

    Realises "determine the optimal base before computing": e.g. a power law is
    linearised by ``loglog``, an exponential by ``semilogy``, a line by
    ``linear``.
    """
    transforms = transforms or list(_AXIS_TRANSFORMS)
    scored = []
    for t in transforms:
        try:
            scored.append((t, linearization_rmse(t, xs, ys)))
        except (ValueError, ZeroDivisionError):
            continue
    scored.sort(key=lambda kv: kv[1])
    return {"optimal_base": scored[0][0], "rmse": scored[0][1],
            "ranking": scored}


# ---------------------------------------------------------------------------
# Convenience report
# ---------------------------------------------------------------------------
def arithmetic_task_report(xs: Sequence[float], dps: int = 60) -> dict:
    """Compare original vs transformed domain for the log-likelihood task."""
    task = TransformedTotal(Bijection.logarithm())
    return {
        "n": len(xs),
        "dynamic_range_decades": dynamic_range(xs),
        "recommend": recommend_domain(xs),
        "error_original_domain": total_error(task, xs, "original", dps),
        "error_transformed_domain": total_error(task, xs, "transformed", dps),
        "op_count": op_count(len(xs)),
    }
