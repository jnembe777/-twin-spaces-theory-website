# `arithmetics.symbolic.twin` — Twin-Spaces Generator

Realises the construction of **Vol. 01 _Twin Spaces: Foundations_** on top of
the symbolic formula generator. From three primitives it generates and
classifies new ("twin") spaces:

1. a **base space** `(E, ⊙_e)` — a set with a binary operation,
2. a **group** `G` acting on `E`,
3. the **transport formula**  `x ⊙_{eg} y = g⁻¹·((g·x) ⊙_e (g·y))`.

## The three action families

| Family | Class | Example |
|--------|-------|---------|
| Monogenic `G = ⟨φ⟩ ≅ ℤ` (bijection, iterated) | `BijectionAction` | `exp`, `xᵖ`, `logit`, affine |
| One-parameter **Lie** group | `ContinuousAction` | `(ℝ,+)` scaling/translation, `(ℝ₊,×)` power |
| Finite group of permutations | `PermutationAction` | `Cₙ`, `Sₙ`, `Dₙ`, `V₄` |
| **Compact Lie** group acting linearly/unitarily | `LinearAction` (`lie.py`) | `SO(2)`, `SO(3)`, `SU(2)` |

## Quick start

```python
from arithmetics.symbolic.twin import BijectionAction, twin_operation, twin_field

phi = BijectionAction.exponential()
twin_operation(phi, -1, "add").text()   # 'x*y'   (multiplication = twin of +)
twin_operation(phi,  1, "add").text()   # 'log(exp(x) + exp(y))'  (log-sum-exp)
twin_field(phi, -1)["one"].text()       # 'E'     (multiplicative neutral)
```

```python
from arithmetics.symbolic.twin import PermutationAction, classify, candidate_base_operations
C3 = PermutationAction.cyclic(3)
add = candidate_base_operations(3)[0]
classify(add, C3)        # {'index_[G:L]': 3, 'num_twin_ops': 3, 'trivial': False, ...}
```

See `twin_demo.py` at the repository root for the full discovery run.

## The machinery

- **transport** — `twin_operation` (symbolic), `twin_operation_continuous`
  (Lie), `transport_table` (finite `CayleyTable`), `twin_field` (`⊕_g, ⊗_g`
  + neutrals).
- **classify** — `structural_kernel` (`L`), `operation_space`, `classify`
  (`|Op| = [G:L]`, triviality), `count_invariant_magmas`
  (`∏_O |Fix_E(Stab_G(O))|`), `order_complexity` (`ord(gL)`).
- **catalog** — `candidate_finite_groups`, `candidate_base_operations`,
  `candidate_bijections`, `candidate_continuous`; discovery runners
  `discover_finite` / `discover_symbolic`; rendering (`render_table`,
  `to_latex_table`) and export (`save_results` → `results/twin/`).

## What it discovers

- **Linearity obstruction** — twins are trivial (`L = G`) iff every `g` is an
  automorphism of `(E, ⊙_e)`: e.g. `xᵖ` over `·` stays `·`; left-projection is
  rigid under any permutation group.
- **Exponential hierarchy** — `+ → · → x^{ln y} → …` as the level varies.
- **Counting** — `Cₙ → nⁿ` invariant magmas, `Sₙ (n≥4) → 2`, matching the
  foundations theorems.
- **Coherence invariant** — `num_twin_ops == [G:L]` on every (group, space)
  pair (the Fundamental Classification Theorem, verified numerically).

## Compact Lie groups (`lie.py`)

Quantum twin operations `ψ₁ ⊙_{eg} ψ₂ = U_g†(U_gψ₁ ⊙_e U_gψ₂)` for a compact
Lie group acting by unitaries. The **linearity obstruction generalises**:

```python
from arithmetics.symbolic.twin import (
    LinearAction, Operation, twin_operation_so2, kernel_so2, kernel_profile,
)

kernel_so2(Operation.addition(2, "R"))            # rigid: L = SO(2)
kernel_so2(Operation.complex_multiplication())    # L = {0}, Op ≅ SO(2) ≅ S¹

# SU(2) quantum universality: a generic qubit gate has trivial kernel.
kernel_profile(Operation.random_gate(2, seed=1), LinearAction.SU2())
#   -> kernel_trivial=True  ⇒  Op ≅ SU(2) ≅ S³
```

| Group | Operation | Result |
|-------|-----------|--------|
| `SO(2)` | addition | rigid (`L = SO(2)`) |
| `SO(2)` | complex mult. | `Op ≅ SO(2) ≅ S¹` |
| `SO(3)` | cross product | rigid (rotations preserve `×`) |
| `SU(2)` | addition | rigid (linearity obstruction) |
| `SU(2)` | generic gate | `Op ≅ SU(2) ≅ S³` (quantum universality) |

