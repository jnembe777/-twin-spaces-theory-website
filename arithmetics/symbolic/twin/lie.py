"""
Compact Lie group actions and quantum twin operations.

This module extends the twin-spaces machinery to *compact Lie groups* acting
**linearly** (unitarily) on a vector / Hilbert space, realising the "quantum
twin operations" of Vol. 01:

.. math::

    \\psi_1 \\odot_{eg} \\psi_2 := U_g^{\\dagger}\\big(U_g\\psi_1 \\odot_e U_g\\psi_2\\big),
    \\qquad U_g \\text{ unitary}.

The decisive fact is that the **linearity obstruction generalises**: because the
``U_g`` are linear,

* a **linear** base operation (vector addition) is always preserved -- the twin
  family is *rigid*, ``L = G`` (cf. the ``GL_n`` / rotation examples);
* a **bilinear** base operation (a quantum gate, a product) transports to a
  genuinely different operation unless ``g`` is an algebra automorphism, so the
  kernel ``L`` is the automorphism group and the twin space is *flexible*.

We provide:

* :class:`LinearAction` -- a matrix Lie group (``SO(2)``, ``SO(3)``, ``SU(2)``,
  ``U(n)``) with a symbolic one-parameter form (where available) and a uniform
  sampler for Monte-Carlo kernel estimation on the group manifold;
* :class:`Operation` -- a base operation as a callable on vectors (addition,
  complex multiplication, cross product, generic bilinear gate);
* transport + kernel tools: :func:`twin_operation_so2` (exact symbolic),
  :func:`kernel_so2` (exact, 1-parameter), :func:`kernel_profile` (sampled,
  any compact group);
* :func:`discover_lie` -- the discovery runner, including the SU(2) quantum
  universality instance ``Op ≅ SU(2) ≅ S^3``.
"""

from typing import Callable, List, Optional

import numpy as np
import sympy as sp
from sympy import cos, sin, symbols, simplify, Matrix, Symbol, Interval, pi, solveset


__all__ = [
    "LinearAction", "Operation",
    "twin_operation_so2", "kernel_so2", "kernel_profile", "discover_lie",
]


# ---------------------------------------------------------------------------
# Vector helpers (work for both numpy arrays and SymPy matrices)
# ---------------------------------------------------------------------------
def _vec(like, components):
    if isinstance(like, np.ndarray):
        return np.array(components, dtype=like.dtype)
    return Matrix(components)


def _random_vec(rng, dim, field):
    if field == "C":
        return rng.standard_normal(dim) + 1j * rng.standard_normal(dim)
    return rng.standard_normal(dim)


# ---------------------------------------------------------------------------
# Compact Lie group action by linear (unitary) operators
# ---------------------------------------------------------------------------
class LinearAction:
    """A compact Lie group acting linearly on ``K^dim`` (``K = ℝ`` or ``ℂ``).

    ``sampler(rng)`` draws a Haar-ish random group element (numpy matrix) for
    Monte-Carlo kernel estimation; ``symbolic`` (optional) is a one-parameter
    matrix family for exact analysis.
    """

    kind = "lie-linear"

    def __init__(self, name: str, dim: int, field: str, sampler: Callable,
                 manifold: str = "", symbolic: Optional[Callable] = None,
                 param: Optional[Symbol] = None):
        self.name = name
        self.dim = dim
        self.field = field
        self._sampler = sampler
        self.manifold = manifold
        self._symbolic = symbolic
        self.param = param

    def sample(self, rng) -> np.ndarray:
        return self._sampler(rng)

    def symbolic_matrix(self):
        if self._symbolic is None:
            raise NotImplementedError(f"{self.name} has no symbolic one-parameter form")
        return self._symbolic(self.param)

    # -- catalogue ---------------------------------------------------------
    @classmethod
    def SO2(cls) -> "LinearAction":
        t = Symbol("theta", real=True)

        def sampler(rng):
            a = rng.uniform(0, 2 * np.pi)
            return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])

        def sym(theta):
            return Matrix([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])

        return cls("SO(2)", 2, "R", sampler, manifold="S^1",
                   symbolic=sym, param=t)

    @classmethod
    def SO3(cls) -> "LinearAction":
        def sampler(rng):
            q = rng.standard_normal(4)
            q /= np.linalg.norm(q)
            w, xx, yy, zz = q
            return np.array([
                [1 - 2 * (yy * yy + zz * zz), 2 * (xx * yy - zz * w), 2 * (xx * zz + yy * w)],
                [2 * (xx * yy + zz * w), 1 - 2 * (xx * xx + zz * zz), 2 * (yy * zz - xx * w)],
                [2 * (xx * zz - yy * w), 2 * (yy * zz + xx * w), 1 - 2 * (xx * xx + yy * yy)],
            ])

        return cls("SO(3)", 3, "R", sampler, manifold="SO(3)")

    @classmethod
    def SU2(cls) -> "LinearAction":
        def sampler(rng):
            q = rng.standard_normal(4)
            q /= np.linalg.norm(q)
            a, b, c, d = q
            return np.array([[a + 1j * b, c + 1j * d],
                             [-c + 1j * d, a - 1j * b]], dtype=complex)

        return cls("SU(2)", 2, "C", sampler, manifold="S^3")

    @classmethod
    def SUn(cls, n: int) -> "LinearAction":
        """``SU(n)`` with Haar sampling (Mezzadri QR + unit determinant)."""
        def sampler(rng):
            z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n)))
            z /= np.sqrt(2.0)
            q, r = np.linalg.qr(z)
            ph = np.diagonal(r) / np.abs(np.diagonal(r))
            u = q * ph                       # Haar-random U(n)
            return u / np.linalg.det(u) ** (1.0 / n)   # project to SU(n)

        dim_manifold = n * n - 1
        return cls(f"SU({n})", n, "C", sampler, manifold=f"dim {dim_manifold}")

    def __repr__(self):
        return f"LinearAction({self.name!r}, dim={self.dim}, manifold={self.manifold})"


