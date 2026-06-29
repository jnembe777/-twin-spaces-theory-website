# Publication roadmap — twisted-zeta-functions corpus

Triage assessment of the article corpus: tier, genuine contribution, realistic
venue, and the action needed before submission. Built from close reading of
abstracts, theorem statements, and scope/correction remarks (and, for
`agt1_twisted_cohomology` and `invariant_density_minimax`, full proof
verification). This is a triage, **not** a referee report: each Tier-1/2
candidate still needs its proofs checked end-to-end and its novelty positioned
against the literature.

Legend — **Tier 1**: publishable as research (real content, proofs present).
**Tier 2**: publishable as expository / specialized note or monograph, with
honest reframing. **Tier 3**: not publishable as written — decouple the solid
kernel from overclaiming framing, or reframe.
Depth — ✔ proofs verified by us · ◑ triaged (statements + remarks read) · ○ not
yet deep-read.

---

## Tier 1 — publishable as research

| Article | Depth | Genuine contribution | Target venue | Action before submission |
|---|---|---|---|---|
| `invariant_density_minimax` | ✔ | Exact adaptive equivariant minimax rate; projection removes the log; multiplicative extension | EJS / Bernoulli | Done (hardened + sims). Final lit-positioning pass; external proof check |
| `papers/twin_spaces/deformation_cohomology` | ◑ | Hochschild cohomology of twin orbits + explicit computations (cyclic, abelian, compact Lie, GL_n) | J. Algebra | Verify the compact-Lie / GL_n vanishing proofs; position vs Gerstenhaber |
| `papers/twin_spaces/arithmetic_twin_operations` | ◑ | Entropy–index relation h_n = h_0 − n·I(φ;X) (new); monoidal composition product | IEEE Trans. IT / Adv. Appl. Math | Tighten entropy proof; drop prime-factorization repackaging |
| `papers/article_A_discrimination` | ◑ | Op ≅ G/L; group structure iff L normal; **correction** (S_4 counterexample); 131 tests | J. Algebra / J. Group Theory | Drop non-Newtonian framing; make Weyl/Monte-Carlo part rigorous or label exploratory |
| `papers/article_C_invariants` | ◑ | Invariant/non-invariant boundary principle; **Hilbert monoids** from affine twin arithmetic + unit correction (new) | Specialized (number theory / repr.) | Recast boundary principle as a lemma; prove (don't compute) the four-frame classification; drop classical Chernoff |
| `papers/twin_spaces/agt1_twisted_cohomology` | ✔ | Twisted defect 2-cocycle of n↦αⁿ; d²∘d¹=[δ,·]; non-triviality; H²≅ℝ (regular) | **Tier 1−**: Comm. Algebra / JAA / Expositiones (NOT Adv. Math) | Reframe modestly (analogy, not full curved dga); position vs quasimorphism/deviation cocycles; compute non-regular H² |

## Tier 2 — expository / specialized / monograph (with honest reframing)

| Article | Depth | Kernel | Target venue | Action |
|---|---|---|---|---|
| `papers/twin_spaces/cramer_twin_spaces` | ✔ | H²(G,K₀ˣ) obstruction recovering Br(ℝ)/quaternions; Cramer naturality; honest descent caveat | Expositiones Math / Monthly | Frame as "transport viewpoint on Galois descent"; position vs classical twisted forms |
| `papers/twin_spaces/mathematics_through_symmetry` | ◑ | Unification of classical transports; exemplary "what this work is not" | Amer. Math. Monthly / Expositiones | Publish ~as is |
| `papers/twin_spaces/vol01_twin_spaces_foundations` | ◑ | Foundational L\G classification; very honest | Monograph (Springer / CRC) | Editorial only |
| `twin_decision_theory` | ◑ | Corrects classification; class equation as decision cells; Weyl/CRT | Specialized algebra | Thin "decision" content — reframe as operation-classification invariants |
| `papers/twin_spaces/cohomological_schemes` | ◑ | Honest negative result: HH¹ does not detect flexibility | J. Algebra (short note) | Extract the dichotomy + quantum-group caveat |
| `papers/twin_spaces/rigidity_flexibility_quantum` | ◑ | Refined rigidity/flexibility classification (§1) | Specialized (Hopf/category) | Split: publish §1; defer the sketchy quantum part |
| `papers/twin_spaces/twinspaces_2categorical_operadic` | ◑ | Twin 2-category; monoidal structure | JPAA / expository | Demote operadic part to "organizational" |
| `papers/twin_spaces/twin_arithmetic_monogenic_transport` | ◑ | Foundational twin-ring hierarchy; honest non-triviality conditions | Archivum Math / expository | Foundational — merge with a results paper or shorten |
| `papers/twin_spaces/twin_commutative_algebra_geometry` | ◑ | Equivariant AG under twin umbrella; honest RR counterexample | Expositiones / survey | Extract the twin-Riemann–Roch note; drop the Langlands/crypto speculation |
| `papers/twin_spaces/noether_twin_spaces` | ◑ | Classical mechanics in deformed coordinates (transport-trivial but correct) | Niche math-physics / expository | Reframe as "alternative coordinatization", not new conservation laws |
| `papers/article_B_domains` | ◑ | Log-domain/softmax toolkit + HMM benchmark; measurement-driven domain choice | SIAM Review / ACM Surveys (tutorial) | Engineering/pedagogy framing; acknowledge the "two-run" caveat |
| `minimum_complexity_estimation` | ✔ | MCE oracle + near-minimax-vs-exact clarification | Entropy / JSPI | Position as methodological note; novelty is the clarification |
| `mdl_estimation` | ◑ | Unified MDL with explicit per-process Hellinger formulas | Entropy / ESAIM P&S | Position vs per-process literature |
| `orbital_estimation` | ◑ | Glivenko–Cantelli/Donsker on quotients; equivariant KDE/MLE; honest "no spurious gain" | J. Nonparametric Stat / ESAIM P&S / Metrika | Standard reframing |
| `spectral_equivariance_rkhs` | ◑ | Risk invariance under unitary twin transport (clean, one-line core) | Stat. Probab. Lett. / Sankhyā (note) | Short note |
| `concentration_diffeomorphism_corrected` | ◑ | Covariance-transport dictionary; no-free-lunch; tail-free affinity oracle | Stat. Probab. Lett. (note) | Publish as a clarification note |
| `equivariant_statistical_estimation` | ◑ | Treatise; minimax section + projection fix (added this cycle) | Lecture notes / monograph; or extract chapters | Extract the minimax chapter as a paper |
| `statistical_estimation_twin_calculus` | ◑ | Info-geometry unification (MLE/Bayes/natural-gradient) via pullback coordinates; honest "reduces to classical calculus" | Monograph / info-geom (Bernoulli, JMLR) | Too long/incremental as one paper; extract a pullback-metric + constraint-elimination paper |
| `cohomological_categorical_foundations` | ◑ | Hochschild/Gerstenhaber deformation + Mumford GIT + operad applied to twin ops; **exemplary honesty** ("this is Mumford GIT; we use twin terminology") | Specialized algebra (J. Algebra / Alg. Repr. Theory) | Publish ~as is; flesh out the q-group caveat and the Einstein-addition bridge |

## Tier 3 — not publishable as written (decouple / reframe)

| Article | Depth | Problem | Salvage |
|---|---|---|---|
| `papers/twin_spaces/twinspaces_general_complex` | ◑ | Part III (complex spacetime) speculative, HIGH overclaim | Publish **Parts I–II** (Minkowski recovery) separately; Part III → appendix labelled speculative |
| `twin_spaces_general_complex_spacetime` (root) | ◑ | Same as above (root copy) | Same |
| `papers/twin_spaces/twin_paradigm_book` | ◑ | "SM uniquely determined by C1–C4" is a **verification dressed as derivation**; "gauge from relations" is philosophy | Ch. 2 (kernel chain) as a pure-algebra paper, constraints renamed group-theoretically |
| `papers/twin_spaces/quantum_geometry_foundations` | ◑ | "ℏ emerges" — quantization condition is an **axiom smuggled in** | Reframe as "coordinatization of the quantization axioms"; remove "emergence" |
| `papers/twin_spaces/gr_from_orbital_structure` | ◑ | Most defensible physics paper; correct synthesis (Bianchi + Curiel/Navarro–Sancho), excellent honesty | Publishable in Class. Quantum Gravity as **axiomatic clarification** (not a discovery) |
| `papers/twin_spaces/qm_from_orbital_structure` | ◑ | Re-derives Bargmann/Lévy-Leblond; circular (mass = central charge); no new physics | Math-physics expository, retitled honestly |
| `papers/twin_spaces/sr_from_orbital_structure` | ◑ | Reformulates Ignatowski/Souriau; "without Lagrangian" misleading (Hamiltonian is variational); c is a units constant | Math-physics expository; keep rapidity/coadjoint kernels |
| `papers/twin_spaces/relativity_without_lagrangian` | ◑ | Compressed SR+GR; same Hamiltonian-is-variational issue | Merge with gr_/sr_ as one expository piece |
| `papers/twin_spaces/qft_unification_from_orbital_structure` | ◑ | Weinberg's program reworded; "Unifying Observation" admitted post-hoc; OIC unfalsifiable | Not publishable as physics; at most a review "synthesis of Weinberg's program" |
| `tks_physical_interpretation` | ◑ | HIGH overclaim: operator covariance ≠ statistical/Lorentz invariance; gauge mislabel. Solid kernel: kernel transport = pullback + spectral covariance | Reframe as pure math ("Kernel transport as geometric pullback; diffusion semigroups"); drop all physics language |
| `document` (twisted-zeta / cohomology) | ◑ | **Overlaps `agt1`** (same curved cohomology) wrapped in "twisted primes" / ζ_α / RH framing — the RH connection is HIGH-overclaim relabeling (ζ_α is a weighted Dirichlet series with no number-theoretic RH content) | Strip the RH/twisted-prime rhetoric; the publishable kernel **is** `agt1`. Do not submit the RH framing |

## Not for submission (internal)

`bilan_recherche` (self-assessment), `plan_experience`,
`orbital_minimax_invariance_plan`, `orbital_lower_bound_proof`,
`orbital_upper_bound_proof` (now folded into `invariant_density_minimax`).

**Note — `document` ≈ `agt1`.** `document.tex` and `agt1_twisted_cohomology`
share the same curved-cohomology core; `document` adds a Riemann-hypothesis /
twisted-zeta framing that is not substantiated. Consolidate: submit the algebra
once (as the reframed `agt1`), and drop the RH wrapper rather than maintaining two
overlapping papers.

---

## Recommended submission order

1. **`invariant_density_minimax`** → EJS/Bernoulli (ready; final lit pass).
2. **`papers/article_A_discrimination`** → J. Algebra (drop calculus framing).
3. **`papers/twin_spaces/arithmetic_twin_operations`** (entropy–index result) → IEEE IT / AAM.
4. **`papers/twin_spaces/deformation_cohomology`** → J. Algebra.
5. **`papers/article_C_invariants`** (Hilbert-monoid kernel) → specialized.
6. Expository batch (Tier 2): `mathematics_through_symmetry`, `cramer_twin_spaces`, the corrected stats notes.

## Cross-cutting notes

- **Honesty culture is an asset.** The corpus consistently flags its own limits
  (self-corrections, counterexamples, "what this work is not"). This is a
  publishability strength, not a weakness.
- **The recurring limitation is transport-triviality**: much follows from "every
  twin structure is isomorphic to the root". The publishable value lives in
  corrections, unifications, worked examples, and the precise *boundary* where
  triviality stops (article_C makes this explicit).
- **Physics cluster**: decouple the solid group-theoretic kernels from
  "deriving physics" titles. No new predictions; reframe as math-physics
  exposition. `gr_from_orbital_structure` is the most defensible.
- **Dependency chain**: several papers cite forthcoming Nembe (2026) volumes and
  earlier foundations; their standing depends on those being sound.
