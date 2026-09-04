"""One test per claim about the river boundaries and the active-node mask."""

import numpy as np
import pytest

from hillcreep import Hillslope


def test_both_rivers_lower_at_the_prescribed_rate():
    h = Hillslope(incision_rate=0.05e-3)
    h.run(1.0e4, dt=10.0)

    expected = -0.05e-3 * 1.0e4
    assert np.isclose(h.left.bed, expected)
    assert np.isclose(h.right.bed, expected)
    assert h.z[0] == h.left.bed and h.z[-1] == h.right.bed


def test_aggradation_past_the_toe_raises_rather_than_silently_misbehaving():
    """Burying the hillslope toe is a moving-boundary problem, not implemented.

    The failure has to be loud: a quietly wrong answer here would look like a
    result.  See design/03-boundaries-and-rivers.md.
    """
    h = Hillslope(incision_rate=-1.0e-3)          # negative: rivers aggrade
    with pytest.raises(NotImplementedError, match="moving-boundary"):
        h.run(1.0e5, dt=100.0)


def test_a_node_dropped_from_the_active_mask_does_not_evolve():
    """The hook aggradation will use: inactive nodes are held, not solved."""
    h = Hillslope(K=0.02, H_star=0.5, incision_rate=0.0)
    h.z = 10.0 * np.sin(np.pi * h.x / h.length)
    h.apply_boundaries()

    pinned = 25
    h.active[pinned] = False
    held = h.z[pinned]

    h.run(1.0e4)

    assert h.z[pinned] == held
    assert not np.isclose(h.z[pinned + 5], 10.0 * np.sin(np.pi * h.x[pinned + 5] / h.length))


def test_the_hill_stays_symmetric_when_both_rivers_share_a_rate():
    h = Hillslope(K=0.02, H_star=0.5, incision_rate=0.05e-3)
    h.run(1.0e5)
    assert np.allclose(h.z, h.z[::-1], rtol=0.0, atol=1e-12)