# ---------------------------------------------------------------------------
# Base operations on the vector space
# ---------------------------------------------------------------------------
class Operation:
    """A base operation ``⊙_e`` as a callable ``func(x, y) -> vector``.

    ``linear`` marks operations that are linear in their arguments (e.g.
    addition); such operations are rigid under any linear group action.
    """

    def __init__(self, name: str, dim: int, func: Callable,
                 field: str = "C", linear: bool = False):
        self.name = name
        self.dim = dim
        self.func = func
        self.field = field
        self.linear = linear

    def __call__(self, x, y):
        return self.func(x, y)

    @classmethod
    def addition(cls, dim: int, field: str = "C") -> "Operation":
        return cls("addition", dim, lambda x, y: x + y, field, linear=True)

    @classmethod
    def complex_multiplication(cls) -> "Operation":
        # ℝ^2 ≅ ℂ ;  (x0+x1 i)(y0+y1 i)
        def mul(x, y):
            return _vec(x, [x[0] * y[0] - x[1] * y[1],
                            x[0] * y[1] + x[1] * y[0]])
        return cls("complex-mul", 2, mul, field="R")

    @classmethod
    def cross_product(cls) -> "Operation":
        def cross(x, y):
            return _vec(x, [x[1] * y[2] - x[2] * y[1],
                            x[2] * y[0] - x[0] * y[2],
                            x[0] * y[1] - x[1] * y[0]])
        return cls("cross-product", 3, cross, field="R")

    @classmethod
    def random_gate(cls, dim: int = 2, seed: int = 0,
                    field: str = "C") -> "Operation":
        """A generic bilinear 'quantum gate' with random structure tensor."""
        rng = np.random.default_rng(seed)
        if field == "C":
            tensor = (rng.standard_normal((dim, dim, dim))
                      + 1j * rng.standard_normal((dim, dim, dim)))
        else:
            tensor = rng.standard_normal((dim, dim, dim))

        def gate(x, y):
            return np.einsum("kij,i,j->k", tensor, x, y)
        return cls(f"random-gate(seed={seed})", dim, gate, field=field)


