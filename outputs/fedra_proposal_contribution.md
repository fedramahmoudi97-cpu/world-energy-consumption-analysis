# Fedra's proposal contribution - draft for group review

Status: consolidated draft for group review; not a complete group proposal or a final sample decision.

## Problem definition and purpose

Renewable energy consumption can increase while fossil fuel consumption also rises, and a falling fossil fuel share does not necessarily indicate a reduction in its absolute use. Using the World Energy Consumption dataset, we propose to examine renewable and fossil fuel consumption changes alongside changes in total primary energy consumption. Total volume, consumption per person and source composition answer different questions; per-capita comparisons and the association between GDP growth and energy-consumption growth provide supporting context. The purpose is to provide reproducible, comparable descriptive evidence while making data coverage and geographic limitations explicit.

## Main research question

Is growth in renewable energy consumption accompanied by a decline in fossil fuel consumption, or do both increase alongside rising total primary energy consumption?

## Proposed scope

We propose 2000–2018 as the initial study period, using one fixed World Energy Consumption dataset snapshot. The unit of observation is a separately reported country or area in a year. Inclusion will require geographic comparability and valid joint observations for each analysis. Aggregate labels will remain outside entity-level comparisons and may be used only as separately identified benchmarks where appropriate. Overlapping areas and historical boundaries will be reviewed without automatically merging predecessor and successor series. The final period and the choice of a common or explicitly documented analysis-specific sample will follow the group’s definition and coverage checks.

## Proposed methods

The five analyses will examine annual consumption and energy mix, renewable and fossil consumption changes, total versus per-capita rankings, percentage-point increases in renewable share, and GDP–energy growth over matching periods. Nuclear energy will remain separate from renewables. Any nuclear share derived from low-carbon minus renewable share will require snapshot-compatible definitions, numerical validation and explicit labelling; otherwise, we will disclose a narrower nuclear sample or incomplete mix coverage. Missing observations will not be treated as zero. GDP comparisons will use a verified, consistent price and currency basis; energy intensity will be optional rather than an automatic condition for the growth analysis.

## Connection to the five planned analyses

The analytical questions below retain the wording in the updated contribution. Analysis 2 directly addresses the main research question; the other analyses provide supporting context. All five remain subject to variable-definition and joint-coverage checks.

| Analysis | Proposed analytical question | Contribution and interpretation |
| --- | --- | --- |
| 1. Consumption trends and energy mix | How have total primary energy consumption and the shares of fossil fuels, renewables and nuclear energy changed over the study period? | Establishes the scale and composition of observed change. |
| 2. Renewable and fossil changes | Where has renewable energy consumption increased while fossil fuel consumption declined, remained approximately stable or increased, and how did total primary energy consumption change alongside them? | Distinguishes co-occurring patterns; does not establish that renewables caused fossil displacement. |
| 3. Total versus per-capita consumption | How do energy-consumption rankings differ when the same countries and areas are compared using total primary energy consumption and consumption per person? | Shows how comparisons change after population normalisation; does not establish that population alone explains energy consumption. |
| 4. Renewable share increases | Which eligible countries and areas experienced the largest percentage-point increases in renewable energy’s share of total primary energy consumption? | Compares endpoint changes in composition, complementing Analysis 1’s annual trends; a share increase alone does not establish an absolute decline in fossil use. |
| 5. GDP and energy growth | How is GDP growth associated with growth in total primary energy consumption over the same period? | Provides economic context for changes in total primary energy consumption, without claiming causation or identifying its mechanisms. |

## Limitations to retain in the proposal

Comparisons will depend on valid joint coverage of the required variables, compatible units and geographic definitions, and comparable years. Complete year rows and regional reference matches do not establish analytical eligibility. Missing observations, changing boundaries and possible overlap between separately reported areas may restrict the sample or timeframe. Any analysis-specific samples will be reported explicitly. The findings will describe the selected observations and associations. They will not establish causal fossil displacement, global representativeness, emissions reductions or policy effectiveness. The proposal will state unresolved feasibility decisions clearly, and final comparisons will use consistent entities, periods, units and calculation rules.

## Group integration and remaining decisions

- Fedra: resolve affected geographic cases with source evidence and update scope recommendations when the other reviews are available.
- Person 2: confirm dataset documentation, variable definitions, units and applicability to the fixed dataset snapshot.
- Person 3: confirm structural checks, cleaning choices and calculation methods.
- Person 4: assess valid joint coverage and feasibility for each of the five analyses.
- Group: agree on the final entities, periods and sample strategy, and confirm consistent use of the agreed question wording before submission.
- Retain the candidate NiFi ingestion -> HDFS storage -> Spark/PySpark preparation and calculations -> Hive analytical-query workflow. Confirm implementation responsibilities and its mapping to at least four course lectures against the course guidelines; this draft does not verify that requirement.

For the short group proposal, use the problem definition, main question and a concise scope/limitations passage. The analysis table and integration notes support editing and coordination; this entire document is not intended to be pasted into the proposal. The dataset and methods sections must be integrated with the other members' contributions.

## How this document was prepared

This document is generated by apps/08_record_proposal_contribution.py from the consolidated editorial wording of the two contribution drafts. It retains the updated main research question, five analytical questions and proposed methods, while restoring useful explanations of purpose, benchmark treatment and coverage limitations from the earlier version. No energy results, new country selections or missing-data calculations are produced. Source definitions and feasibility remain subject to the reviews above.

The script reads outputs/proposed_scope_countries_timeframes.md and outputs/geography_policy_proposed.md, checks the expected draft structure, provisional status, period marker and geography-rule headings, and records their SHA256 values below. These checks do not validate the underlying data or approve analytical eligibility. The proposal scope wording is recorded in this script rather than copied from the older step-07 paragraph. The generated output is outputs/fedra_proposal_contribution.md. This update does not modify script 07, the Group Review document or the preparation inputs.

Input SHA256 values:
- proposed_scope_countries_timeframes.md: 0379f1aac9b7346cc9c7148bb34b15b89311f5de662ae31f48afb3e3ade95492
- geography_policy_proposed.md: a3710b1afad45a229b07b89229e576e272fbdf58147d873930886f0b9495c5e2
