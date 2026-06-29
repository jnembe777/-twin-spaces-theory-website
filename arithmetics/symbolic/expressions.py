"""
Core symbolic layer for the twisted zeta framework.

This module provides:

* A small set of shared SymPy symbols (``n``, ``s``, ``p``, ``alpha`` ...)
  used consistently across the symbolic package.
* The iterated operators :class:`IterExp` (``exp^{∘p}``) and :class:`IterLog`
  (``log^{∘p}``), which carry the compact ``\\exp^{\\circ p}`` notation of the
  paper while still expanding to native nested ``exp``/``log`` for concrete
  levels (so they evaluate and differentiate like ordinary SymPy objects).
* The :class:`Formula` wrapper, a thin convenience layer around a SymPy
  expression that exposes the four output formats requested by the framework:
  the native SymPy object, LaTeX, Unicode/ASCII text, and a numeric bridge to
  mpmath.

The goal is to mirror the *numeric* framework (``arithmetics.core`` /
``arithmetics.zeta``) symbolically, so that every formula can be inspected,
manipulated, typeset, and checked.
"""

from typing import Optional, Sequence, Union, Mapping

import sympy as sp
from sympy import (
    Function, Symbol, Dummy, Integer, Mul, Product, exp, log,
    sympify, latex, simplify, pretty, sstr,
)
from sympy.core.function import ArgumentIndexError


# ---------------------------------------------------------------------------
# Shared symbols
# ---------------------------------------------------------------------------
# Arithmetic index and the complex variable of the zeta function.
n = Symbol("n", positive=True, integer=True)
s = Symbol("s")

# Cocycle test points.
a = Symbol("a", positive=True)
b = Symbol("b", positive=True)
c = Symbol("c", positive=True)

# Hierarchy level (kept a non-negative integer where it matters).
p = Symbol("p", integer=True, nonnegative=True)

# Generic positive reals (for level-p operands x ⊕_p y, etc.).
x = Symbol("x", positive=True)
y = Symbol("y", positive=True)

# Transfer parameters.
alpha = Symbol("alpha", positive=True)
beta = Symbol("beta", positive=True)


__all__ = [
    "n", "s", "a", "b", "c", "p", "x", "y", "alpha", "beta",
    "IterExp", "IterLog", "Formula",
]


# ---------------------------------------------------------------------------
# Iterated exponential / logarithm
# ---------------------------------------------------------------------------
class IterExp(Function):
    r"""The ``p``-fold iterated exponential :math:`\exp^{\circ p}`.

    ``IterExp(x, p)`` represents :math:`\Phi_p(x) = \exp^{\circ p}(x)`.

    Automatic simplifications:

    * ``IterExp(x, 0)`` collapses to ``x``;
    * a negative integer level folds into :class:`IterLog`;
    * ``IterExp(IterLog(x, p), p)`` cancels to ``x``.

    For a concrete non-negative integer level, :meth:`doit` expands to the
    native nested ``exp`` (so the expression evaluates and typesets exactly);
    the un-expanded form keeps the compact ``\exp^{\circ p}`` notation.
    """

    nargs = 2

    @classmethod
    def eval(cls, arg, level):
        if level.is_Integer:
            lv = int(level)
            if lv == 0:
                return arg
            if lv < 0:
                return IterLog(arg, Integer(-lv))
        # Cancel an inner iterated logarithm of the same level.
        if isinstance(arg, IterLog) and arg.args[1] == level:
            return arg.args[0]
        return None

    def doit(self, deep=True, **hints):
        arg, level = self.args
        if deep:
            arg = arg.doit(deep=deep, **hints)
        if level.is_Integer and level >= 0:
            result = arg
            for _ in range(int(level)):
                result = exp(result)
            return result
        return IterExp(arg, level)

    def fdiff(self, argindex=1):
        # d/dx exp^{∘p}(x) = ∏_{k=1}^{p} exp^{∘k}(x)   (chain rule)
        if argindex != 1:
            raise ArgumentIndexError(self, argindex)
        arg, level = self.args
        if level.is_Integer and level >= 0:
            lv = int(level)
            if lv == 0:
                return Integer(1)
            return Mul(*[IterExp(arg, Integer(k)) for k in range(1, lv + 1)])
        k = Dummy("k", integer=True, positive=True)
        return Product(IterExp(arg, k), (k, 1, level))

    # -- printing -----------------------------------------------------------
    def _latex(self, printer, exp=None, **kwargs):
        arg, level = self.args
        base = r"\exp^{\circ %s}\!\left(%s\right)" % (
            printer._print(level), printer._print(arg)
        )
        # ``exp`` is supplied (already typeset) when this appears as a power
        # base, e.g. (exp^{∘p}(x))^{k}; wrap so the superscripts don't collide.
        if exp is not None:
            return r"\left(%s\right)^{%s}" % (base, exp)
        return base

    def _sympystr(self, printer, *args, **kwargs):
        arg, level = self.args
        return "exp^o%s(%s)" % (printer._print(level), printer._print(arg))

    def _pretty(self, printer, *args, **kwargs):
        return _pretty_iterated(printer, "exp", self.args)


