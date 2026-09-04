"""One test per claim about the transport law.  The test name states the claim."""

import numpy as np
import pytest

from hillcreep import Hillslope


def test_diffusivity_is_exactly_the_product_of_the_two_sliders():
    h = Hillslope(k_u=0.037, dz_u=1.3)
    assert h.k_hs == 0.037 * 1.3


def test_velocity_field_integrates_to_the_flux():
    """int_0^inf u dzeta = q.  This is the identity the whole model rests on."""
    h = Hillslope(k_u=0.02, dz_u=0.5)
    h.z = 20.0 * np.sin(np.pi * h.x / h.length)     # any non-trivial profile
    h.apply_boundaries()

    # Integrate the drawn field numerically, deep enough that the tail is
    # negligible, and compare with the closed-form q_m at nodes.
    zeta = np.linspace(0.0, 40.0 * h.dz_u, 200001)
    u = h.velocity_field(zeta)
    q_numeric = np.trapz(u, zeta, axis=0)
    # edge_order=2 to match Hillslope.surface_velocity.  With numpy's default
    # the two end nodes disagree -- not a failure of the identity, just two
    # different estimates of dz/dx being compared against each other.
    q_closed = -h.k_hs * np.gradient(h.z, h.dx, edge_order=2)

    assert np.allclose(q_numeric, q_closed, rtol=1e-8, atol=1e-14)


def test_face_form_flux_matches_the_constant_diffusivity_stencil():
    """With k_u and dz_u uniform, face form == the familiar second difference.

    Face form is used anyway, because it is the only version that survives D
    becoming a function of x (design 05).  This test is what lets that claim be
    made without cost.
    """
    h = Hillslope(k_u=0.02, dz_u=0.5)
    # Arbitrary elevations, deliberately not a hillslope: this tests the flux
    # operator, so the profile should exercise it rather than flatter it.
    # apply_boundaries() is not called -- the boundaries are not under test,
    # and a random z[1] below the river bed correctly trips the aggradation
    # guard (see test_boundaries.py).
    # Offset above the alluvial surface: the transport law acts on
    # max(z, fill), so a profile dipping below the river level would be clipped
    # by the fill and would not be testing the flux operator at all.
    h.z = 10.0 + np.random.default_rng(0).normal(size=h.x.size)

    face_form = -np.diff(h.q_m()) / h.dx
    surf = h.surface()
    stencil = (h.k_hs
               * (surf[:-2] - 2.0 * surf[1:-1] + surf[2:]) / h.dx ** 2)

    assert np.allclose(face_form, stencil, rtol=0.0, atol=1e-12)


def test_surface_velocity_is_zero_at_the_divide_and_opposed_at_the_toes():
    h = Hillslope(k_u=0.02, dz_u=0.5)
    h.z = h.steady_profile()
    u_s = h.surface_velocity()

    mid = h.x.size // 2
    assert abs(u_s[mid]) < 1e-15
    assert u_s[0] < 0.0 < u_s[-1]        # both toes move away from the divide


def test_velocity_decays_by_one_e_folding_over_H_star():
    h = Hillslope(k_u=0.02, dz_u=0.7)
    h.z = h.steady_profile()
    u = h.velocity_field([0.0, 0.7, 1.4])

    assert np.allclose(u[1], u[0] / np.e)
    assert np.allclose(u[2], u[0] / np.e ** 2)
