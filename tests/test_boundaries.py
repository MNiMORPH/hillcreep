"""One test per claim about the river boundaries, aggradation and the mask."""

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


def test_the_hill_stays_symmetric_when_both_rivers_share_a_rate():
    h = Hillslope(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    h.run(1.0e5)
    assert np.allclose(h.z, h.z[::-1], rtol=0.0, atol=1e-12)


# -- aggradation -------------------------------------------------------------

def _steady_hill(**kw):
    h = Hillslope(**kw)
    h.equilibrate()
    return h


def _aggrade_to(h, bed):
    """Raise both rivers to ``bed`` as an aggrading river would.

    The rate matters, not just the elevation: only an aggrading river holds its
    floodplain flat, so a bed raised while the rate is still positive describes
    a river that is cutting down through ground it is somehow also above.
    """
    h.incision_rate = -abs(h.incision_rate) or -0.05e-3
    h.left.bed = h.right.bed = bed
    h.apply_boundaries()
    return h


def test_aggrading_rivers_bury_the_toes_and_shorten_the_hillslope():
    """The coupling, not a cosmetic fill: burying a toe makes the hill shorter."""
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    assert h.exposed_length == h.length

    lengths = []
    for bed in (0.5, 1.0, 2.0, 4.0):
        _aggrade_to(h, bed)
        lengths.append(h.exposed_length)

    assert lengths == sorted(lengths, reverse=True)     # strictly shortening
    assert lengths[0] < h.length
    assert np.isclose(lengths[-1], 60.0)                # probe_d, bed = 4 m
    assert np.allclose(h.z[~h.active], 4.0)             # deposited to the level


def test_buried_nodes_sit_at_the_fill_elevation_and_do_not_evolve():
    h = _aggrade_to(_steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3), 2.0)

    buried = ~h.active
    assert buried.sum() > 2                             # more than the two ends
    assert np.allclose(h.z[buried], 2.0)        # alluvium at the fill

    # Kept aggrading: only an aggrading river holds its floodplain, and this
    # test is about what a held node does. (Written first with the rate set to
    # zero, which now releases the floodplain to diffuse -- correctly, but it
    # is a different claim.)
    h.run(2.0e4)
    # Against the *current* fill, not the 2.0 m it started at: the river is
    # still aggrading, so the level it holds keeps rising during the run.
    assert np.allclose(h.z[~h.active], h.left.bed)
    assert not (h.z[h.active] < h.left.bed).any()


def test_re_incision_leaves_a_fill_terrace_that_then_diffuses():
    """Deposition is permanent, so falling base level leaves a terrace.

    An earlier version tracked only the alluvial *level* and kept the buried
    hillslope underneath it. That exhumed the original topography and could
    never make a terrace, which is the wrong physics: sediment that was
    actually deposited does not vanish when the river cuts back down.
    """
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    original_toe = h.z[5]

    _aggrade_to(h, 3.0)
    assert not h.active[5]
    assert np.isclose(h.z[5], 3.0)                   # sediment deposited on it
    assert h.z[5] > original_toe                     # the toe is buried, not kept

    h.incision_rate = 0.05e-3                        # rivers cut back down
    h.left.bed = h.right.bed = 1.0
    h.apply_boundaries()
    assert h.active[5]
    assert np.isclose(h.z[5], 3.0)                   # the fill stayed put ...
    assert h.z[5] > h.left.bed                       # ... and stands above the river

    # A terrace is topography, so it degrades like any other.
    before = h.z[5]
    h.run(3.0e4)
    assert h.z[5] < before


def test_a_fully_buried_hillslope_is_flat_and_has_no_exposed_span():
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    _aggrade_to(h, h.z.max() + 1.0)

    assert h.exposed_span() is None
    assert h.exposed_length == 0.0
    # The *surface* is flat -- alluvium from side to side. The hillslope
    # beneath it is untouched, which is what lets it be exhumed later.
    assert np.allclose(h.z, h.left.bed)


def test_aggradation_runs_without_raising():
    """The whole point of this change: a negative rate used to be an error."""
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    h.incision_rate = -0.05e-3
    h.run(3.0e5)                                        # buries the toes
    assert h.exposed_length < h.length
