# Proposed common calculation rules and nuclear-data treatment

Version: 0.1-proposed
Status: proposed for group review; not approved or implemented analytical rules.

## Purpose and relationship to existing documents

This supplement records calculation rules that were not fully specified in steps 06-08. Read it alongside geography_policy_proposed.md, proposed_scope_countries_timeframes.md and fedra_proposal_contribution.md. Those documents remain unchanged. Geography rules continue to apply. This document adds proposed calculation and nuclear-data rules; it does not approve the sample, establish feasibility, or claim that earlier scripts performed these calculations. It does not replace or reconcile the earlier root-level scope_rules.md automatically.

## Shared calculation rules

### C01 - Definitions, units and valid observations

Use the fixed project dataset snapshot. Confirm each indicator definition, unit, source, geographic coverage and accounting basis before combining fields. Primary energy consumption, electricity generation and energy production are not interchangeable. Required inputs must parse as finite numbers; blanks, nulls, NaN, infinity and invalid text are not valid measurements. Preserve genuine observed zero values. Flag implausible levels and outliers for review rather than automatically deleting or correcting them. Negative changes may be valid even when negative consumption levels require investigation.

### C02 - Absolute and percentage change

Absolute change = end_value - start_value, in the original unit. Percentage change = 100 * (end_value / start_value - 1), only when both values are valid, comparable and the start value is positive. A zero, negative or missing base does not produce an approved percentage growth value; record an explicit reason. A valid absolute change may still be reported from a zero base. Distinguish endpoint change from year-on-year growth. Year-on-year growth requires consecutive calendar years, not merely consecutive available rows. Do not label total period change as an annual rate.

### C03 - Share changes

When source shares use a 0-100 scale, percentage-point change = end_share - start_share. Do not multiply this difference by 100 again. For example, 20% to 25% is +5 percentage points; the relative increase is 25%. Confirm the scale before calculation. The renewable-share ranking in Analysis 4 uses percentage-point changes, with common endpoints and compatible definitions.

### C04 - Per-capita consumption

Use the provided per-capita field after checking its definition. For validation, if primary energy is in TWh and population is in persons: energy per capita (kWh/person) = primary_energy_consumption * 1,000,000,000 / population. Require positive population and matching entity/year coverage. Do not mix electricity-only numerators with total-energy per-capita measures. Preserve the supplied field and store any recalculation separately. Investigate differences in source, rounding or coverage before selecting a preferred measure.

### C05 - GDP growth and energy intensity

Confirm GDP currency, price basis, PPP treatment where applicable, and geographic coverage for the actual snapshot. If energy is in TWh and GDP is expressed in individual documented currency units, energy intensity = energy * 1,000,000,000 / GDP, in kWh per documented currency unit; adjust the conversion if GDP is scaled in millions or billions. Require positive GDP. The formula is conditional on definitions and is not proof that it reproduces energy_per_gdp. Energy intensity is distinct from GDP growth. Do not require energy_per_gdp for Analysis 5 unless the agreed method actually uses it. Compare GDP and energy growth over the same interval; do not infer real economic growth from an unverified nominal series.

### C06 - Samples, years and joint coverage

Use the same eligible entities and endpoints within each paired comparison. Compare total and per-capita rankings in the same reference year and sample. Annual trends require an explicit annual-coverage rule; valid endpoints alone do not establish a complete annual series. Do not silently substitute the nearest available year. A common sample across all five analyses versus analysis-specific samples remains a group decision. Report required variables, sample sizes, years and exclusion reasons. For sample-total trends, hold membership constant or explicitly disclose and assess membership changes. Do not impose an arbitrary completeness threshold merely to obtain a desired sample size.

### C07 - Sample totals, shares and weighting

For a sample energy share, use 100 * sum(source_consumption) / sum(primary_energy_consumption), with compatible units and definitions, the same entities and year in numerator and denominator, a positive denominator, and resolved geographic overlap. Do not divide a partial numerator by a denominator covering more entities. An unweighted mean of country shares is an average country share, not the sample energy share. Likewise, sample per-capita consumption uses total energy divided by total population; a simple mean of country per-capita values is a different statistic. Exclude aggregate labels from entity sums and label selected-sample totals accurately.

### C08 - Interpretation, rounding and reproducibility

Keep calculation precision and round only for presentation. Define validation tolerances explicitly with their units and justification. Do not silently clip shares, force components to sum to 100, or replace missing observations with zeros. Rank on unrounded values and document tie handling. Increasing renewable use or share does not by itself establish declining fossil use, emissions reductions or causal displacement. GDP-energy associations are not causal effects. Record the sample, formulas, source fields, exclusions and method version for reproducible implementation.

