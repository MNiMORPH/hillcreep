"""Probe E -- is there a closed form for a diffusing scarp, and is it right?

Settles: whether the scarp demo can carry an analytic check curve, the way the
hillslope demo carries the steady parabola.

The initial form is a ramp: flat at +a, a straight face of slope -a/w between
-w and +w, flat at -a.  Differentiating the diffusion equation shows the
*slope* of that profile is a diffusing rectangular pulse, whose solution is a
difference of error functions; integrating back and fixing the constant with
z(+inf) = -a gives

    beta = 2 sqrt(k_hs t)

    z(x,t) = -(a / 2w) [ (x+w) erf((x+w)/beta) - (x-w) erf((x-w)/beta)
                         + (beta/sqrt(pi)) ( e^-((x+w)/beta)^2
                                           - e^-((x-w)/beta)^2 ) ]

Checked below against an explicit numerical solution of the same equation with
no-flux ends.  If they agree, the demo can draw it and the exercise can use
morphologic dating; if they do not, the derivation is wrong and neither should
be attempted.

Run:  python3 prototypes/probe_e_scarp_analytic.py
"""
import math

import numpy as np

_erf = np.vectorize(math.erf)


def analytic(x, t, a, w, k_hs):
    if t <= 0.0:
        return np.clip(-a * x / w, -a, a)
    beta = 2.0 * math.sqrt(k_hs * t)
    xp, xm = (x + w) / beta, (x - w) / beta
    return -(a / (2.0 * w)) * (
        (x + w) * _erf(xp) - (x - w) * _erf(xm)
        + (beta / math.sqrt(math.pi)) * (np.exp(-xp ** 2) - np.exp(-xm ** 2)))


def numerical(x, t_end, a, w, k_hs, dt):
    dx = x[1] - x[0]
    z = np.clip(-a * x / w, -a, a)
    for _ in range(int(round(t_end / dt))):
        # No flux at either end: mirror the first and last interior nodes.
        zz = np.concatenate(([z[1]], z, [z[-2]]))
        z = z + dt * k_hs * (zz[:-2] - 2.0 * zz[1:-1] + zz[2:]) / dx ** 2
    return z


HEIGHT = 5.0                       # scarp height [m], crest to toe
ANGLE = 30.0                       # initial face angle [degrees]
a = 0.5 * HEIGHT
w = a / math.tan(math.radians(ANGLE))
K_HS = 0.01

x = np.linspace(-120.0, 120.0, 2401)      # dx = 0.1 m
dt = 0.2 * (x[1] - x[0]) ** 2 / K_HS

print("scarp height %.1f m at %.0f deg -> half-height a = %.2f m, half-width "
      "w = %.3f m" % (HEIGHT, ANGLE, a, w))
print("k_hs = %g m2/yr, dx = %.2f m, dt = %.3f yr" % (K_HS, x[1] - x[0], dt))
print()
print("   t [yr]   morphologic age k_hs*t [m2]   max |analytic - numerical| [m]")
for t in (100.0, 1000.0, 5000.0, 20000.0):
    num = numerical(x, t, a, w, K_HS, dt)
    ana = analytic(x, t, a, w, K_HS)
    print("   %7.0f   %20.1f   %28.3e" % (t, K_HS * t, np.max(np.abs(num - ana))))

print()
print("Mass is conserved (no flux out), so the mean must not move:")
z0 = np.clip(-a * x / w, -a, a)
for t in (0.0, 1000.0, 20000.0):
    z = numerical(x, t, a, w, K_HS, dt) if t else z0
    print("   t=%7.0f  mean z = %+.6e m" % (t, z.mean()))

print()
print("And the scarp's mid-point slope should fall as 1/sqrt(t):")
mid = x.size // 2
for t in (1000.0, 4000.0, 16000.0):
    ana = analytic(x, t, a, w, K_HS)
    s = abs((ana[mid + 1] - ana[mid - 1]) / (2.0 * (x[1] - x[0])))
    print("   t=%6.0f  slope = %.4f   slope*sqrt(t) = %.4f" % (t, s, s * math.sqrt(t)))
