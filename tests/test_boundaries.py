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


def test_aggrading_rivers_bury_the_toes_and_shorten_the_hillslope():
    """The coupling, not a cosmetic fill: burying a toe makes the hill shorter."""
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    assert h.exposed_length == h.length

    lengths = []
    for bed in (0.5, 1.0, 2.0, 4.0):
        h.left.bed = h.right.bed = bed
        h.apply_boundaries()
        lengths.append(h.exposed_length)

    assert lengths == sorted(lengths, reverse=True)     # strictly shortening
    assert lengths[0] < h.length
    assert np.isclose(lengths[-1], 62.0)                # probe_d, bed = 4 m


def test_buried_nodes_sit_at_the_fill_elevation_and_do_not_evolve():
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    h.left.bed = h.right.bed = 2.0
    h.apply_boundaries()

    buried = ~h.active
    assert buried.sum() > 2                             # more than the two ends
    assert np.allclose(h.surface()[buried], 2.0)        # alluvium at the fill

    # Written first as "the buried set grows", which failed: it shrank from 18
    # nodes to 2. That is the model being right. With the fill held, the
    # exposed hill decays *onto* it, so drowned nodes are lifted to the fill
    # level and stop being below it. The invariants that actually hold are the
    # two below.
    h.incision_rate = 0.0
    h.run(2.0e4)
    assert np.allclose(h.surface()[~h.active], 2.0)  # alluvium over buried nodes
    assert not (h.surface()[h.active] < 2.0).any()   # nothing exposed below it


def test_a_buried_toe_is_exhumed_unchanged_when_base_level_falls():
    """Re-emergence is free because the mask is rebuilt every call.

    The hillslope under the sediment is *remembered*, not overwritten, so
    lowering base level exhumes the topography that was buried rather than
    inventing a terrace. An earlier version did overwrite it, and that quietly
    defeated the whole mechanism: with z pinned to a rising bed, diffusion
    lifted the toe along with it and no node ever drowned at any rate the
    sliders offer.
    """
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    original_toe = h.z[1]

    h.left.bed = h.right.bed = 3.0
    h.apply_boundaries()
    assert not h.active[1]
    assert np.isclose(h.surface()[1], 3.0)           # alluvium over it
    assert np.isclose(h.z[1], original_toe)          # hillslope remembered

    h.left.bed = h.right.bed = 0.0
    h.apply_boundaries()
    assert h.active[1]
    assert np.isclose(h.z[1], original_toe)          # exhumed unchanged


def test_a_fully_buried_hillslope_is_flat_and_has_no_exposed_span():
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    h.left.bed = h.right.bed = h.z.max() + 1.0
    h.apply_boundaries()

    assert h.exposed_span() is None
    assert h.exposed_length == 0.0
    # The *surface* is flat -- alluvium from side to side. The hillslope
    # beneath it is untouched, which is what lets it be exhumed later.
    assert np.allclose(h.surface(), h.left.bed)


def test_aggradation_runs_without_raising():
    """The whole point of this change: a negative rate used to be an error."""
    h = _steady_hill(k_u=0.02, dz_u=0.5, incision_rate=0.05e-3)
    h.incision_rate = -0.05e-3
    h.run(3.0e5)                                        # buries the toes
    assert h.exposed_length < h.length
