"""A fault scarp, left to diffuse.

The same creep law as the hillslope (:mod:`hillcreep.creep`), with the simplest
possible boundaries: **none**. No rivers, no base level, no flux across either
end. Whatever material leaves the scarp face has to arrive somewhere else in
the domain, so the scarp does not decay away -- it spreads into itself, and its
volume never changes.

The initial form is a scarp cut into a flat surface: flat above, a straight
face at some angle, flat below. Net transport is left to right, so the high
side is on the left.

    z(x, 0) =  +a                      left of the face
            =  -a (x - x_c) / w        across it
            =  -a                      right of it

with ``a`` half the scarp height and ``w = a / tan(angle)`` half its width.

Unlike the hillslope, this problem has a **closed-form solution**, and the demo
draws it. Differentiating the diffusion equation shows the *slope* of that
initial profile is a diffusing rectangular pulse, whose solution is a
difference of error functions; integrating back gives :meth:`analytic`.
Verified against the numerical solution to 1.2e-6 m in
``prototypes/probe_e_scarp_analytic.py``.

That closed form is the basis of **scarp morphologic dating**: it depends on
time and diffusivity only through their product, so a surveyed scarp yields
``k_hs * t`` and nothing more. Getting an age out of it needs ``k_hs`` from
somewhere else -- which, in this package, is ``k_u * dz_u``.
"""

import math

import numpy as np

from .creep import CreepingProfile

__all__ = ["Scarp"]

_erf = np.vectorize(math.erf)


class Scarp(CreepingProfile):
    """A fault scarp diffusing on an otherwise flat surface.

    Parameters
    ----------
    length : float
        Width of the domain [m]. Wide enough that the ends stay flat, or the
        no-flux boundaries will start to matter; see :meth:`ends_are_quiet`.
    n_nodes : int
        Number of nodes across it.
    k_u : float
        Surface creep velocity at unit slope [m/yr].
    dz_u : float
        Creep e-folding depth [m].
    height : float
        Scarp height, crest to toe [m].
    angle : float
        Angle of the initial face [degrees]. Steep on purpose: a real scarp is
        cut by faulting, not by creep, so it starts far outside anything a
        linear transport law would produce.
    """

    def __init__(self, length=240.0, n_nodes=241, k_u=0.02, dz_u=0.5,
                 height=5.0, angle=30.0):
        CreepingProfile.__init__(self, length, n_nodes, k_u, dz_u)
        self.height = float(height)
        self.angle = float(angle)
        self.reset()

    # -- the initial form --------------------------------------------------

    @property
    def half_height(self):
        """Half the scarp height, ``a`` [m]."""
        return 0.5 * self.height

    @property
    def half_width(self):
        """Half the width of the initial face, ``w = a / tan(angle)`` [m]."""
        return self.half_height / math.tan(math.radians(self.angle))

    def initial_profile(self):
        """Flat, a straight face at ``angle``, flat again [m]."""
        xc = self.x - 0.5 * self.length
        a, w = self.half_height, self.half_width
        return np.clip(-a * xc / w, -a, a)

    def reset(self):
        """Return to the freshly cut scarp at ``t = 0``."""
        self.z = self.initial_profile()
        self.t = 0.0
        self.apply_boundaries()

    # -- boundaries: there are none ---------------------------------------

    def apply_boundaries(self):
        """No flux at either end, so every node is free to move.

        The hillslope's edges are held by rivers; a scarp's are held by
        nothing. Both ends are closed instead, which is what makes the scarp's
        volume constant: material creeping off the face has to land inside the
        domain.
        """
        self.active[:] = True

    def advance(self, dt):
        """Advance by ``dt`` years, conserving volume exactly."""
        q = self.q_m()                       # on the n-1 interior faces
        dzdt = np.empty(self.z.size)
        dzdt[1:-1] = -np.diff(q) / self.dx
        # The two outermost cells exchange with one neighbour each, the other
        # face carrying no flux. Summing dzdt over all nodes telescopes to
        # zero, so the volume is conserved to machine precision rather than
        # approximately.
        dzdt[0] = -q[0] / self.dx
        dzdt[-1] = q[-1] / self.dx
        self.z += dt * dzdt
        self.t += dt
        self.apply_boundaries()

    # -- what the numerical solution can be checked against ----------------

    @property
    def morphologic_age(self):
        """``k_hs * t`` [m**2] -- the only thing a surveyed scarp records.

        Time and diffusivity enter the solution solely through this product, so
        two scarps with the same value are the same shape whatever their ages.
        """
        return self.k_hs * self.t

    def analytic(self, t=None):
        """The closed-form profile at time ``t`` (default: now) [m].

        See the module docstring for the derivation, and
        ``prototypes/probe_e_scarp_analytic.py`` for the check against the
        numerical solution.
        """
        t = self.t if t is None else float(t)
        a, w = self.half_height, self.half_width
        xc = self.x - 0.5 * self.length
        if self.k_hs * t <= 0.0:
            return np.clip(-a * xc / w, -a, a)
        beta = 2.0 * math.sqrt(self.k_hs * t)
        xp, xm = (xc + w) / beta, (xc - w) / beta
        return -(a / (2.0 * w)) * (
            (xc + w) * _erf(xp) - (xc - w) * _erf(xm)
            + (beta / math.sqrt(math.pi))
            * (np.exp(-xp ** 2) - np.exp(-xm ** 2)))

    def max_slope(self):
        """Steepest slope anywhere on the profile [-], as a positive number."""
        return float(np.max(np.abs(np.gradient(self.z, self.dx, edge_order=2))))

    def ends_are_quiet(self, tol=0.01):
        """Has the scarp reached the domain ends yet?

        ``False`` means the no-flux boundaries have begun to matter and the
        closed form -- which assumes an infinite surface -- no longer applies.
        """
        a = self.half_height
        return bool(abs(self.z[0] - a) < tol * self.height
                    and abs(self.z[-1] + a) < tol * self.height)
