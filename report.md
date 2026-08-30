## 1. Introduction

The Hubble constant ($H_0$) measures the present rate of the expansion of the universe and is also a fundamental parameter in observational cosmology. Measurements of $H_0$ are often divided into two broad categories: early- and late-universe methods. Early-universe methods use observations that encode information about the early universe and infer $H_0$ within an assumed cosmological model. While late-universe methods directly measure the expansion rate of the local universe. However, with increasing precision in these measurements, the discrepancy between these two results has become statistically significant. 

This difference not only prompts us to make more precise measurements but also to delve deeper into how different measurement methods are constructed. Different methods are based on different principles and rely on different cosmological assumptions. Systematically tracing these differences, from observation to the final inference of $H_0$, helps identify potential systematic errors or model dependencies, thus providing clues to revealing the root causes of these discrepancies.

At the same time, organising these methods based on their observation and inference chain provides an intuitive way to understand how an $H_0$ value is measured. In addition to enabling systematic comparison among existing measurement approaches, this framework offers a practical reference for future observational studies.

The aim of this project is to construct a structured, common framework for the comparison of current methods for determining $H_0$. Rather than focusing on their final reported values of $H_0$, the framework characterises the observational-to-inference chain underlying each method. This is done by describing each method from physical principle, observation targets, facilities, required data products and physical quantities aspects. Additional fields such as redshift coverage, $H_0$ inference route and cosmological dependence summarise certain features of the methods. This should help identify measurement methods or observational directions with potential for future development, as well as bottlenecks that deserve focused improvement.

## 2. Database Construction

### 2.1 Overview

The database is constructed at the level of measurement methods rather than individual analyses. Specific papers using the same method may differ in sample selection, statistical treatment or detailed modelling. Recording every paper-specific choices will make systematic comparison between methods infeasible. This database therefore presents the characteristic measurement and intrinsic need of each meathod, hence representative papers were selected and analysed for each method.

The distance ladder is not treated as a single measurement method, because it does not correspond to a fixed observational procedure. Instead, it is an inference chain in which the indicators used at individual rungs can be replaced by alternative ones. In the distance ladder, each rung is calibrated using overlapping objects with the previous rung, allowing the absolute distance scale to be propagated to increasingly distant galaxies. Once a distance indicator is calibrated, it is applied to more distant galaxies to obtain luminosity distances and host-galaxy redshifts. The resulting distance-redshift relation, usually represented by a Hubble diagram, is then used to determine the Hubble constant $H_0$. 2 geometric anchors used in the distance ladder, 5 first-rung indicators and 5 second-rung indicators are listed individually in the database. This allows their different physical principles and observational ranges to be compared directly.

One of the main difficulties in constructing the database is that different methods uses different quantities and different papers use different terminologies. In order to review the measurement chain under a consistent framework, it is decomposed into several layers: principle, target, facility, data product, physical quantity and $H_0$ inference route. Several other fields: redshift range, cosmic epoch and cosmological model dependency\ describe the intrinsic features of each method. To ensure the same level of abstraction across methods, controlled vocabulary is used in the fields: principle, target, facility, data product, $H_0$ inference route, cosmic epoch and cosmological model dependence. The controlled vocabularies enable visualisation and direct method comparison. However, this categorisation will lose certain level of detail and the classification scheme always contains judgments.

### 2.2 Database Fields

The definition of each field that describes the methods are listed below.

| Field                   | Definition                                                   |
| ----------------------- | ------------------------------------------------------------ |
| Method                  | Name of the measurement method or distance indicator.        |
| Principle               | The fundamental physical basis that provides the cosmological information relevant to the determination of $H_0$. |
| Target                  | Astronomical object that is observed.                        |
| Facility                | Type of observational facility required.                     |
| Data Product            | Observational representation from which the relevant physical quantities are extracted. |
| Physical Quantity       | Physical quantity inferred or measured from the observational data. |
| $H_0$ Inference Route   | How the measured information contributes to the inference of $H_0$. |
| Redshift Range          | Redshift range directly used in published measurements or inferences of $H_0$. |
| Cosmic Epoch            | The cosmic epoch reached by observations used in an $H_0$ measurement or inference, classified according to the maximum redshift used. |
| Cosmological Dependence | Degree to which the inference relies on assumptions about cosmological physics or expansion history. |

The Target field is broadly divided into stars, galaxies, clusters, active galactic nuclei (AGN), transients, compact object mergers, cosmic wave background (CMB) and absroption systems.

