# Changelog

All notable changes to this project are documented here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing released yet. The model runs, the test suite passes, and the browser
demo has been compiled and confirmed working — but there is no bedrock, no soil
thickness, and no weathering, so `Δz_u` cannot yet do the one thing that makes it
geomorphically interesting (design 05).

### Added

- `hillcreep.Hillslope`: a soil-mantled hillslope between two rivers. Soil
  creeps downslope at `u(x, ζ) = -K ∂z/∂x · exp(-ζ/H*)`, which integrates over a
  semi-infinite mobile layer to `q = -K H* ∂z/∂x`. `Hillslope.k_hs` is a
  read-only property returning `k_u·Δz_u`: `k_hs` is *reported*, never set.
- `hillcreep.River`: a channel setting base level at one end, with a prescribed
  incision rate (positive for incision, following the sign convention of Andy's
  2013 course script).
- `Hillslope.velocity_field(zeta)`: the velocity field beneath the surface, the
  thing `k_hs` is a summary of, as a separable outer product cheap enough to
  redraw every animation frame.
- `Hillslope.steady_profile()` and `steady_surface_velocity()`: the parabola the
  profile chases, and the surface velocity `E x'/H*` that mass balance forces —
  which does not depend on `k_u` at all.
- `interactive_demo/hillcreep_panel.py`: the `artesian` browser demo. Two
  stacked panels sharing an x-axis — topography above, the velocity field on its
  own depth axis below — with sliders for `k_u`, `Δz_u` and `ε̇`, and `k_hs` shown as a
  read-out.
- `examples/figure_two_panel.py`: the same figure as a static matplotlib
  rendering, parameterised on the command line.
- `design/01`–`design/05` and `prototypes/probe_a`–`probe_c`: a design document
  and a runnable probe behind each decision, with every quoted number produced
  by running the probe.

### Added later the same day

- **Aggradation, and fill terraces.** A negative incision rate fills the
  valley: the alluvial surface is a level set, ground below it is raised to it
  and held by the river, and the exposed hillslope genuinely shortens.
  Deposition is *permanent*, so when base level falls the fill stands above the
  new river level as a **fill terrace**, which then degrades diffusively like
  any other topography.
- `Hillslope.equilibrate()`, and a **Jump to equilibrium** button in the demo:
  impose the steady form instead of waiting out the 10⁵-year relaxation. Raises
  for a non-positive rate, where no steady form exists.
- The demo writes `k_hs = k_u × Δz_u` out with the current numbers substituted,
  and reports how much hillslope aggradation has buried.

### Known gaps

- No bedrock, no soil thickness, no weathering (design 05). The model therefore
  cannot show the saturation of `k_hs` once `Δz_u` exceeds the soil thickness, which
  is the behaviour that makes `Δz_u` matter to a geomorphologist.
- Left and right rivers share one rate, so the divide cannot migrate
  (design 03).
- **Slider combinations can reach indefensible slopes.** Each slider is bounded
  so that none alone produces one, but `E = 0.10 mm/yr` with `H* = 0.25 m`
  gives a steady toe slope of 1.0 (45°), where a linear creep law has no
  business. Nothing clamps and nothing warns: mass wasting is the right answer
  rather than a guard rail, and a threshold now would occupy its place
  (design 06).