`run discover_lie()` (and `twin_demo.py`) regenerates this table; exact
analysis for the one-parameter `SO(2)`, Monte-Carlo kernel estimation on the
group manifold for `SO(3)` / `SU(2)`.

## Decision layer (`decision.py`)

Group-theoretic discrimination for the operation space, formalised in
`twin_decision_theory.tex`. Turns conjugacy structure into a decision tool.

```python
from arithmetics.symbolic.twin import (
    FiniteGroup, class_equation, twin_decision, su2_class_decision,
)

class_equation(FiniteGroup.quaternion8())   # '8 = 2 + 2 + 2 + 2'  (5 classes)
twin_decision(base_plus_mod4, PermutationAction.symmetric(4))
#   -> L not normal, Op is a homogeneous space (not a group);
#      12 operations reduce to 5 decision cells (Weyl group N_G(L)/L)
```

Key facts (each proved in the note and verified by a test):

- **Classification (corrected):** `Op ≅ G/L` as a *homogeneous space*,
  `|Op| = [G:L]`; it is a **group iff `L ◁ G`**. Counterexample: `S₄` on
  `+ mod 4` has a non-normal order-2 kernel — a correction to the foundations
  volume, found by the tool.
- **Reduction:** a class-function cost is constant on conjugacy classes, so the
  **class equation `|G| = |Z| + Σ [G:C(xᵢ)]` enumerates the decision cells**;
  in general the cells are the orbits of the normalizer `N_G(L)` (Burnside).
- **Stratification:** centre = robust/canonical choices; large class = generic;
  small class = highly symmetric.
- **Compact Lie:** the class equation becomes the **Weyl integration formula**;
  `SU(2)` uses the measure `(2/π) sin²θ` on `θ ∈ [0, π]`.

### Primary decomposition (`primary.py`, abelian `G`)

For abelian `G`, `L` is normal and `Op = G/L` factors along its Sylow-`p`
components — the **CRT/Fourier of operations**:

```python
from arithmetics.symbolic.twin import verify_primary_decomposition, FiniteGroup
verify_primary_decomposition(FiniteGroup.cyclic(12), [0, 6])
#   Op = G/L ≅ Op_2 × Op_3  (orders 2 × 3 = 6 = [G:L]),  L = ∏ L_p,  valid
```

- `G ≅ ∏ G_p`, `L = ∏ L_p` (automatic), `Op ≅ ∏ Op_p` (`Op_p = G_p/L_p`).
- **Unique factorisation** of each operation into `p`-primary parts.
- **Separable decision**: an additive cost is optimised componentwise, search
  `∏|Op_p| → Σ|Op_p|`.
- **Order-complexity partition** `|C_d| = φ(d)·m_d`, `Σ_{d|n}|C_d| = n`.

### Arithmetic-task costs (`tasks.py`)

Makes the cost *operational*: the group element of `⟨φ⟩` is the **computational
domain**, chosen by measurement.

```python
from arithmetics.symbolic.twin import arithmetic_task_report, optimal_base
import random
probs = [10 ** random.uniform(-9, -1) for _ in range(800)]
r = arithmetic_task_report(probs)
#   error_original_domain   = inf      (∏ underflows -> log(0))
#   error_transformed_domain = 0.0     (Σ log, stable)  -> recommend 'transformed'

optimal_base(xs, ys)["optimal_base"]   # 'loglog' for a power law, etc.
```

- **Domain of computation** (fixed target `T = Σ φ(xᵢ)`): transformed vs
  original domain, cost = relative error vs high-precision (`total_error`,
  `recommend_domain`) — the log-domain trick, measured.
- **Optimal base** (representation): `optimal_base` / `linearization_rmse`
  select the base that linearises data (power → `loglog`, exp → `semilogy`).
- Honest **speed/stability trade-off** in `op_count`.

### Qudits — the `SU(n)` Weyl formula (`qudit.py`)

The `d`-level generalisation of the `SU(2)` instance: the class equation becomes
the **Weyl integration formula**, with eigen-phase density
`(1/n!(2π)ⁿ) ∏_{j<k}|e^{iθⱼ}−e^{iθₖ}|²` (the CUE density).

```python
from arithmetics.symbolic.twin import (
    weyl_average, verify_character_orthonormality, qudit_universality,
)
import numpy as np
weyl_average(lambda th: abs(np.sum(np.exp(1j*th)))**2, 3)   # E|tr U|² ≈ 1
verify_character_orthonormality(3, [[0,0,0],[1,0,0],[1,1,0]])["orthonormal"]  # True
qudit_universality(3)["Op"]                                  # 'SU(3)'  (trivial kernel)
```

