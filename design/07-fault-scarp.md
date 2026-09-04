# 07 -- A diffusing fault scarp

## The question

A second experiment, in its own panel: a scarp cut into a flat surface at 30
degrees, left to diffuse. What does it need that the hillslope did not, and
what does it teach that the hillslope cannot?

## Why it is worth a second panel

The hillslope demo shows that `k_hs = k_u · Δz_u`. It cannot show what that
number is *used for*, because a hillslope in balance with its rivers hides the
timescale: the profile stops changing and stands there.

A scarp is the opposite. Nothing holds it, so it does nothing but relax, and
its shape is a clock. That makes it the natural place to introduce **scarp
morphologic dating** -- and to land the sting in the tail, which is that a
surveyed scarp does not give an age at all.

## The model

Boundaries are the only thing that differs from the hillslope, which is why the
transport law moved into `hillcreep/creep.py` and both surfaces now inherit it.
The scarp's boundaries are **no flux at either end**. A hillslope's edges are
held by rivers that carry material away; a scarp's edges are held by nothing,
so the domain is closed and the scarp's volume is constant. It does not decay
*away*; it spreads into itself.

Volume conservation is exact, not approximate: the flux form telescopes, and
the two end cells each exchange across a single face.

Initial form, with the high side on the left so transport runs left to right:

```
z(x,0) = +a                     left of the face
       = -a (x - x_c) / w       across it
       = -a                     right of it
```

with `a = height/2` and `w = a / tan(angle)`.

**The 30 degree face is deliberately outside what the transport law would ever
produce.** That is the point: a scarp is cut by faulting, in an instant, and
then handed to a process that could never have built it. Nothing needs to
apologise for the steepness.

## The closed form, and what it buys

This problem has an analytic solution, which the hillslope's transient does
not. Differentiating the diffusion equation shows that the *slope* of a ramp is
a diffusing rectangular pulse -- a difference of error functions -- and
integrating back, with `z(+∞) = -a` fixing the constant:

```
beta = 2 sqrt(k_hs t)

z(x,t) = -(a/2w) [ (x+w) erf((x+w)/beta) - (x-w) erf((x-w)/beta)
                   + (beta/sqrt(pi)) ( e^-((x+w)/beta)^2 - e^-((x-w)/beta)^2 ) ]
```

Verified against a fine-grid numerical solution in `probe_e`: agreement to
4.9e-5 m at t = 100 yr, improving to 1.2e-6 m at t = 20 kyr, with the mean
elevation unchanged to machine precision. At long times the mid-point slope
approaches the step-scarp limit `a / sqrt(pi k_hs)` -- measured 13.97 against
14.10 -- because a finite ramp eventually looks like a step.

**The lesson is in the form of the solution, not its value.** `k_hs` and `t`
appear only as the product `k_hs · t`. A surveyed scarp therefore records a
**morphologic age** in m², and nothing else: a fast scarp seen early and a slow
one seen late are the same shape. Turning that into years needs `k_hs` from
somewhere else -- which is `k_u · Δz_u`, and is exactly what the first panel is
about. The two exercises close on each other.

Tested directly: `k_hs = 0.02` at 5 kyr and `k_hs = 0.005` at 20 kyr both reach
`k_hs t = 100 m²` and agree to 1e-6 m, at ages differing fourfold.

## Parameters chosen here

- **Scarp height 5 m, face angle 30 degrees.** The angle is Andy's. The height
  is *a proposal*: large enough to read against a 240 m domain, small enough
  that a 1 m grid resolves the 8.7 m face.
- **Domain 240 m, 241 nodes.** *A proposal.* Wide enough that the ends stay
  flat over the demo's run, which matters because the closed form assumes an
  infinite surface. `Scarp.ends_are_quiet()` reports when that stops being
  true, rather than leaving it to be assumed.

## Not done

- The scarp cannot be re-cut while running; `reset()` returns it to `t = 0`.
- No background slope. Real scarp dating fits one, because a scarp cut across
  a sloping surface degrades to that slope rather than to the horizontal.
