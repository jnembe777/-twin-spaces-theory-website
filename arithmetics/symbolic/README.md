# `arithmetics.symbolic` — Symbolic Formula Generator

A SymPy-backed engine that mirrors the numeric framework
(`arithmetics.core`, `arithmetics.zeta`) **symbolically**. Every generator
returns a `Formula`, a thin wrapper exposing four output formats:

| Format | Accessor | Use |
|--------|----------|-----|
| SymPy object | `.expr` | exact manipulation (`subs`, `diff`, `simplify`) |
| LaTeX | `.latex()` | typesetting for the papers |
| Unicode / ASCII | `.unicode()` / `.text()` | console inspection |
| Numeric | `.evalf()`, `.lambdify()`, `numeric.*` | mpmath evaluation |

## Quick start

```python
from arithmetics.symbolic import exponential_transfer, defect, zeta_p, eval_zeta_p

phi = exponential_transfer(2)            # 2**n
print(defect(phi).latex())               # δ_φ(a,b) in LaTeX
print(zeta_p(2).unicode())               # ζ_2(s), pretty-printed
print(eval_zeta_p(0, 2))                 # numeric: ζ_0(2) = ζ(3)
```

See `symbolic_demo.py` at the repository root for a full tour.

## What it generates

- **Transfers** `φ(n)` — exponential, iterated `exp^{∘p}`, affine, polynomial,
  rational, mixed, coherent-twist, identity (`transfers.py`).
- **Level-p operations** `⊕_p`, `⊗_p`, isomorphism `Φ_p = exp^{∘p}` and its
  inverse, additive/multiplicative identities `0_p`, `1_p` (`operations.py`).
- **Defect cocycle** `δ_φ(a,b) = φ(a)φ(b) − φ(ab)` and the twisted cocycle
  residual, with a structural `is_cocycle` check (`defect.py`).
- **Intrinsic zeta** `ζ_p(s) = Φ_p(Σ (log^{∘p} n)^{−(s+1)})`, the inner
  Dirichlet series `D_p(s)`, and the zero conditions
  `ζ_p(s) = 0_p` ⇔ `D_p(s) = 0` (`zeta.py`).
- **mpmath bridge** to evaluate any formula, and a dedicated `eval_zeta_p`
  summing the inner series with `mpmath.nsum` (`numeric.py`).

## Iterated operators

`IterExp(x, p)` and `IterLog(x, p)` carry the compact `\exp^{\circ p}`
notation but expand to native nested `exp`/`log` for concrete integer levels
via `.doit()` / `Formula.expand_levels()`, so they differentiate and evaluate
like ordinary SymPy objects. Level 0 is the identity; negative levels fold
into the inverse operator; `IterExp(IterLog(x, p), p)` cancels to `x`.