- **Weyl measure** verified by **Schur-character orthonormality**
  `⟨χ_λ,χ_μ⟩ = δ_{λμ}` (the relation that pins down the measure) and the CUE
  moments `E[tr U]=0`, `E|tr U|²=1`.
- **Decision** over qudit gate classes via `qudit_class_decision` (Weyl average
  + optimum over the torus).
- **Universality persists**: a generic gate on `ℂ^d` has trivial kernel, so
  `Op ≅ SU(d)` for every `d` (Monte-Carlo verified for `d = 2,3,4`).

### Analytic layer (`analysis.py`) — invariants vs non-invariants

Tools that turn the "relabeling" into genuine mathematics by crossing invariant
algebra with non-invariant analysis (metric, measure, order, a second
operation). Computed discoveries (each pinned by a test):

```python
from arithmetics.symbolic.twin import (
    power_mean, verify_power_mean_inequality, invariance_report,
    best_phi_bound, twin_prime_spectrum,
)
```

- **Quasi-arithmetic (Kolmogorov–Nagumo) means**: `power_mean`, with the
  power-mean inequality `M_p ≤ M_q` (AM–GM–HM) — invariant identities compared
  across frames.
- **Invariance boundary** `invariance_report`: which structure a bijection
  preserves. Discovery: **`exp` is the unique additive→multiplicative
  homomorphism** (`φ(x+y)=φ(x)φ(y)`), which is *why* the MGF factorizes sums and
  Chernoff works — while `exp` distorts the metric (non-invariant).
- **φ-concentration** `best_phi_bound`: the generalized Markov/Chernoff bound
  with **tail-adaptive base selection** — light tails pick `e^{tx}` (Chernoff),
  heavy tails pick `x^k` (polynomial Markov). `mgf_factorizes` checks the twin
  identity `MGF_{X+Y}=MGF_X·MGF_Y`.
- **Twisted primes** `twin_prime_spectrum`: primality is **not invariant** —
  identity/`x²` give the classical primes, `2^n` collapses to `{2,3}` (the
  product becomes addition), and `2n+1` yields a new dense set governed by the
  factorization of `2n+1`.

Two deeper discoveries (`discover_homomorphism_types`, `discover_twin_primes`,
`verify_affine_prime_formula`):

- **The four productive frames.** `homomorphism_signature` classifies a
  bijection by which homomorphism it realizes, and the sweep finds exactly four
  coherent types, each tied to an application — `+→+` (linear, rigid), `+→×`
  (`exp`: concentration), `×→+` (`log`: entropy/log-domain), `×→×` (powers:
  classical primes) — everything else being *generic* (new arithmetic).
- **Closed form for affine primes.** `n` is `affine(c,d)`-twisted-prime ⇔
  `cn+d` has no factorization `(cα+d)(cβ+d)` with `α,β≥2`; verified against the
  brute-force `twisted_primes` for several `(c,d)`.

### The multiplicative pillar (`multiplicative.py`) — Hilbert monoids & twisted zeta

Deepening the `×→×` frame toward the twisted zeta. The twin product is always
conjugate to `×`, so the twisted arithmetic is a multiplicative monoid; for an
affine generator it is the monoid of an arithmetic progression (a **Hilbert
monoid**). A decisive correction: **the twin unit is `φ⁻¹(1) = (1−d)/c`, not
`1`** (the repo's `is_twisted_prime` uses `1`, counting spurious primes).

```python
from arithmetics.symbolic.twin import (
    corrected_twisted_primes, find_non_unique_factorization, euler_defect,
)
corrected_twisted_primes(2, 1, 30)           # {n : 2n+1 prime}
find_non_unique_factorization(3, 1, 150)     # 100 = 4*25 = 10*10  (n=33)
euler_defect(3, 1, 2.0, 300)                 # > 0: the Euler product breaks
```

- `(2,1)` = odds → unique factorization, primes = odd primes, corrected
  twisted primes `{n : 2n+1 prime}` (Sophie-Germain-flavoured).
- `(3,1)`, `(4,1)` = Hilbert monoids → **non-unique factorization**
  (`100=4·25=10·10`; `441=9·49=21·21`), the classical failure of UFD in a
  residue class.
- `euler_defect = Σ (r(m)−1) m^{−s}` measures the twisted-zeta Euler-product
  overcount; zero iff factorization is unique.

This connects the twin framework to **primes in arithmetic progressions and
Dirichlet L-functions**, and locates where genuinely new zeta functions live:
not in a single coherent frame (relabeled `ζ`) but across frames (the level-`p`
`ζ_p`, where the defect is non-zero).
