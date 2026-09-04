# Hubble Constant Measurement Methods

## Explore Online

[**Open the H₀ Interactive Explorer →**](https://zhnicex.github.io/hubble-constant-measurement-methods/)

The explorer lets users filter measurement methods by cosmic epoch, astronomical target, observing facility, and $H_0$ inference route, and inspect the observation-to-inference chain for each method.

## Introduction

Measurements of the Hubble constant ($H_0$) obtained using early- and late-universe methods do not fully agree, a discrepancy commonly referred to as the Hubble tension. Understanding this discrepancy requires examining the measured $H_0$ values in the context of each method's observation-to-inference chain, calibration route, and model dependence. Organising these methods in a structured database provides an intuitive account of how $H_0$ is measured and a consistent basis for comparison.

A broad literature search was conducted to identify as many $H_0$ measurement methods as practicable. For each method, representative papers were selected to reconstruct the characteristic observation-to-inference pipeline. These method-level summaries were then standardised using a common set of fields and controlled vocabularies, and compiled into a structured database. This database is intended to serve as a reference for observational studies and to help identify promising methods and limitations for future research.

## Database

This database currently contains 29 measurement methods and distance ladder indicators.

Each method is described using the following fields.

| Field                         | Definition                                                   |
| ----------------------------- | ------------------------------------------------------------ |
| Method                        | Name of the measurement method or distance indicator.        |
| Principle                     | The fundamental physical basis that provides the cosmological information relevant to the determination of $H_0$. |
| Target                        | Astronomical object that is observed.                        |
| Facility                      | Type of observational facility required.                     |
| Data Product                  | Observational representation from which the relevant physical quantities are extracted. |
| Physical Quantity             | Physical quantity inferred or measured from the observational data. |
| $H_0$ Inference Route         | How the measured information contributes to the inference of $H_0$. |
| Redshift Range                | Redshift range directly used in published $H_0$ measurements or inferences when available; otherwise, the forecast redshift range for methods not yet applied to $H_0$ measurements. |
| Cosmic Epoch                  | The cosmic epoch reached by observations used in an $H_0$ measurement or inference, classified according to the maximum redshift used. |
| Cosmological Model Dependence | Degree to which the inference relies on assumptions about cosmological physics or expansion history. |

The classification framework for *Principle*, $H_0$ *Inference Route* and *Cosmological Model Dependence* is outlined below.

*Principle*:

| Category                 | Definition                                                   |
| ------------------------ | ------------------------------------------------------------ |
| geometric                | Absolute distance is derived from the geometry/dynamics of an individual system. |
| standard ruler           | A physical length scale is known, standardised or calibrated rather than being determined from the individual system. |
| standard candle          | The intrinsic luminosity is known, standardised or calibrated. |
| standard siren           | Absolute luminosity distance is inferred from the gravitational-wave signal. |
| standard clock           | An absolute age or a standardisable differential age interval is inferred from astrophysical evolution. |
| accumulated-effect probe | Cosmological path-length or expansion information is encoded in a propagation effect accumulated along the line of sight. |

$H_0$ *Inference Route*:

| Category                       | Definition                                                   |
| ------------------------------ | ------------------------------------------------------------ |
| integrated expansion history   | Constrains an integrated quantity (e.g. distance), whose redshift dependence encodes the accumulated expansion history along the line of sight, and infers $H_0$ through its relation to the expansion history. |
| differential expansion history | Constrains the expansion rate $H(z)$ directly; $H_0$ is inferred by extrapolating or fitting the expansion history to $z=0$. |
| global cosmological inference  | The observed data are compared with predictions from a full cosmological model, where $H_0$ is obtained simultaneously with other cosmological parameters through a global model fit. |
| distance ladder                | Determines $H_0$ by propagating an absolute distance calibration through a sequence of overlapping distance indicators, from geometric anchors to Hubble flow indicators. |

*Cosmological Model Dependence*:

| Category | Definition                                                   |
| -------- | ------------------------------------------------------------ |
| no       | No specific dynamical cosmological model is required; relies only on FLRW kinematics/local cosmography. |
| weak     | Requires assumptions about the late-time expansion history or externally constrained $\Omega_b$. |
| medium   | Uses a physical scale from pre-recombination physics.        |
| strong   | Directly fits observables generated by early-universe physics using a detailed cosmological model. |

See the full [project report](https://github.com/zhnicex/hubble-constant-measurement-methods/blob/main/report.md) for details of the database construction, including classification framework and rationale, results and discussion.

## Interactive Explorer

This database is visualised through the [interactive web-based explorer](https://zhnicex.github.io/hubble-constant-measurement-methods/). The interactive explorer allows users to:

* explore methods by using filters for cosmic epoch, target, facility and $H_0$ inference route;
* search for a method by name;
* view the observation-to-inference network for each method consisting of its target, facility, data product, physical quantities and $H_0$ inference route;
* view the physical principle, cosmic epoch, cosmological model dependence, details and references for individual methods;
* compare methods using the shared controlled vocabulary nodes in the network.

## Limitations

This database has several limitations, in particular:

* It is not an exhaustive summary of $H_0$ measurement methods.
* Methods are summarised at the method level rather than at the level of individual analyses, while specific analysis choices may vary across papers.
* Organising heterogeneous methods within a shared framework and controlled vocabulary necessarily removes some methodological details.
* Some classifications require judgement; for instance, the categories used for *Cosmological Model Dependence* do not represent fundamental divisions in nature.
* The reported redshift ranges are not strict upper limits and may change as observations and methods advance.
* The current framework lacks assessment in astrophysical model dependence.

Future work could assess the validity and robustness of the astronomical model used, helping to identify which methods are more promising.

## Acknowledgements

The interactive visualisation and data-processing scripts were developed with assistance from AI tools.

The cosmic-timeline background used by the interactive explorer is adapted from the “Timeline of the Universe” illustration on NASA’s [WMAP Overview](https://science.nasa.gov/mission/wmap/wmap-overview/) page. Credit: NASA / WMAP Science Team.

## Contributing

Feedback and new ideas are welcome. Please [open an issue](https://github.com/zhnicex/hubble-constant-measurement-methods/issues) to report a problem or suggest an idea.