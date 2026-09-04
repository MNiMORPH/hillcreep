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

### Three versions, two of them wrong

Worth recording, because each failed for a different reason and the second one
looked right.

1. **Set drowned nodes to the level, keep a separate mask.** Inert. Pinning
   `z[0]` to a rising bed let diffusion lift the toe along with it, so at every
   rate the sliders offer no node ever drowned: exposed length stayed 100 m of
   100 m at 5, 10, 25 and 40 kyr of aggradation.
2. **Track the level only, remember the hillslope underneath.** Buried
   correctly -- exposed length 100 to 92 to 48 m -- but on re-incision the fill
   *vanished* and the original hillslope was exhumed intact. Andy caught it:
   aggradation should leave **fill terraces, which then diffuse on their own**.
   Tracking a level cannot do that, because nothing was ever deposited.
3. **Deposit permanently.** `z` is raised to the alluvial level and never
   lowered. While the river holds that level the node is inactive, so the fill
   stays flat and the hillslope shortens; when base level falls the node stands
   *above* the new level, becomes active, and is a fill terrace that degrades
   like any other topography.

Version 3 is also the simplest: one `np.maximum`, and no second array.

So the volume-or-level question resolves differently than design 03 first
recorded. The *level* drives deposition, but what is deposited is kept, so the
surface carries a memory of the fill. Mass is still not conserved within the
hillslope, and should not be: the river delivers material from outside it.

### Only an *aggrading* river holds its floodplain

The hold was first applied whenever ground sat at the alluvial level, whatever
the river was doing. Andy caught what that gives: with the rate at zero, the
floodplain edges stay pinned flat and the hillslope meets them at a kink --
"forces a parabola at the floodplain edges" -- when the whole domain should
diffuse and the fill edge should relax into a **sigmoid**.

He is right, and the reason is physical. A river holds its valley floor flat
*because it is actively regrading it*, which is what aggrading means. A river
that has stopped, or that is cutting down, has abandoned that surface; it is
then ordinary topography and degrades like a scarp.

So the hold is conditioned on the rate, not on the elevation:

```
held = (incision_rate < 0) and (z <= fill)
```

Measured, 72 kyr of aggradation then base level held at zero for 60 kyr, as
elevation above the river across the first 12 m of floodplain:

```
held always:  0      0      0      0      0      0     ...   flat, pinned
released:     0  0.0006 0.0011 0.0017 0.0022 0.0028   ...   a relaxing scarp
```

This also removes an oddity the earlier rule carried: a flat hillslope starting
level with its rivers was classified as valley floor and could not begin to
grow until they had cut down. Now it is active from the first step, and simply
does nothing until there is relief to drive it.

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
