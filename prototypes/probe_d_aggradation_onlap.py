"""Probe D -- does flooding a level set actually shorten the hillslope?

Settles: whether onlap can be implemented entirely inside apply_boundaries(),
and what it does to the hillslope that survives.

The algorithm, as specified: the alluvial surface is a level set -- one flat
elevation z_river.  Flooding it means raising z_river, finding every node the
sediment has drowned, setting those nodes to z_river and dropping them from the
active mask.  The hillslope's boundary is then the shallowest still-active
node, and the hillslope is *shorter*.

Two questions this probe answers before any of it is written into the model:

1. Does the exposed hillslope shorten as the rivers rise, and by how much?
2. When base level falls again, do buried nodes re-emerge -- and at what
   elevation?  They were set to the fill surface, so they should come back as
   a fill terrace that then decays diffusively, not as the original hillslope.

Run:  python3 prototypes/probe_d_aggradation_onlap.py
"""
import numpy as np

L, NX = 100.0, 101
DX = L / (NX - 1)
K_U, DZ_U = 0.02, 0.5
K_HS = K_U * DZ_U
DT = 2.5


def flood(z, bed):
    """The proposed algorithm, standalone: returns (z, active)."""
    z = z.copy()
    active = np.ones(z.size, dtype=bool)
    active[0] = active[-1] = False
    z[0] = z[-1] = bed
    i = 1
    while i < z.size - 1 and z[i] < bed:
        z[i] = bed
        active[i] = False
        i += 1
    j = z.size - 2
    while j > 0 and z[j] < bed:
        z[j] = bed
        active[j] = False
        j -= 1
    return z, active


def exposed_length(active):
    idx = np.flatnonzero(active)
    return 0.0 if idx.size == 0 else (idx[-1] - idx[0] + 2) * DX


x = np.linspace(0.0, L, NX)
# Start from the steady parabola for E = 0.05 mm/yr: crest 6.25 m.
edot = 0.05e-3
z0 = edot / (2.0 * K_HS) * x * (L - x)

print("(1) Raise a flat sediment surface through a steady hillslope.")
print("    crest = %.2f m" % z0.max())
print("     bed [m]   exposed length [m]   buried nodes   crest above fill [m]")
for bed in (0.0, 0.5, 1.0, 2.0, 4.0, 6.0, 6.3):
    z, active = flood(z0, bed)
    print("     %6.2f   %12.1f   %12d   %14.2f"
          % (bed, exposed_length(active), (~active).sum() - 2, z.max() - bed))

print()
print("(2) With the fill level held, the shortened hillslope decays to it.")
print("    There is no steady form while a river aggrades -- base level is")
print("    rising -- so the only check available is the E = 0 one: hold the")
print("    level and the exposed hill should flatten onto it.")
z, active = flood(z0, 2.0)
idx = np.flatnonzero(active)
xl, xr = x[idx[0] - 1], x[idx[-1] + 1]
print("    exposed span %.1f to %.1f m (length %.1f m), crest %.2f m above fill"
      % (xl, xr, xr - xl, z.max() - 2.0))
for step in range(400000):
    q_m = -K_HS * np.diff(z) / DX
    z[1:-1] += DT * np.where(active[1:-1], -np.diff(q_m) / DX, 0.0)
    z, active = flood(z, 2.0)
print("    after 1 Myr at that level: crest %.4f m above fill" % (z.max() - 2.0))

print()
print("(3) Re-emergence: bury to 3 m, then drop the level back to 0.")
z, active = flood(z0, 3.0)
buried = int((~active).sum() - 2)
z_back, active_back = flood(z, 0.0)
print("    buried %d nodes at bed = 3 m; after dropping to 0 m, %d are active"
      % (buried, active_back.sum()))
print("    the re-exposed toe comes back at the FILL elevation, not the")
print("    original hillslope:  z[1] = %.3f m (was %.3f m before flooding)"
      % (z_back[1], z0[1]))
print("    -> the fill is left as a terrace and then decays diffusively,")
print("       which is what depositing sediment and removing base level does.")
