"""A hillslope whose diffusivity is built, not assumed.

The model in one place.  Soil creeps downslope at a rate that decays
exponentially below the land-air interface,

    u(x, zeta) = u_s(x) * exp(-zeta / dz_u),      u_s(x) = -k_u * dz/dx

with ``zeta`` the depth below the surface, positive downward.  Integrating that
profile over a semi-infinite mobile layer gives the depth-integrated flux of
mobile material, and with it the hillslope diffusivity:

    q_m(x) = integral_0^inf u dzeta = -k_u * dz_u * dz/dx
    k_hs   = k_u * dz_u

``k_hs`` is therefore *computed and reported*, never set.  That is the whole
point of this model; see ``design/02-teaching-scope.md``.

Notation follows Andy's Geomorphology course notes rather than any one paper,
because the literature has no single convention for this law -- three papers
give three notations -- and because the obvious literature symbols are already
taken elsewhere in the course: ``D`` is grain size and ``K`` is turbulent
diffusivity.  ``k_u`` is the one symbol not already in the notes; it is the
[L/T] coefficient that the notes' ``k_hs`` currently doubles for.  The
crosswalk to the literature is in ``README.md`` and the reasoning is in
``design/01-transport-law.md``.

    k_hs   hillslope diffusivity          [m^2/yr]   computed, never set
    k_u    surface creep velocity at unit slope [m/yr]
    dz_u   creep e-folding depth, the notes' Delta z_u    [m]
    q_m    depth-integrated flux of mobile material  [m^2/yr]
    u_s    surface creep velocity, k_u * S           [m/yr]
    zeta   depth below the land-air interface, = -(z' - z) in the notes

The law is Johnstone & Hilley (2015), Geology 43(1) 83-86, in the no-bedrock
limit; the exponential velocity profile it integrates is measured by Deshpande,
Furbish, Arratia & Jerolmack (2021), Nature Communications 12:3909; and it is
derived independently in the course notes themselves (see
``docs/course-notes-provenance.md``).

Units are metres and years throughout.  Elevation ``z`` is positive up; depth
below the surface ``zeta`` is positive down.
"""

import numpy as np

__all__ = ["River", "Hillslope"]


class River(object):
    """A channel at one end of the hillslope, setting base level.

    Parameters
    ----------
    bed : float
        Bed elevation [m].
    incision_rate : float
        Rate of bed lowering [m/yr], **positive for incision**, following the
        sign of ``zdot_channel`` in Andy's 2013 course script.  Negative values
        raise the bed; burying the hillslope toe is not implemented (see
        ``Hillslope.apply_boundaries``).
    """

    def __init__(self, bed=0.0, incision_rate=0.0):
        self.bed = float(bed)
        self.incision_rate = float(incision_rate)

    def advance(self, dt):
        """Lower (or raise) the bed by one time step."""
        self.bed -= self.incision_rate * dt