## Proposed nuclear-data treatment

### N01 - Keep nuclear separate from renewables

Represent nuclear separately when describing the energy mix. Do not add it to renewable consumption or renewable share. For this project, any use of low-carbon share as renewables plus nuclear must be supported by compatible definitions in the selected snapshot. Fossil and renewable categories alone must not be described as an exhaustive energy mix without checking nuclear and remaining coverage differences.

### N02 - Candidate derivation, not approved imputation

Candidate formula: derived_nuclear_share_energy = low_carbon_share_energy - renewables_share_energy. Both inputs must be valid shares with the same scale, denominator, source/accounting basis, entity and year. This estimates a share, not nuclear consumption in TWh. It must not be implemented as an approved replacement until Persons 2 and 3 validate the definitions and method and the group agrees. This script performs no derivation or imputation.

### N03 - Validation requirements

Before adoption, compare derived shares with observed nuclear shares for matched entity-years. Report the number compared, error distribution and maximum absolute discrepancy in percentage points; identify problematic entities/years and out-of-range results. Numerical agreement supports but does not prove definition compatibility. Establish and document a justified rounding tolerance; do not turn a previously observed maximum discrepancy into an automatically approved tolerance. Do not silently clamp negative values or values above 100.

### N04 - Preserve observations and identify derived values

Keep nuclear_share_energy unchanged. If derivation is approved, store it in a separate field and label the source fields, formula and method version. If an analysis-ready field combines observed and derived values, document the precedence rule and flag every value as observed, derived or unavailable. Missing direct nuclear data does not establish zero nuclear consumption. Do not derive a value when either required input is invalid or missing.

### N05 - Analysis-specific use and fallback

Nuclear treatment is particularly relevant to Analysis 1 and interpretation of Analysis 2. Analysis 4 remains a renewable-share comparison. Do not require complete direct nuclear observations for unrelated analyses. If derivation is not approved, use a transparently reported nuclear-specific sample or revise the mix presentation to disclose its incomplete coverage. Do not silently exclude otherwise eligible entities from every analysis.

## Preliminary evidence versus final eligibility

Earlier nonempty-cell coverage screens and numerical nuclear-share comparisons are preliminary evidence. This script does not reproduce or verify their counts or numerical results. A future validation run must state its exact variables, period, entity screen, missing-value definition and numeric-validity rules. Nonempty values alone do not establish valid joint coverage. The preliminary energy-intensity requirement must not automatically restrict the GDP-energy growth analysis.

## Review responsibilities and adoption gate

- Person 2: document snapshot-specific definitions, units, denominators and sources, including the proposed nuclear identity.
- Person 3: validate and implement agreed formulas, numeric checks, error handling and rounding tolerances; retain validation evidence.
- Person 4: assess analysis-specific joint coverage under the agreed rules and report the impact of alternative nuclear treatments.
- Fedra: align geographic eligibility, sample/timeframe recommendations and proposal wording with these findings.
- Group: approve choices and record the decision, evidence, reviewer and method version before final implementation.

Open decisions include the final periods and samples, any completeness thresholds, ranking tie handling, validation tolerances, use of energy intensity, and whether nuclear derivation is acceptable. Recording a proposal is not approval. Revise the source script and regenerate through a reviewed update rather than manually patching generated data.

## Documentation context

- General OWID energy-mix context: https://ourworldindata.org/energy-mix
- OWID energy-data documentation: https://github.com/owid/energy-data
These links provide context, not proof of the definitions in the older Kaggle snapshot. The script does not download or verify these pages. Snapshot-specific supporting evidence remains a required review item.

## Reproducibility

Generated by apps/09_record_calculation_rules.py. The rules are explicit proposed methodology written in this script. Existing Markdown inputs are checked for presence and recorded by hash only; this is not a semantic consistency audit. No raw data, numeric outputs, earlier documents or eligibility statuses are modified.

Input SHA256 values:
- geography_policy_proposed.md: a3710b1afad45a229b07b89229e576e272fbdf58147d873930886f0b9495c5e2
- proposed_scope_countries_timeframes.md: 0379f1aac9b7346cc9c7148bb34b15b89311f5de662ae31f48afb3e3ade95492
- fedra_proposal_contribution.md: f243b5a4b9d571ad18972783c0c0fbed1017867bd16bfbdbfc905c0cb55188ed
