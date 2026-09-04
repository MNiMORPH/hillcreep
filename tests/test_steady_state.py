"""One test per claim about the steady form the profile chases."""

import numpy as np

from hillcreep import Hillslope


def test_the_steady_parabola_is_a_fixed_point_in_the_falling_frame():
    """From the steady profile, one step lowers everything by exactly E*dt.

    dz/dt = D d2z/dx2 = -E for the parabola, so the whole surface translates
    downward with the rivers and its shape does not change.
    """
    h = Hillslope(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    h.z = h.steady_profile()
    before = h.z.copy()

    dt = h.stable_timestep()
    h.advance(dt)

    assert np.allclose(h.z, before - h.incision_rate * dt, rtol=0.0, atol=1e-12)


def test_the_profile_relaxes_toward_the_steady_parabola():
    h = Hillslope(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    misfit = [np.max(np.abs(h.z - h.steady_profile()))]
    for _ in range(4):
        h.run(1.0e5)
        misfit.append(np.max(np.abs(h.z - h.steady_profile())))

    assert np.all(np.diff(misfit) < 0.0)        # monotonically closing
    assert misfit[-1] < 0.05 * misfit[0]


def test_steady_surface_velocity_does_not_depend_on_K():
    """The demo's second lesson, as a test.

    Mass balance gives u_s = E x' / dz_u with no k_u in it.  The independent
    route -- u_s = -k_u dz/dx on the steady parabola -- must agree, for every k_u.
    Both are exact for a quadratic, so this is a machine-precision comparison.
    """
    for k_u in (0.005, 0.02, 0.08):
        h = Hillslope(k_u=k_u, dz_u=0.5, incision_rate=0.05e-3)
        h.z = h.steady_profile()

        from_profile = h.surface_velocity()
        from_mass_balance = h.steady_surface_velocity()

        assert np.allclose(from_profile, from_mass_balance, rtol=0.0, atol=1e-15)


def test_a_hill_with_no_incision_decays_at_the_analytic_rate():
    """With E = 0 the fundamental mode decays as exp(-D pi**2 t / L**2).

    A sine hump between fixed ends *is* that eigenmode, so it must keep its
    shape and lose amplitude at the analytic rate.  Written first as a loose
    "relief drops below 5%" check, which failed: the model gave 1.389 m from
    10 m, and exp(-1.974) = 0.1389 exactly.  The model was right and the
    threshold was invented, so the threshold was replaced by the analytic
    prediction -- a far stronger test than the one it replaces.
    """
    h = Hillslope(k_u=0.02, dz_u=0.5, incision_rate=0.0)
    shape = np.sin(np.pi * h.x / h.length)
    h.z = 10.0 * shape
    h.apply_boundaries()

    t_end = 2.0e5
    h.run(t_end)

    decay = np.exp(-h.k_hs * np.pi ** 2 * t_end / h.length ** 2)
    # 1% covers the two discretisations: the discrete Laplacian's eigenvalue
    # differs from pi**2/L**2 by ~1e-4 relative, and forward Euler's (1-dt*L)**n
    # from exp(-L*t) by ~3e-4.
    assert np.allclose(h.z, 10.0 * decay * shape, rtol=1e-2, atol=1e-6)
    assert h.z.max() < 0.2 * 10.0
