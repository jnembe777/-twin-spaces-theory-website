"""
Twin-spaces generator (arithmetics.symbolic.twin).

Builds on the symbolic formula generator to realise the construction of
Vol. 01 *Twin Spaces: Foundations*. From three primitives — a base space
``(E, ⊙_e)``, a group ``G`` acting on ``E``, and the transport formula
``x ⊙_{eg} y = g⁻¹·((g·x) ⊙_e (g·y))`` — it generates and classifies new
("twin") spaces.

Layers:

* **actions** — group actions: monogenic ``⟨φ⟩`` (:class:`BijectionAction`),
  one-parameter Lie groups (:class:`ContinuousAction`), finite permutation
  groups (:class:`PermutationAction`).
* **transport** — the transport primitive: :func:`twin_operation`,
  :func:`twin_field`, :func:`twin_operation_continuous`,
  :func:`transport_table`, and :class:`CayleyTable`.
* **classify** — :func:`structural_kernel`, :func:`operation_space`,
  :func:`classify`, :func:`count_invariant_magmas`, :func:`order_complexity`.
* **catalog** — candidate groups & spaces and the discovery runners
  :func:`discover_finite` / :func:`discover_symbolic`, with rendering/export.

Quick start::

    from arithmetics.symbolic.twin import BijectionAction, twin_operation
    phi = BijectionAction.exponential()
    print(twin_operation(phi, level=-1, base="add").text())   # -> x*y
"""

from arithmetics.symbolic.twin.actions import (
    BijectionAction, ContinuousAction, PermutationAction,
)
from arithmetics.symbolic.twin.transport import (
    CayleyTable, twin_operation, twin_field,
    twin_operation_continuous, transport_table,
)
from arithmetics.symbolic.twin.classify import (
    structural_kernel, operation_space, classify,
    count_invariant_magmas, order_complexity,
)
from arithmetics.symbolic.twin.catalog import (
    candidate_finite_groups, candidate_base_operations,
    candidate_bijections, candidate_continuous,
    discover_finite, discover_symbolic,
    render_table, to_latex_table, save_results,
)
from arithmetics.symbolic.twin.lie import (
    LinearAction, Operation,
    twin_operation_so2, kernel_so2, kernel_profile, discover_lie,
)
from arithmetics.symbolic.twin.decision import (
    FiniteGroup, class_equation, is_class_function, decision_report,
    class_average, normalizer, operation_orbits, twin_decision,
    su2_weyl_density, su2_class_average, su2_class_decision,
)
from arithmetics.symbolic.twin.primary import (
    prime_factorization, euler_phi,
    primary_components, primary_projection, op_primary_components,
    operation_factorization, verify_primary_decomposition, primary_decision,
    complexity_classes, verify_complexity_partition, twin_primary_decomposition,
)
from arithmetics.symbolic.twin.tasks import (
    Bijection, TransformedTotal, total_error, dynamic_range, recommend_domain,
    op_count, linearization_rmse, optimal_base, arithmetic_task_report,
)
from arithmetics.symbolic.twin.qudit import (
    sample_unitary, eigenphases, weyl_density, weyl_average,
    schur_character, character_inner_product, verify_character_orthonormality,
    qudit_class_decision, qudit_universality,
)
from arithmetics.symbolic.twin.analysis import (
    quasi_arithmetic_mean, power_mean, geometric_mean, harmonic_mean,
    power_mean_curve, verify_power_mean_inequality,
    mgf, empirical_tail, markov_bound, polynomial_markov_bound,
    chernoff_bound, best_phi_bound, mgf_factorizes,
    additive_defect, homomorphism_add_mul_defect, invariance_report,
    homomorphism_signature, affine_twisted_prime, affine_twisted_primes,
    verify_affine_prime_formula,
    discover_homomorphism_types, discover_twin_primes,
    twin_prime_spectrum,
)
from arithmetics.symbolic.twin.multiplicative import (
    twisted_unit, ap_is_closed, ap_monoid, ap_primes,
    factorizations, num_factorizations, find_non_unique_factorization,
    is_unique_factorization, corrected_twisted_primes,
    progression_zeta, progression_zeta_closed, euler_product, euler_defect,
    compare_to_repo_twisted_primes,
)

__all__ = [
    # actions
    "BijectionAction", "ContinuousAction", "PermutationAction",
    # transport
    "CayleyTable", "twin_operation", "twin_field",
    "twin_operation_continuous", "transport_table",
    # classify
    "structural_kernel", "operation_space", "classify",
    "count_invariant_magmas", "order_complexity",
    # catalog
    "candidate_finite_groups", "candidate_base_operations",
    "candidate_bijections", "candidate_continuous",
    "discover_finite", "discover_symbolic",
    "render_table", "to_latex_table", "save_results",
    # compact Lie groups
    "LinearAction", "Operation",
    "twin_operation_so2", "kernel_so2", "kernel_profile", "discover_lie",
    # decision layer
    "FiniteGroup", "class_equation", "is_class_function", "decision_report",
    "class_average", "normalizer", "operation_orbits", "twin_decision",
    "su2_weyl_density", "su2_class_average", "su2_class_decision",
    # primary decomposition (abelian)
    "prime_factorization", "euler_phi",
    "primary_components", "primary_projection", "op_primary_components",
    "operation_factorization", "verify_primary_decomposition", "primary_decision",
    "complexity_classes", "verify_complexity_partition",
    "twin_primary_decomposition",
    # arithmetic-task costs
    "Bijection", "TransformedTotal", "total_error", "dynamic_range",
    "recommend_domain", "op_count", "linearization_rmse", "optimal_base",
    "arithmetic_task_report",
    # qudits: SU(n) Weyl integration
    "sample_unitary", "eigenphases", "weyl_density", "weyl_average",
    "schur_character", "character_inner_product",
    "verify_character_orthonormality", "qudit_class_decision",
    "qudit_universality",
    # analytic layer: means, concentration, invariance, twisted primes
    "quasi_arithmetic_mean", "power_mean", "geometric_mean", "harmonic_mean",
    "power_mean_curve", "verify_power_mean_inequality",
    "mgf", "empirical_tail", "markov_bound", "polynomial_markov_bound",
    "chernoff_bound", "best_phi_bound", "mgf_factorizes",
    "additive_defect", "homomorphism_add_mul_defect", "invariance_report",
    "homomorphism_signature", "affine_twisted_prime", "affine_twisted_primes",
    "verify_affine_prime_formula",
    "discover_homomorphism_types", "discover_twin_primes",
    "twin_prime_spectrum",
    # multiplicative pillar: Hilbert monoids, twisted zeta
    "twisted_unit", "ap_is_closed", "ap_monoid", "ap_primes",
    "factorizations", "num_factorizations", "find_non_unique_factorization",
    "is_unique_factorization", "corrected_twisted_primes",
    "progression_zeta", "progression_zeta_closed", "euler_product", "euler_defect",
    "compare_to_repo_twisted_primes",
]
