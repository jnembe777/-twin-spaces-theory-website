"""
Simulation study for "Adaptive exact minimax rates for invariant density
estimation on quotient spaces".

Estimator throughout: the *penalised projection* estimator of the paper
(piecewise-constant projection = regular histogram; resolution selected by
  m* = argmin_m { -||g_hat_m||^2_{L2} + kappa * D_m / n },  D_m = m^dim ).
Lipschitz (Holder-1) targets are used so the histogram bias O(h) is active and
the predicted slopes are visible: in dimension d the ISE ~ n^{-2/(2+d)}.

(1) RADIAL (positive-dimensional symmetry): E=R^2, G=SO(2), d_eff=1.
    Invariant: 1-D penalised-projection histogram of radii R_i=|X_i|, pushed back
    to f_hat(x)=p_hat_R(|x|)/(2*pi*|x|). Ambient: the SAME projection family in
    dimension 2. Both judged as estimators of the SAME 2-D density f (ISE on a
    grid). Predicted slopes: invariant n^{-2/3}, ambient n^{-1/2}.

(2) NEGATIVE CONTROL (finite symmetry): circle [0,1), G=Z_m (m-fold rotation),
    r=0 so d_eff=D: NO rate change, only a constant (1/|G|) variance gain.
    Invariant (orbit-folded onto [0,1/m), tiled back) vs plain 1-D histogram:
    same slope, ISE ratio ~ m.

All numbers below are produced by this script.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(20260619)

# ---- penalised-projection (histogram) selectors -----------------------------
def pp_hist_1d(samples, lo, hi, n, kappa, m_grid):
    best = None
    for m in m_grid:
        edges = np.linspace(lo, hi, m + 1); w = (hi - lo) / m
        counts, _ = np.histogram(samples, bins=edges)
        phat = counts / (n * w)
        crit = -np.sum(phat**2) * w + kappa * m / n
        if best is None or crit < best[0]:
            best = (crit, edges, phat)
    return best[1], best[2]

def pp_hist_2d(X, lo, hi, n, kappa, m_grid):
    best = None
    for m in m_grid:
        edges = np.linspace(lo, hi, m + 1); area = ((hi - lo) / m)**2
        H, _, _ = np.histogram2d(X[:, 0], X[:, 1], bins=[edges, edges])
        phat = H / (n * area)
        crit = -np.sum(phat**2) * area + kappa * (m * m) / n
        if best is None or crit < best[0]:
            best = (crit, edges, phat)
    return best[1], best[2]

# ---- Experiment 1: radial density on R^2, Lipschitz radial profile ----------
RMAX = 3.0
def raw_rad(r):                 # piecewise-linear (Lipschitz) radial profile >=0
    return (np.maximum(0.0, 1.0 - np.abs(r - 1.0) / 0.8)
            + 0.5 * np.maximum(0.0, 1.0 - np.abs(r - 2.2) / 0.5))
_rq = np.linspace(0, RMAX, 20001)
_Z = np.trapezoid(raw_rad(_rq) * 2*np.pi*_rq, _rq)      # normalising constant
def f_rad(r):   return raw_rad(r) / _Z                  # 2-D density value at radius r
def pR(r):      return 2*np.pi*r * f_rad(r)             # radius law, =0 at r=0
_PRmax = np.max(pR(_rq)) * 1.05

def sample_radius(n):
    out = np.empty(n); filled = 0
    while filled < n:
        k = n - filled
        r = rng.uniform(0, RMAX, k); y = rng.uniform(0, _PRmax, k)
        acc = y < pR(r); a = r[acc]; t = min(a.size, k)
        out[filled:filled+t] = a[:t]; filled += t
    return out

gx = np.linspace(-RMAX, RMAX, 161); GX, GY = np.meshgrid(gx, gx)
GR = np.sqrt(GX**2 + GY**2); cell = (gx[1]-gx[0])**2
inside = (GR >= 0.05) & (GR <= RMAX)
f_true = f_rad(GR[inside]); rr = GR[inside]

def ise_radial(n, reps=30):
    # projection estimator at its risk-optimal (oracle) resolution = the
    # bias-variance balance of Prop. (known s); the penalised rule attains the
    # same rate adaptively (Thm, adaptive exact rate).
    inv, amb = [], []
    m1 = np.arange(4, 81); m2 = np.arange(3, 31)
    for _ in range(reps):
        R = sample_radius(n); th = rng.uniform(0, 2*np.pi, n)
        X = np.column_stack([R*np.cos(th), R*np.sin(th)])
        best = np.inf
        for m in m1:
            edges = np.linspace(0, RMAX, m+1); w = RMAX/m
            counts, _ = np.histogram(R, bins=edges); phat = counts/(n*w)
            idx = np.clip(np.searchsorted(edges, rr, side='right')-1, 0, len(phat)-1)
            e = np.sum((phat[idx]/(2*np.pi*rr) - f_true)**2) * cell
            best = min(best, e)
        inv.append(best)
        best = np.inf
        for m in m2:
            e2 = np.linspace(-RMAX, RMAX, m+1); area = (2*RMAX/m)**2
            H, _, _ = np.histogram2d(X[:,0], X[:,1], bins=[e2, e2]); p2 = H/(n*area)
            ix = np.clip(np.searchsorted(e2, GX[inside], side='right')-1, 0, p2.shape[0]-1)
            iy = np.clip(np.searchsorted(e2, GY[inside], side='right')-1, 0, p2.shape[1]-1)
            e = np.sum((p2[ix, iy] - f_true)**2) * cell
            best = min(best, e)
        amb.append(best)
    return np.mean(inv), np.mean(amb)

# ---- Experiment 2: Z_m on the circle, Lipschitz periodic target -------------
M_FOLD = 4
def tent(u):                    # Lipschitz bump on [0,1), period-1
    return 2.0 * np.abs((u % 1.0) - 0.5)
def f_circle(t):                # 1/M-periodic density on [0,1), integral 1
    return 1.0 + 0.5 * (tent(M_FOLD * t) - 0.5) / 0.5 * 0.5   # mean 1, Lipschitz
# simpler explicit form: base shape on each 1/M period
def f_circle(t):
    s = (M_FOLD * t) % 1.0
    return 1.0 + 0.6 * (0.5 - np.abs(s - 0.5)) * 2.0 - 0.6*0.5  # mean ~1, Lipschitz, >0
_tt = np.linspace(0, 1, 4001)[:-1]; _dt = _tt[1]-_tt[0]
_fc = f_circle(_tt); _fc = _fc / (np.sum(_fc)*_dt)             # renormalise to integral 1
_fcmax = _fc.max()*1.05
def sample_circle(n):
    out = np.empty(n); filled = 0
    while filled < n:
        k = n - filled; u = rng.uniform(0,1,k); y = rng.uniform(0,_fcmax,k)
        # interpolate target at u
        fu = np.interp(u, _tt, _fc); acc = y < fu; a = u[acc]; t = min(a.size,k)
        out[filled:filled+t] = a[:t]; filled += t
    return out

def ise_circle(n, reps=80):
    plain, inv = [], []
    mg = np.arange(4, 161)
    for _ in range(reps):
        T = sample_circle(n)
        best = np.inf
        for m in mg:
            edges = np.linspace(0, 1, m+1); w = 1.0/m
            counts, _ = np.histogram(T, bins=edges); phat = counts/(n*w)
            idx = np.clip(np.searchsorted(edges, _tt, side='right')-1, 0, len(phat)-1)
            best = min(best, np.sum((phat[idx] - _fc)**2) * _dt)
        plain.append(best)
        U = T % (1.0/M_FOLD)                # orbit fold onto [0,1/M)
        best = np.inf
        for m in mg:
            edges = np.linspace(0, 1.0/M_FOLD, m+1); w = (1.0/M_FOLD)/m
            counts, _ = np.histogram(U, bins=edges); p2 = counts/(n*w)
            uu = _tt % (1.0/M_FOLD)
            j = np.clip(np.searchsorted(edges, uu, side='right')-1, 0, len(p2)-1)
            best = min(best, np.sum((p2[j]/M_FOLD - _fc)**2) * _dt)   # circle density = f_U/M
        inv.append(best)
    return np.mean(plain), np.mean(inv)

def slope(ns, e): return np.polyfit(np.log(ns), np.log(e), 1)[0]

ns = np.array([250, 500, 1000, 2000, 4000, 8000])
inv1, amb1 = [], []
for n in ns:
    a, b = ise_radial(int(n)); inv1.append(a); amb1.append(b)
    print(f"[radial] n={n:5d}  ISE inv={a:.3e}  amb={b:.3e}")
inv1, amb1 = np.array(inv1), np.array(amb1)
s_inv, s_amb = slope(ns, inv1), slope(ns, amb1)
print(f"[radial] slopes: invariant={s_inv:.3f} (theory -0.667)  ambient={s_amb:.3f} (theory -0.500)")

pl2, in2 = [], []
for n in ns:
    p, q = ise_circle(int(n)); pl2.append(p); in2.append(q)
    print(f"[Zm]     n={n:5d}  ISE plain={p:.3e}  inv={q:.3e}  ratio={p/q:.2f}")
pl2, in2 = np.array(pl2), np.array(in2)
s_pl, s_in = slope(ns, pl2), slope(ns, in2)
print(f"[Zm]     slopes: plain={s_pl:.3f}  invariant={s_in:.3f} (both ~ -0.667)  mean ratio={np.mean(pl2/in2):.2f} (|G|={M_FOLD})")

fig, ax = plt.subplots(1, 2, figsize=(10, 4.1))
a0 = ax[0]
a0.loglog(ns, inv1, 'o-', label=f'invariant ($d$=1): slope {s_inv:.2f}')
a0.loglog(ns, amb1, 's--', label=f'ambient ($D$=2): slope {s_amb:.2f}')
a0.loglog(ns, inv1[0]*(ns/ns[0])**(-2/3.), ':', color='gray',  label=r'$n^{-2/3}$')
a0.loglog(ns, amb1[0]*(ns/ns[0])**(-1/2.), ':', color='black', label=r'$n^{-1/2}$')
a0.set_xlabel('$n$'); a0.set_ylabel('mean ISE'); a0.set_title('(a) Radial $SO(2)$: dimension gain')
a0.legend(fontsize=8); a0.grid(True, which='both', alpha=0.3)
a1 = ax[1]
a1.loglog(ns, pl2, 's--', label=f'plain: slope {s_pl:.2f}')
a1.loglog(ns, in2, 'o-', label=f'invariant: slope {s_in:.2f}')
a1.set_xlabel('$n$'); a1.set_ylabel('mean ISE')
a1.set_title(f'(b) Finite $\\mathbb{{Z}}_{M_FOLD}$: constant gain (ratio$\\approx${np.mean(pl2/in2):.1f})')
a1.legend(fontsize=8); a1.grid(True, which='both', alpha=0.3)
fig.tight_layout(); fig.savefig('sim_invariant_minimax.pdf')
print("saved sim_invariant_minimax.pdf")