class IterLog(Function):
    r"""The ``p``-fold iterated logarithm :math:`\log^{\circ p}`.

    ``IterLog(x, p)`` represents :math:`\Phi_p^{-1}(x) = \log^{\circ p}(x)`,
    the inverse of :class:`IterExp` at the same level.
    """

    nargs = 2

    @classmethod
    def eval(cls, arg, level):
        if level.is_Integer:
            lv = int(level)
            if lv == 0:
                return arg
            if lv < 0:
                return IterExp(arg, Integer(-lv))
        if isinstance(arg, IterExp) and arg.args[1] == level:
            return arg.args[0]
        return None

    def doit(self, deep=True, **hints):
        arg, level = self.args
        if deep:
            arg = arg.doit(deep=deep, **hints)
        if level.is_Integer and level >= 0:
            result = arg
            for _ in range(int(level)):
                result = log(result)
            return result
        return IterLog(arg, level)

    def fdiff(self, argindex=1):
        # d/dx log^{∘p}(x) = ∏_{k=0}^{p-1} 1 / log^{∘k}(x)
        if argindex != 1:
            raise ArgumentIndexError(self, argindex)
        arg, level = self.args
        if level.is_Integer and level >= 0:
            lv = int(level)
            return Mul(*[1 / IterLog(arg, Integer(k)) for k in range(lv)])
        k = Dummy("k", integer=True, nonnegative=True)
        return Product(1 / IterLog(arg, k), (k, 0, level - 1))

    # -- printing -----------------------------------------------------------
    def _latex(self, printer, exp=None, **kwargs):
        arg, level = self.args
        base = r"\log^{\circ %s}\!\left(%s\right)" % (
            printer._print(level), printer._print(arg)
        )
        if exp is not None:
            return r"\left(%s\right)^{%s}" % (base, exp)
        return base

    def _sympystr(self, printer, *args, **kwargs):
        arg, level = self.args
        return "log^o%s(%s)" % (printer._print(level), printer._print(arg))

    def _pretty(self, printer, *args, **kwargs):
        return _pretty_iterated(printer, "log", self.args)


def _pretty_iterated(printer, head, args):
    """Render ``head^{∘level}(arg)`` as a pretty (Unicode) form."""
    from sympy.printing.pretty.stringpict import prettyForm

    arg, level = args
    circ = prettyForm("\N{RING OPERATOR}")
    sup = prettyForm(*circ.right(printer._print(level)))
    func = prettyForm(head) ** sup
    parg = prettyForm(*printer._print(arg).parens())
    return prettyForm(*func.right(parg))


