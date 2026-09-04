# 03 -- Boundaries: rivers with prescribed rates

## The question

The hillslope's two ends are rivers. What do they do, and how is the code
arranged so that rivers which *aggrade* -- rise, and bury the base of the
hillslope -- can be added later without rewriting the boundary handling?

## What ships now

Both rivers lower (or raise) their beds at a single prescribed rate `ε̇`,
positive for incision, matching the sign of Andy's 2013 `zdot_channel`. The two
sides are symmetric, which keeps the divide at the centre and keeps the steady
parabola valid as a live check curve:

```
z - z_river = E * x * (L - x) / (2 * D)
```

`E = 0` is allowed and is a lesson in itself: the hill decays toward flat.
`E < 0` is accepted by the model and raises the river beds, but until the
onlap code of the next section exists it simply lifts the boundary nodes
without burying anything.

## Onlap: implemented 2026-09-04

Aggradation that buries the hillslope toe is a **moving-boundary** problem: as
the alluvial surface rises past the hillslope profile, the contact migrates
upslope and the hillslope domain shrinks. The structure was built first and the
branch left empty; the code went in afterwards, and **the claim that nothing
outside `apply_boundaries()` would need to change held** -- the implementation
touched that one method plus the two steady-form helpers, which now measure
across the exposed span instead of the full grid.

The structure that made it cheap:

- the boundary is a `River` object holding its bed elevation and its rate, not
  a bare number spliced into `z[0]` and `z[-1]`;
- an `active` boolean mask over nodes says which the solver evolves. Today it
  is all-`True` except the two ends;
- `apply_boundaries()` is the single place that reads the rivers and writes
  elevations, with the onlap branch present and raising `NotImplementedError`.

### The algorithm, in Andy's words

> just flood a level set with sediment, which then really does affect the
> downslope boundary of the hillslope

That is the whole thing, and it is simpler than "moving boundary" makes it
sound. The alluvial surface is a **level set**: one elevation `z_river`, flat
across the valley. Flooding it means

1. raise `z_river` at the prescribed rate;
2. find every node with `z < z_river` -- the toe the sediment has drowned;
3. set those nodes to `z_river` and drop them from `active`;
4. the hillslope's boundary is now the shallowest still-active node, and the
   hillslope is *shorter*.

Step 4 is the part that matters and the reason this is not cosmetic: burying
the toe shortens the hillslope, which shortens the distance over which the
divide has to shed its material, which changes the whole profile. It is a real
coupling, not a paint job on the bottom of the figure.

Two questions this will raise, recorded now so they are not rediscovered:
whether a node re-emerges when `z_river` falls again (it should, by the same
test in reverse), and whether the deposited sediment is tracked as a volume or
merely as a level (the level alone is enough to move the boundary, and is what
the quote describes).

One thing the design did not anticipate, found by running it: **re-emergence is
free.** Because the mask is rebuilt from scratch on every call, a node that is
no longer under the alluvial surface simply becomes active again. No bookkeeping
was needed for it at all.

The second question -- volume or level -- is answered by the quote: the level
alone is enough to move the boundary, and no sediment volume is tracked. The
consequence, which is physically right and worth stating, is that mass is not
conserved within the hillslope. It should not be: the river is *delivering*
sediment from outside.

### One ordering trap, paid for

The flux must be computed against the bed as it stands at the *start* of a step,
with the rivers moved afterwards. Moving them first means node 1 sees an
already-lowered boundary, and the steady parabola drifts off its own fixed
point by `D E dt² / dx²` per step -- 3e-7 m at the usual settings. Small, and
purely an artefact of operator ordering rather than of the physics, so it is
free to avoid. `test_the_steady_parabola_is_a_fixed_point_in_the_falling_frame`
catches it.

## Rejected: independent left and right rates

Asymmetric incision migrates the divide toward the faster-incising side, which
is a genuinely good lesson and costs nothing in the solver. It was rejected for
now on one ground only: there is no steady state in that frame, so the dashed
check curve -- the thing that tells a student what the profile is chasing --
would have to be dropped or shown conditionally. Revisit if the check curve
turns out to matter less than the divide migration.

## Parameters chosen here

- **`ε̇` slider range: -0.05 to +0.10 mm/yr, default 0.05.** *A proposal.* The
  upper bound is set by steepness: `probe_a` shows `E = 0.2 mm/yr` at the
  default `k_u` and `Δz_u` gives a steady toe slope of 1.0 (45°), far outside where
  a linear creep law is defensible. At `E = 0.10` the toe slope is 0.50
  (26.6°). The negative end is arbitrary pending the onlap code.
