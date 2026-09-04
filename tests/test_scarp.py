"""One test per claim about the diffusing fault scarp."""

import math

import numpy as np
import pytest

from hillcreep import Scarp


def test_the_initial_form_is_flat_then_the_stated_angle_then_flat():
    s = Scarp(height=5.0, angle=30.0)

    assert np.isclose(s.max_slope(), math.tan(math.radians(30.0)), rtol=1e-6)
    assert np.isclose(s.z[0], +2.5) and np.isclose(s.z[-1], -2.5)
    assert np.isclose(s.z.max() - s.z.min(), 5.0)
    # Flat away from the face, to the grid's resolution.
    assert np.allclose(s.z[:40], 2.5)
    assert np.allclose(s.z[-40:], -2.5)


def test_transport_runs_left_to_right():
    """High side on the left, so material creeps to the right."""
    s = Scarp()
    u = s.surface_velocity()
    assert u.max() > 0.0
    assert np.all(u >= -1e-15)               # nothing moves left, anywhere
    assert u[s.x.size // 2] > 0.0            # fastest at the face


def test_no_flux_ends_conserve_the_scarp_exactly():
    """A scarp has no rivers to carry material away, so nothing may leave.

    Volume conservation is exact rather than approximate: the flux form
    telescopes, and the two end cells exchange across one face each.
    """
    s = Scarp()
    before = s.z.sum()
    s.run(2.0e4)
    assert abs(s.z.sum() - before) < 1e-10 * max(1.0, abs(before))


def test_the_numerical_solution_tracks_the_closed_form():
    s = Scarp()
    for _ in range(4):
        s.run(5.0e3)
        misfit = np.max(np.abs(s.z - s.analytic()))
        # 5 m scarp on a 1 m grid: this is discretisation, and it shrinks as
        # the profile smooths. probe_e gets to 1.2e-6 m at dx = 0.1 m.
        assert misfit < 1e-3 * s.height


def test_a_scarp_records_only_the_product_of_diffusivity_and_time():
    """Morphologic dating, as a test.

    The closed form depends on ``k_hs`` and ``t`` only through ``k_hs * t``, so
    a fast scarp seen early and a slow one seen late are the same shape. This
    is why a surveyed scarp cannot be given an age without a diffusivity from
    somewhere else.
    """
    fast = Scarp(k_u=0.04, dz_u=0.10)         # k_hs = 0.004
    slow = Scarp(k_u=0.01, dz_u=0.10)         # k_hs = 0.001, four times slower

    fast.run(2.5e4)                            # k_hs t = 100 m2
    slow.run(1.0e5)                            # k_hs t = 100 m2

    assert np.isclose(fast.morphologic_age, slow.morphologic_age)
    assert np.isclose(fast.morphologic_age, 100.0)
    assert np.allclose(fast.z, slow.z, atol=1e-6)
    assert not np.isclose(fast.t, slow.t)      # ... at very different ages


def test_the_closed_form_is_only_trusted_while_the_ends_stay_flat():
    s = Scarp(length=60.0, n_nodes=61)         # deliberately too narrow
    assert s.ends_are_quiet()
    s.run(3.0e5)
    assert not s.ends_are_quiet()


def test_reset_returns_the_freshly_cut_scarp():
    s = Scarp()
    original = s.z.copy()
    s.run(1.0e4)
    assert not np.allclose(s.z, original)
    s.reset()
    assert s.t == 0.0
    assert np.allclose(s.z, original)


def test_the_scarp_shares_the_hillslope_transport_law():
    """Same k_hs, same velocity profile -- the point of the shared base class."""
    s = Scarp(k_u=0.02, dz_u=0.10)
    assert s.k_hs == 0.02 * 0.10

    zeta = np.array([0.0, 0.10, 0.20])
    u = s.velocity_field(zeta)
    assert np.allclose(u[1], u[0] / math.e)
    assert np.allclose(u[2], u[0] / math.e ** 2)
