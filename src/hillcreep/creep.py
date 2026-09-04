"""The creep transport law, shared by every surface in this package.

One idea, in one place: soil creeps downslope at a rate that decays
exponentially below the ground surface,

    u(x, zeta) = -k_u dz/dx * exp(-zeta / dz_u)

and integrating that profile over a deep mobile layer gives the flux and, with
it, the diffusivity:

    q_m  = -k_u * dz_u * dz/dx
    k_hs =  k_u * dz_u

Everything that differs between a hillslope and a fault scarp is a *boundary
condition*, not a transport law, so the law lives here and each surface says
only what happens at its edges.

Units are metres and years.  Elevation ``z`` is positive up; depth below the
surface ``zeta`` is positive down.
"""

import numpy as np

__all__ = ["CreepingProfile"]


class CreepingProfile(object):
    """A one-dimensional surface that creeps.

    Subclasses supply :meth:`apply_boundaries`, which is the only thing that
    distinguishes one setting from another.

    Parameters
    ----------
    length : float
        Width of the domain [m].
    n_nodes : int
        Number of nodes across it.
    k_u : float
        Surface creep velocity at unit slope [m/yr].  *Not* the surface
        velocity itself, which varies along the profile as ``u_s = k_u * S``.
    dz_u : float
        Creep e-folding depth [m], the course notes' ``Delta z_u``.
    """

    def __init__(self, length, n_nodes, k_u, dz_u):
        self.length = float(length)
        self.x = np.linspace(0.0, self.length, int(n_nodes))
        self.dx = self.x[1] - self.x[0]
        self.k_u = float(k_u)
        self.dz_u = float(dz_u)
        self.z = np.zeros(self.x.size)
        self.t = 0.0
        self.active = np.ones(self.x.size, dtype=bool)

    def apply_boundaries(self):
        """Impose whatever holds at the edges. Subclasses override."""
        raise NotImplementedError

    @property
    def k_hs(self):
        """Hillslope diffusivity ``k_hs = k_u * dz_u`` [m**2/yr].

        Reported, never set.  Landlab's ``DepthDependentDiffuser`` states the
        same identity, in its own notation (quoted verbatim, so its symbols are
        left alone): "the commonly used 'hillslope diffusivity' coefficient is
        equal to the product of K and H*".
        """
        return self.k_u * self.dz_u

    def face_slope(self):
        """Slope ``dz/dx`` on the faces between nodes [-]. Length ``n - 1``."""
        return np.diff(self.z) / self.dx

    def surface_velocity(self):
        """Downslope surface creep velocity ``u_s = -k_u dz/dx`` at nodes [m/yr].

        Signed: positive is motion in the +x direction.  Zero at the divide,
        largest in magnitude at the toes.  Node-aligned with ``x``.

        ``edge_order=2`` is not optional.  numpy's default first-order one-sided
        difference at the ends is not exact for a quadratic, and biases the toe
        velocity low by 1% (4.95 against 5.00 mm/yr at the shipped defaults) --
        at exactly the two nodes where velocity is largest and where the demo
        draws the eye.  Caught by
        ``test_steady_surface_velocity_does_not_depend_on_K``.
        """
        return -self.k_u * np.gradient(self.z, self.dx, edge_order=2)

    def velocity_field(self, zeta):
        """``u(x, zeta) = u_s(x) exp(-zeta / dz_u)`` [m/yr].

        Parameters
        ----------
        zeta : array_like
            Depths below the land-air interface [m], positive down.

        Returns
        -------
        ndarray, shape ``(zeta.size, x.size)``
            Row 0 is the surface.  The field is separable, so this is an outer
            product -- cheap enough to recompute every animation frame.
        """
        zeta = np.atleast_1d(np.asarray(zeta, dtype=float))
        return np.exp(-zeta / self.dz_u)[:, None] * self.surface_velocity()[None, :]

    def q_m(self):
        """Depth-integrated soil q_m ``q = -k_u dz_u dz/dx`` on faces [m**2/yr].

        Face form, not a node-centred second difference.  With ``k_u`` and
        ``dz_u`` uniform the two are identical, so this costs nothing now;
        it is the only form that survives ``D`` becoming a function of ``x``
        once soil thickness varies.  See design/05.
        """
        return -self.k_hs * np.diff(self.z) / self.dx

    # -- time stepping -----------------------------------------------------

    def stable_timestep(self, safety=0.25):
        """Explicit-diffusion time step ``safety * dx**2 / D`` [yr].

        The stability limit is ``dx**2 / (2 D)``; ``safety = 0.25`` is half of
        that.  A demo whose sliders change ``D`` while it runs must size the
        step from the largest ``D`` on offer, not the current one.
        """
        return safety * self.dx ** 2 / self.k_hs

    def run(self, duration, dt=None):
        """Advance for ``duration`` years in steps of ``dt`` (default stable)."""
        dt = self.stable_timestep() if dt is None else dt
        for _ in range(int(round(duration / dt))):
            self.advance(dt)