# ---------------------------------------------------------------------------
# Exact symbolic transport / kernel for the one-parameter group SO(2)
# ---------------------------------------------------------------------------
def twin_operation_so2(op: Operation):
    """Exact symbolic twin operation ``⊙_{eθ}`` under ``SO(2)``.

    Returns ``(result_vector, theta)`` where ``result_vector`` is the SymPy
    column ``x ⊙_{eθ} y`` in the symbols ``x0, x1, y0, y1``.
    """
    if op.dim != 2:
        raise ValueError("twin_operation_so2 expects a 2-dimensional operation")
    theta = Symbol("theta", real=True)
    R = Matrix([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    Rinv = R.T  # orthogonal: R^{-1} = R^T
    x = Matrix(symbols("x0 x1"))
    y = Matrix(symbols("y0 y1"))
    transported = simplify(Rinv * op.func(R * x, R * y))
    return transported, theta


def kernel_so2(op: Operation):
    """Exact structural kernel of an operation under ``SO(2)``.

    Returns a dict with the kernel (a SymPy set of angles in ``[0, 2π)``),
    whether the twins are ``rigid`` (``L = SO(2)``) and whether the kernel is
    ``trivial`` (``L = {0}`` ⇒ ``Op ≅ SO(2) ≅ S^1``).
    """
    transported, theta = twin_operation_so2(op)
    x0, x1, y0, y1 = symbols("x0 x1 y0 y1")
    base = op.func(Matrix([x0, x1]), Matrix([y0, y1]))

    # The operation is preserved iff the residual vanishes identically in x, y:
    # collect the angle-dependent coefficients of every monomial.
    eqs = set()
    for k in range(2):
        residual = sp.expand(transported[k] - base[k])
        if residual == 0:
            continue
        poly = sp.Poly(residual, x0, x1, y0, y1)
        for coeff in poly.coeffs():
            c = simplify(coeff)
            if c != 0:
                eqs.add(c)

    if not eqs:
        return {"kernel": "SO(2)", "rigid": True, "trivial": False,
                "Op": "{e} (trivial)"}

    domain = Interval(0, 2 * pi, right_open=True)
    sol = None
    for e in eqs:
        s = solveset(e, theta, domain=domain)
        sol = s if sol is None else sol.intersect(s)
    sol = sol if sol is not None else sp.EmptySet

    trivial = sol == sp.FiniteSet(0)
    return {"kernel": sol, "rigid": False, "trivial": trivial,
            "Op": "SO(2) ≅ S^1" if trivial else "SO(2)/L"}


# ---------------------------------------------------------------------------
# Sampled kernel estimation for any compact linear group (incl. SU(2))
# ---------------------------------------------------------------------------
def _preserves(op: Operation, g: np.ndarray, g_inv: np.ndarray, rng,
               tol: float = 1e-9, trials: int = 4) -> bool:
    """Test (by random probing) whether ``g`` preserves ``op``."""
    for _ in range(trials):
        x = _random_vec(rng, op.dim, op.field)
        y = _random_vec(rng, op.dim, op.field)
        lhs = g_inv @ op.func(g @ x, g @ y)
        rhs = op.func(x, y)
        if np.max(np.abs(np.asarray(lhs) - np.asarray(rhs))) > tol:
            return False
    return True


def kernel_profile(op: Operation, action: LinearAction, n_samples: int = 400,
                   tol: float = 1e-9, seed: int = 0) -> dict:
    """Monte-Carlo estimate of the structural kernel on the group manifold.

    Samples ``n_samples`` group elements and counts how many preserve ``op``.
    Random elements miss any positive-codimension kernel almost surely, so:

    * all preserve  ⇒ ``rigid`` (``L = G``);
    * none preserve ⇒ ``kernel_trivial`` (``Op ≅ G``, the full manifold);
    * a fraction preserve ⇒ a positive-dimensional proper kernel.
    """
    rng = np.random.default_rng(seed)
    preserving = 0
    for _ in range(n_samples):
        g = action.sample(rng)
        g_inv = np.linalg.inv(g)
        if _preserves(op, g, g_inv, rng, tol=tol):
            preserving += 1
    return {
        "group": action.name,
        "manifold": action.manifold,
        "operation": op.name,
        "samples": n_samples,
        "preserving": preserving,
        "fraction": preserving / n_samples,
        "rigid": preserving == n_samples,
        "kernel_trivial": preserving == 0,
    }


# ---------------------------------------------------------------------------
# Discovery runner for compact Lie groups
# ---------------------------------------------------------------------------
def discover_lie(n_samples: int = 400, seed: int = 0) -> List[dict]:
    """Run the machinery over compact-Lie (group, operation) pairs.

    Includes the SU(2) quantum-universality instance: a generic qubit gate has
    a trivial structural kernel, so ``Op ≅ SU(2) ≅ S^3``.
    """
    rows: List[dict] = []

    # --- SO(2): exact symbolic analysis -----------------------------------
    for op in (Operation.addition(2, "R"), Operation.complex_multiplication()):
        info = kernel_so2(op)
        rows.append({
            "group": "SO(2)", "manifold": "S^1", "operation": op.name,
            "method": "symbolic", "rigid": info["rigid"],
            "kernel_trivial": info["trivial"],
            "kernel": str(info["kernel"]), "Op": info["Op"],
        })

    # --- SO(3), SU(2): sampled analysis -----------------------------------
    sampled = [
        (LinearAction.SO3(), Operation.addition(3, "R")),
        (LinearAction.SO3(), Operation.cross_product()),
        (LinearAction.SU2(), Operation.addition(2, "C")),
        (LinearAction.SU2(), Operation.random_gate(2, seed=1, field="C")),
    ]
    for action, op in sampled:
        prof = kernel_profile(op, action, n_samples=n_samples, seed=seed)
        if prof["rigid"]:
            op_label = "{e} (trivial)"
        elif prof["kernel_trivial"]:
            op_label = f"{action.name} ≅ {action.manifold}"
        else:
            op_label = f"{action.name}/L"
        rows.append({
            "group": action.name, "manifold": action.manifold,
            "operation": op.name, "method": f"sampled(n={prof['samples']})",
            "rigid": prof["rigid"], "kernel_trivial": prof["kernel_trivial"],
            "kernel": f"frac_preserving={prof['fraction']:.3f}", "Op": op_label,
        })

    return rows