The Facility field is classified first by messenger type. For electromagnetic (EM) observations, facilities are further distinguished by observing technique and wavelength band. The resulting categories are: GW: interferometer network, EM: radio band telescope / interferometer, EM: other band telescope / interferometer, EM: spectroscopic telescope and time-domain telescope. Radio-band facilities are separated from other EM facilities because radio observations commonly use coherent receiver systems and interferometric techniques, whereas observations at shorter wavelengths generally rely on direct photon or energy detection.

The Data Product field uses categories including image / photometry, datacube, light curve, spectrum, power spectrum and GW strain / phase.

The Redshift Range field is intended to indicate the broadest redshift range that has been explicitly used to infer $H_0$ in the literature. Because the literature search was representative rather than exhaustive, the quoted redshift ranges should not be considered as strict upper limits.

### 2.3 Classification Framework 

#### Principle

This field answers the question of where the physical scale or expansion information comes from.

| Category                 | Definition                                                   |
| ------------------------ | ------------------------------------------------------------ |
| geometric                | Absolute distance is derived from the geometry/dynamics of an individual system. |
| standard ruler           | A physical length scale is known, standardised or calibrated rather than being determined from the individual system. |
| standard candle          | The intrinsic luminosity is known, standardised or calibrated. |
| standard siren           | Absolute luminosity distance is inferred from the gravitational-wave signal. |
| standard clock           | Cosmic chronometer.                                          |
| accumulated-effect probe | Cosmological path-length or expansion information is encoded in a propagation effect accumulated along the line of sight. |

#### $H_0$ Inference Route

This field is useful because it prevents intermediate cosmological information, such as $H(z)$, from being obscured by reducing every method immediately to a single $H_0$ value. If a method is an indicator in the distance ladder, it is indicated in this field.

| Category                         | Definition                                                   |
| -------------------------------- | ------------------------------------------------------------ |
| integrated distance              | Constrains a cosmological distance, which encodes the expansion history through an integral, and $H_0$ is obtained using the distance-redshift relation. |
| differential expansion           | Constrains the expansion rate $H(z)$ directly; $H_0$ is inferred by extrapolating or fitting the expansion history to $z=0$. |
| accumulated effect inference     | A physical effect is accumulated along the line of sight whose redshift dependence encodes cosmological path-length or expansion information, from which $H_0$ is inferred. |
| global cosmological inference    | The observed data are compared with predictions from a full cosmological model, where $H_0$ is obtained simultaneously with other cosmological parameters through a global model fit. |
| distance ladder geometric anchor | A system whose distance is determined geometrically and is used to calibrate the absolute scale of the first-rung indicator. |
| distance ladder first rung       | A nearby indicator calibrated by geometric anchors, which is used to measure distances to more distant galaxies hosting second-rung indicators and thereby calibrate the second rung. |
| distance ladder second rung      | A more distant-reaching indicator calibrated by the first rung, which extends into the Hubble flow and is used to infer $H_0$ through the D-z relation. |

#### Cosmic Epoch

This field provides a simplified description of the redshift range. The boundaries are set at $z=0.15$ and $z=6$. Since $z=0.15$ approximately corresponds to the upper redshift limit commonly adopted for Hubble-flow SNe Ia in distance ladder, while $z=6$ roughly marks the end of the epoch of reionisation.

| Category              | Definition       |
| --------------------- | ---------------- |
| local universe        | $z_{max}<0.15$   |
| intermediate redshift | $0.15<z_{max}<6$ |
| high redshift         | $z_{max}>6$      |

#### Cosmological Model Dependence

This classification refers to the modelling required to translate the measured observables into $H_0$, rather than to the statistical precision or reliability of the method. Categories are assigned according to the intrinsic requirement of each method rather than to the modelling choices adopted in individual papers. 

Methods in the 'no' category do not intrinsically require a specific dynamical cosmological model. When their relevant redshift range is sufficiently low, $H_0$ can in principle be inferred directly from the linear Hubble relation, $, or using a local cosmographic expansion $d_L(z)= \frac{c}{H_0} \left[z+ \frac{1-q_0}{2}z^2 - \frac{1-q_0-3q_0^2+j_0+\Omega_k}{6}z^3 + \mathcal{O}(z^4) \right]$ with parameters obtained by data fitting. 

For the methods in the 'weak' category, a dynamical expansion model, commonly of the form $H(z) = H_0 \sqrt{ \Omega_m(1+z)^3 + \Omega_\Lambda}$, is required to extrapolate measurements at finite redshift to $H_0$. The fast radio burst (FRB) dispersion measure-redshift (DM-z) method also requires an externally constrained cosmological parameter $\Omega_b$. However, as $\Omega_b$ has a direct physical interpretation and is independently constrained by multiple observational probes, this is classified as weak-dependence. 