class Hillslope(object):
    """A symmetric soil-mantled hillslope between two rivers.

    Parameters
    ----------
    length : float
        Distance between the two channels [m].
    n_nodes : int
        Number of nodes across that distance.
    k_u : float
        Surface creep velocity at unit slope [m/yr].  *Not* the surface
        velocity itself, which varies along the hill as ``u_s = k_u * S``.
        This is the coefficient the course notes' ``k_hs`` doubles for in
        their depth-dependent flux equation; it needs its own name because it
        differs from a diffusivity by one power of length.
    dz_u : float
        Creep e-folding depth [m], the notes' ``Delta z_u``: the depth over
        which downslope velocity falls by a factor of e.
    incision_rate : float
        Bed lowering rate applied to both rivers [m/yr], positive for incision.
    z : array_like, optional
        Initial surface elevation [m].  Defaults to flat at the river bed.
    """

    def __init__(self, length=100.0, n_nodes=101, k_u=0.02, dz_u=0.5,
                 incision_rate=0.05e-3, z=None):
        self.length = float(length)
        self.x = np.linspace(0.0, self.length, int(n_nodes))
        self.dx = self.x[1] - self.x[0]

        self.k_u = float(k_u)
        self.dz_u = float(dz_u)

        self.left = River(bed=0.0, incision_rate=incision_rate)
        self.right = River(bed=0.0, incision_rate=incision_rate)

        self.z = np.zeros(self.x.size) if z is None else np.array(z, dtype=float)
        self.t = 0.0

        # Which nodes the solver evolves.  Today this is every interior node,
        # and it exists so that aggrading rivers can later bury the toe by
        # dropping nodes out of it without the solver being rewritten.
        # See design/03-boundaries-and-rivers.md.
        self.active = np.ones(self.x.size, dtype=bool)
        self.active[0] = self.active[-1] = False

        self.apply_boundaries()

    # -- what the two sliders add up to ----------------------------------

    @property
    def k_hs(self):
        """Hillslope diffusivity ``k_hs = k_u * dz_u`` [m**2/yr].

        Reported, never set.  Landlab's ``DepthDependentDiffuser`` states the
        same identity, in its own notation (quoted verbatim, so its symbols are
        left alone): "the commonly used 'hillslope diffusivity' coefficient is
        equal to the product of K and H*".
        """
        return self.k_u * self.dz_u

    @property
    def incision_rate(self):
        """The rate both rivers share [m/yr]. Setting it sets both."""
        return self.left.incision_rate

    @incision_rate.setter
    def incision_rate(self, value):
        self.left.incision_rate = self.right.incision_rate = float(value)

    # -- the transport law ------------------------------------------------

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
        return -self.k_hs * self.face_slope()

    # -- time stepping -----------------------------------------------------

    def stable_timestep(self, safety=0.25):
        """Explicit-diffusion time step ``safety * dx**2 / D`` [yr].

        The stability limit is ``dx**2 / (2 D)``; ``safety = 0.25`` is half of
        that.  A demo whose sliders change ``D`` while it runs must size the
        step from the largest ``D`` on offer, not the current one.
        """
        return safety * self.dx ** 2 / self.k_hs

    def apply_boundaries(self):
        """Write the river beds into the elevation array.

        The single place that couples rivers to the hillslope.  When aggrading
        rivers are implemented, the onlap branch below is where they go: find
        the nodes standing below the alluvial surface, set them to it, and drop
        them from ``self.active``.  Nothing outside this method should need to
        change -- that claim is the reason the structure exists.
        """
        if self.left.bed > self.z[1] or self.right.bed > self.z[-2]:
            raise NotImplementedError(
                "A river bed has risen above its neighbouring hillslope node. "
                "Burying the hillslope toe by aggradation is a moving-boundary "
                "problem and is not implemented; see "
                "design/03-boundaries-and-rivers.md.")
        self.z[0] = self.left.bed
        self.z[-1] = self.right.bed

    def advance(self, dt):
        """Advance the hillslope by one time step of ``dt`` years."""
        self.left.advance(dt)
        self.right.advance(dt)
        # Conservation of mass: dz/dt = -dq/dx, with q on faces.
        dzdt = -np.diff(self.q_m()) / self.dx
        self.z[1:-1] += dt * np.where(self.active[1:-1], dzdt, 0.0)
        self.apply_boundaries()
        self.t += dt

    def run(self, duration, dt=None):
        """Advance for ``duration`` years in steps of ``dt`` (default stable)."""
        dt = self.stable_timestep() if dt is None else dt
        for _ in range(int(round(duration / dt))):
            self.advance(dt)

    # -- what the profile is chasing --------------------------------------

    def steady_profile(self):
        """Elevation of the steady form for the current settings [m].

        Balancing uniform lowering at ``E`` against diffusion gives the
        parabola ``z - z_river = E x (L - x) / (2 D)``.  Valid only while both
        rivers share a rate, which is why they do (design 03).
        """
        base = 0.5 * (self.left.bed + self.right.bed)
        return base + (self.incision_rate / (2.0 * self.k_hs)
                       * self.x * (self.length - self.x))

    def steady_surface_velocity(self):
        """Steady surface velocity ``u_s = E x' / dz_u`` at nodes [m/yr].

        ``x'`` is distance from the divide, signed so that the result carries
        the direction of motion.  Note what is absent: ``k_u``.  Mass balance
        fixes the flux each point must carry, and the e-folding depth alone
        decides how fast the surface must move to carry it.  Verified against
        the parabola route in ``prototypes/probe_b_steady_surface_velocity.py``.
        """
        return self.incision_rate * (self.x - 0.5 * self.length) / self.dz_u
