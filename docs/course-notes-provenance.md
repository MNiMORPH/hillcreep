# Where this model came from

`hillcreep` is not a new idea. It is one section of Andy's own Geomorphology
notes, made runnable — and the section it implements turns out to have been
published independently.

## The section

Andy Wickert's Geomorphology course notes (unpublished),
§"Explicit consideration of soils in hillslope transport". Motivated there by
Roger Hooke's Bevens Creek measurements (segmented wooden rods inserted in 1968
and excavated 9.5 years later), which show creep concentrated in the upper soil
and dying away downward. The notes take an exponential velocity profile,
integrate it over the mobile layer, and reach a slope- *and* thickness-
dependent flux.

The notes say of this: *"In answering this, I stray beyond most published
literature"*, with a footnote — *"I should publish this somewhere, or check if
someone else has."*

## It has been published

**Johnstone, S.A., and Hilley, G.E., 2015, Lithologic control on the form of
soil-mantled hillslopes: Geology, v. 43, p. 83–86, doi:10.1130/G36052.1**, and
it is implemented as Landlab's `DepthDependentDiffuser`. Term for term:

```
notes (sign-corrected):  q_m = -k_hs * Δz_u * (1 - e^(-h_m/Δz_u)) * dz/dx
Johnstone & Hilley:      q_s = -K    * H*   * (1 - e^(-H/H*))    * S
```

with `k_hs ↔ K`, `Δz_u ↔ H*`, `h_m ↔ H`. Landlab's docstring states the same
conclusion the notes reach: "the commonly used 'hillslope diffusivity'
coefficient is equal to the product of K and H*". The related depth–slope law
of Heimsath, Furbish & Dietrich (2005) is the `Δz_u → ∞` limit.

The derivation in the notes is sound and independently confirmed. What remains
unpublished, as far as this repo's reading goes, is nothing about the law — but
the *velocity field itself* is rarely if ever drawn, and that is what this model
puts on the screen.

## Two corrections carried over

Found while reading the notes for this model, verified numerically in
`/tmp` scratch work and reproduced here:

1. **A lost sign.** The notes correctly derive
   `q_m ∝ Δz_u (1 - e^((z_r - z)/Δz_u))` and correctly state `z_r - z = -h_m`,
   but the substituted equation reads `e^{+h_m/Δz_u}`. At `h_m = 20 m,
   Δz_u = 0.5 m` that gives `-1.18e17` instead of `0.5`: transport uphill, and
   diverging. The notes' own stated limit (`→ 1` as `h_m → ∞`) requires the
   corrected sign. The `h_m → 0` limit gives 0 either way, which is why it did
   not catch the error. **This model uses the corrected sign** — it is the only
   one consistent with the derivation above it and with Johnstone & Hilley.

2. **`k_hs` carrying two dimensions.** In the notes' Eq. `q_m` it is `[L²/T]`;
   in Eq. `q_m_RLBH` it multiplies `Δz_u` and so must be `[L/T]`. These are
   genuinely two different coefficients, which is why Landlab names the second
   `soil_transport_velocity`.

   **This model resolves it by introducing `k_u`** for the `[L/T]` coefficient,
   leaving `k_hs` as the diffusivity it is defined to be in the notes' Eq.
   `q_m`. `k_u` pairs with `Δz_u` — both subscripted for the velocity profile
   they describe — fits the notes' existing `k_x` family (`k_a`, `k_b`, `k_s`,
   `k_S`, `k_ω`, `k_{ε̇}`) without colliding with any of them, and makes

   ```
   k_hs = k_u * Δz_u
   ```

   read as the result it is. `k_u` is a proposal *for the notes*, arrived at by
   writing the model: code cannot let one name carry two dimensions, so the
   overload surfaced within minutes of implementation after sitting unnoticed
   in the TeX. That is an argument for settling notation against runnable
   models rather than on the page alone.

(A third error, in the Mohr–Coulomb mass-wasting section — an effective normal
stress omitting grain buoyancy, making saturated slopes a factor
`ρ_r/(ρ_r - ρ_w) ≈ 1.61` too stable — does not touch this model, which has no
mass wasting. It is recorded in the errata handed to Andy separately, and is
relevant here only as motivation for `design/06`.)