The 'strong' dependence methods (e.g. cosmic microwave background (CMB)) have more direct use of early-universe physics than the 'medium' dependence method (e.g. baryon acoustic oscillations (BAO) + Big Bang Nucleosynthesis (BBN)). These categories broadly encompass methods commonly described in the literature as early-universe method.

| Category | Definition                                                   |
| -------- | ------------------------------------------------------------ |
| no       | No specific dynamical cosmological model is required; relies only on FLRW kinematics / local cosmography. |
| weak     | Requires assumptions about the late-time expansion history and/or externally constrained cosmological parameters ($\Omega_b$). |
| medium   | Uses a physical scale from pre-recombination physics.        |
| strong   | Directly fits observables generated by early-universe physics using a detailed cosmological model. |

## 3. Results

### 3.1 Interpretation

Despite the diversity of observational techniques, many late-universe measurements can be understood in terms of obtaining information about cosmological distance and comparing it with redshift or recession velocity. The database makes the route by which this information is obtained explicit.

The distinction between integrated distance and differential expansion is particularly useful. An 'integral distance' measurement constrains a quantity such as luminosity or angular-diameter distance, which depends on the integral of expansion history. 'Differential expansion' probes constrain the differential expansion rate $H(z)$ more directly. Measurements classified as 'differential expansion', including cosmic chronometers and the BAO+BBN method, do not necessarily need to be reduced immediately to a single value of $H_0$. Instead, their $H(z)$ measurements can be compared directly, preserving more redshift-dependent information and avoiding the need to assume a late-time expansion model. Specifically, the consistency between their $H(z)$ profiles can be evaluated by direct comparison, and any disagreement can be traced to either normalisation factors (corresponding to the $H_0$ value) or intrinsic shape (corresponding to the expansion history).

Several methods and distance indicators can extend the observational redshift range well beyond the range reached by the conventional distance ladder. HII galaxies and gamma-ray bursts (GRB) are two examples; the former have strong emission lines, and the latter have high luminosity, which enable them to remain detectable at high redshift. However, at increasing redshift, the relation between the measured distance and the present value $H_0$ becomes more sensitive to the assumed form of the expansion history. Therefore, high-redshift tracers are valuable as tests of consistency of the expansion history across redshift.

It is also worth mentioning that the two indicators mentioned are standardisable candles which require calibration. Though they are not usually considered as part of the distance ladder, GRBs are often calibrated by SNe Ia or cosmic chronometers, and HII can be anchored by nearby giant HII regions. These calibration processes will introduce extra systematic uncertainties and dependencies. Methods are not automatically independent simply because they are not normally labelled as components of the conventional distance ladder. A related issue occurs for methods that share physical scales; to be specific, CMB and BAO+BBN methods. These measurements are observationally very different, but both use a standard ruler from pre-recombination physics.

These dependencies suggest that a promising method is not the one which can achieve the smallest uncertainty, but the one that can provide decisive precision while being independent in the means of calibration, systematic errors, inference chain and cosmological model dependence.

### 3.2 Interactive Website

## 4. Limitations

The database prioritises structure and consistency in method description, hence loses details and simplifies the methods. Specific analysis choices vary across papers, which may make the value of certain fields, like cosmological model dependence, vary slightly, and this database only focuses on the intrinsic features of the method.

The use of controlled vocabularies introduces a second level of simplification. Broad categories make systematic comparison and visualisation feasible while sacrificing some level of detail. Some classifications also require judgement. Boundaries between categories such as 'no', 'weak', 'medium' and 'strong' are not fundamental divisions in nature.

A more important limitation is that the current framework lacks the assessment of astronomical model dependence. Examples include lens-mass modelling in the strong lensing time delay method, supernova atmosphere modelling in the expanding photosphere method (EPM), and the galaxy free electron density model in the DM-z relation method. Several independent methods have their precision and accuracy limited by the astronomical model used. Future work should assess the validity and robustness of the astronomical model used, which will provide constructive insight into which methods are more promising.

## 5. Conclusion

This project constructed a structured framework for comparing the existing methods used to determine $H_0$. Instead of concentrating on the final reported values of $H_0$, the framework decomposes each method into a common observation-to-inference chain, including its principle, target, facility, data product, physical quantities and $H_0$ inference route. Additional characteristics, such as redshift coverage and cosmological model dependence, make the comparison between methods more diagnostically informative. The resulting framework highlights the importance of evaluating the full measurement chain particularly on the calibration and inference route. With future work incorporating astrophysical model dependence and the dominant sources of systematic uncertainty, the framework could provide a more complete assessment of each method, helping to identify the most promising directions for future $H_0$ observations.