# ---------------------------------------------------------------------------
# Formula wrapper
# ---------------------------------------------------------------------------
class Formula:
    """A SymPy expression with multi-format rendering and a numeric bridge.

    A :class:`Formula` is an immutable wrapper around a SymPy expression. It is
    the common return type of the symbolic generators in this package and gives
    uniform access to the four requested output formats:

    * ``formula.expr``      -- the native, manipulable SymPy object;
    * ``formula.latex()``   -- a LaTeX string;
    * ``formula.unicode()`` / ``formula.text()`` -- console-friendly strings;
    * ``formula.evalf()`` / ``formula.lambdify()`` -- mpmath numeric evaluation.

    Manipulation helpers (:meth:`subs`, :meth:`diff`, :meth:`simplify`,
    :meth:`expand_levels`) return new :class:`Formula` instances so chaining is
    natural and the original is never mutated.
    """

    def __init__(self, expr, name: Optional[str] = None,
                 description: Optional[str] = None):
        self.expr = sympify(expr)
        self.name = name
        self.description = description

    # -- output formats -----------------------------------------------------
    def latex(self, **kwargs) -> str:
        """Return the LaTeX representation (``sympy.latex``)."""
        return latex(self.expr, **kwargs)

    def text(self) -> str:
        """Return a flat ASCII string (``sympy.sstr``)."""
        return sstr(self.expr)

    def unicode(self) -> str:
        """Return a 2D Unicode rendering (``sympy.pretty``).

        Falls back to the flat ASCII form if the pretty printer cannot render
        a custom operator on the current SymPy version.
        """
        try:
            return pretty(self.expr, use_unicode=True)
        except Exception:
            return self.text()

    def __str__(self) -> str:
        return self.unicode()

    def __repr__(self) -> str:
        label = f" {self.name!r}" if self.name else ""
        return f"<Formula{label}: {self.text()}>"

    def _repr_latex_(self) -> str:
        # Jupyter / IPython rich display.
        return f"${self.latex()}$"

    # -- manipulation -------------------------------------------------------
    def subs(self, *args, **kwargs) -> "Formula":
        """Substitute symbols, returning a new :class:`Formula`."""
        return Formula(self.expr.subs(*args, **kwargs), self.name)

    def diff(self, *symbols) -> "Formula":
        """Differentiate, returning a new :class:`Formula`."""
        return Formula(sp.diff(self.expr, *symbols), self.name)

    def simplify(self, **kwargs) -> "Formula":
        """Simplify, returning a new :class:`Formula`."""
        return Formula(simplify(self.expr, **kwargs), self.name)

    def expand_levels(self) -> "Formula":
        """Expand all iterated operators to native nested ``exp``/``log``.

        Concrete non-negative integer levels become ordinary SymPy
        expressions; symbolic levels are left untouched.
        """
        return Formula(self.expr.doit(), self.name)

    @property
    def free_symbols(self):
        return self.expr.free_symbols

    # -- numeric bridge -----------------------------------------------------
    def lambdify(self, args: Union[Symbol, Sequence[Symbol]],
                 modules: str = "mpmath"):
        """Compile the (level-expanded) formula into a numeric callable.

        Args:
            args: Symbol or ordered sequence of symbols forming the signature.
            modules: SymPy ``lambdify`` backend (default ``"mpmath"`` for
                arbitrary precision).

        Returns:
            A Python callable evaluating the formula numerically.
        """
        return sp.lambdify(args, self.expand_levels().expr, modules=modules)

    def evalf(self, subs: Optional[Mapping] = None, dps: int = 30):
        """Numerically evaluate the formula with mpmath precision.

        Iterated operators are expanded first, then any substitutions are
        applied, then ``evalf`` (which is mpmath-backed) is called.

        Args:
            subs: Mapping of symbols to numeric values.
            dps: Decimal precision (mpmath ``dps``).

        Returns:
            A SymPy ``Float``/``ComplexFloat`` (or unevaluated expression if
            free symbols remain).
        """
        expr = self.expand_levels().expr
        if subs:
            expr = expr.subs(subs)
        return expr.evalf(dps)

    # -- comparison ---------------------------------------------------------
    def equals(self, other: Union["Formula", "sp.Expr"]) -> Optional[bool]:
        """Test symbolic equality (``True``/``False``/``None`` if unknown)."""
        other_expr = other.expr if isinstance(other, Formula) else sympify(other)
        return self.expr.equals(other_expr)
