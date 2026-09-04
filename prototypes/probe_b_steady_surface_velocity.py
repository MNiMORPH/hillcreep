"""Probe B -- is the surface creep velocity a free parameter?

Settles: whether the demo has a second lesson beyond "D = K * H_star", and
therefore whether the velocity panel is worth its space.

Claim: at steady state the surface velocity is NOT set by K.  Mass balance
over the upslope half requires every grain eroded above a point to pass it, so
the depth-integrated flux at distance x' from the divide is q = E * x'.  With
q = u_s * H_star (no bedrock),

    u_s(x') = E * x' / H_star          <- linear in x', and K does not appear

Checked below against the independent route: the steady parabola gives S(x),
and u_s = K * S(x).  The two must agree for every K.

Run:  python3 prototypes/probe_b_steady_surface_velocity.py
"""
import numpy as np

L, E = 100., 0.05e-3          # hillslope width [m], incision rate [m/yr]

print("Two independent routes to steady surface velocity, at H_star = 0.5 m.")
print("Route 1: u_s = K * S(x), S from the steady parabola z = E x (L-x) / 2D.")
print("Route 2: u_s = E * x' / H_star, x' = distance from divide.  No K in it.")
print()
H_star = 0.5
x = np.linspace(0., L, 11)
xprime = np.abs(x - L / 2.)                  # distance from the divide
for K in (0.005, 0.02, 0.08):
    D = K * H_star
    S = np.abs(E / (2. * D) * (L - 2. * x))  # |dz/dx| of the steady parabola
    route1 = K * S
    route2 = E * xprime / H_star
    print("  K=%.3f  D=%.5f  max|route1 - route2| = %.3e m/yr   agree: %s"
          % (K, D, np.max(np.abs(route1 - route2)), np.allclose(route1, route2)))

print()
print("So K sets how STEEP the hill must be to carry the flux; H_star sets how")
print("FAST the surface moves.  u_s at the toe (x' = L/2) = E*L/(2*H_star):")
for H_star in (0.25, 0.5, 1.0, 2.0):
    print("  H_star=%.2f m -> u_s(toe) = %6.2f mm/yr"
          % (H_star, E * L / (2. * H_star) * 1e3))
