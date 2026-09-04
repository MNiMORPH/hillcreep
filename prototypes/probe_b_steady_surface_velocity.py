"""Probe B -- is the surface creep velocity a free parameter?

Settles: whether the demo has a second lesson beyond "D = k_u * dz_u", and
therefore whether the velocity panel is worth its space.

Claim: at steady state the surface velocity is NOT set by k_u.  Mass balance
over the upslope half requires every grain eroded above a point to pass it, so
the depth-integrated flux at distance x' from the divide is q = E * x'.  With
q = u_s * dz_u (no bedrock),

    u_s(x') = E * x' / dz_u          <- linear in x', and k_u does not appear

Checked below against the independent route: the steady parabola gives S(x),
and u_s = k_u * S(x).  The two must agree for every k_u.

Run:  python3 prototypes/probe_b_steady_surface_velocity.py
"""
import numpy as np

L, E = 100., 0.01e-3          # hillslope width [m], incision rate [m/yr]

print("Two independent routes to steady surface velocity, at dz_u = 0.5 m.")
print("Route 1: u_s = k_u * S(x), S from the steady parabola z = E x (L-x) / 2D.")
print("Route 2: u_s = E * x' / dz_u, x' = distance from divide.  No k_u in it.")
print()
dz_u = 0.5
x = np.linspace(0., L, 11)
xprime = np.abs(x - L / 2.)                  # distance from the divide
for k_u in (0.005, 0.02, 0.08):
    D = k_u * dz_u
    S = np.abs(E / (2. * D) * (L - 2. * x))  # |dz/dx| of the steady parabola
    route1 = k_u * S
    route2 = E * xprime / dz_u
    print("  k_u=%.3f  D=%.5f  max|route1 - route2| = %.3e m/yr   agree: %s"
          % (k_u, D, np.max(np.abs(route1 - route2)), np.allclose(route1, route2)))

print()
print("So k_u sets how STEEP the hill must be to carry the flux; dz_u sets how")
print("FAST the surface moves.  u_s at the toe (x' = L/2) = E*L/(2*dz_u):")
for dz_u in (0.25, 0.5, 1.0, 2.0):
    print("  dz_u=%.2f m -> u_s(toe) = %6.2f mm/yr"
          % (dz_u, E * L / (2. * dz_u) * 1e3))
