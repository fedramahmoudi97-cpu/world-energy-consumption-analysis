# Proposed geographic scope policy

Policy version: 0.1-proposed
Status: proposed for group review; no final sample approved.

This document supplements the existing scope_rules.md draft. It does not overwrite that file or replace analysis-specific coverage checks. The rules are explicit project choices recorded in script 06; counts and exception details below are read from the existing project outputs.

## Proposed rules

### G01 - Unit of observation

Use one separately reported country or area in one year. Preserve the original dataset name and ISO field. Do not describe all candidate areas as independent countries. If areas are included, label the reported sample as countries and areas.

Basis: Project proposal; UN M49 countries-or-areas terminology [R1].

### G02 - Country and territory eligibility

Do not include or exclude an area solely because it is a territory, has an ISO code, or matches M49. Inclusion in an analysis requires a documented statistical area, adequate geographic consistency for that analysis, and the required valid measurements. Unresolved geography remains pending and cannot be marked eligible.

Basis: Project proposal informed by the limits of M49 [R1].

### G03 - Aggregates and double counting

Keep World, continents, income groups and other multi-area aggregates outside the entity-level comparison sample. They may be separately labelled benchmarks. Never add such an aggregate to its constituents. A sum of selected entities is a selected-sample sum, not automatically a global total.

Basis: Project proposal; existing script-02 inventory; OWID aggregate documentation [R2].

### G04 - Parent-area overlap and matching denominators

Check the source definitions for the specific indicator and years before jointly using a country total and a separately reported associated area. Political association alone neither proves nor rules out statistical overlap. Do not sum overlapping observations or treat an unresolved parent/area pair as independent observations in pooled analysis. Compare energy, population and GDP only when their geographic coverage is compatible. If unresolved, hold the affected entity-analysis combination pending; do not fabricate a subtraction or merge.

Basis: Project comparability rule; source-specific evidence must still be documented.

### G05 - Historical entities and changing boundaries

Keep predecessor and successor series separate. Do not concatenate or sum them to invent a continuous country series. A current name, code or a full set of year rows does not establish stable historical boundaries. Require a documented consistent series or an explicitly justified restriction of the period; otherwise hold the affected trend comparison pending. Existing exception proposals stay separate.

Basis: Project proposal; UN M49 historical changes [R1].

### G06 - Regional grouping

Use the saved M49 hierarchy as a fixed statistical grouping for this project. Preserve region, subregion and intermediate region as distinct levels. This reference is not a historical boundary concordance. Blank intermediate region can be legitimate and is not an exclusion criterion.

Basis: Project use of the M49 hierarchy [R1]; cached source and its metadata.

### G07 - Unmatched regional codes

Keep unmatched entities and flag them. Taiwan remains a separate dataset entity with its original TWN code; this step does not assign a region, replace its code, merge it with another entity, or exclude it. A later mapping must identify its source and be explicitly labelled as a project mapping. A missing region blocks region-based grouping until resolved, but does not by itself prevent other analyses.

Basis: Project handling rule; observed unmatched row and UN M49 FAQ [R1].

### G08 - Period and measurement coverage

Keep 2000-2018 as the proposed period until the required measurements are checked. Row availability is not measurement completeness. An entity with fewer than 19 year rows cannot enter a complete 19-year panel unchanged, but may qualify for an explicitly defined shorter-period or endpoint analysis. Do not equate blanks with zeros, infer independence dates from data availability, or backfill values merely to make an entity eligible.

Basis: Project proposal; script-05 evidence and pending Person-4 coverage assessment.

### G09 - Existing exceptions

Retain the separately recorded historical/special exceptions in the audit trail. Carry forward their proposed decisions and reasons without upgrading them to approved decisions. Kosovo is not rejected solely for a missing ISO field. Changing an exception proposal requires explicit documented review.

Basis: Project exception table generated/verified by script 03.

### G10 - Final selection and responsibilities

Final eligibility requires geographic suitability AND analysis-specific valid joint measurement coverage. Fedra prepares geography/period recommendations; Person 2 confirms definitions and units; Person 3 addresses structure, cleaning and calculation methods; Person 4 assesses joint coverage. The group agrees on the final scope. Report each analysis sample and its exclusions. No eligibility decision is automatically approved by running this script.

Basis: Proposed project workflow and the agreed preparation roles.

## Current evidence (not final eligibility)

- Initial geographic labels: 306.
- Aggregate labels in the existing draft: 77.
- Coded candidates retained: 217.
- Historical/special exceptions kept separately: 12.
- Candidates with all 19 year rows: 214.
- Candidates with incomplete year rows: 3.
- Exact M49 matches: 216.
- Unresolved regional mappings: 1.

### Incomplete year rows

| Dataset name | ISO code | Years present, 2000-2018 |
| --- | --- | --- |
| East Timor | TLS | 16 |
| Montenegro | MNE | 14 |
| South Sudan | SSD | 7 |

### Unresolved regional mappings

- Taiwan (TWN): preserve; apply G07.

### Existing exception proposals (unchanged)

| Dataset name | Proposed decision | Recorded reason |
| --- | --- | --- |
| Antarctica | exclude_from_main_country_comparisons | Non-comparable geographic unit for the proposed country-level study; population, per-capita energy, GDP and energy-mix measures are absent in the proposed period. Primary energy alone does not establish eligibility for the main sample. |
| Czechoslovakia | exclude_from_2000_2018_sample | No rows in the proposed period. Keep historical entity separate from Czechia and Slovakia; do not concatenate automatically. |
| East Germany (EIA) | exclude_from_2000_2018_sample | No rows in the proposed period. Do not combine this historical series automatically with Germany. |
| Hawaiian Trade Zone (EIA) | exclude_from_2000_2018_sample | No rows in the proposed period; the series ends in 1986. No need to resolve its exact historical geographic definition for this period. |
| Kosovo | retain_for_analysis_specific_review | Do not exclude solely because iso_code is missing. Primary and per-capita energy exist for part of the period; GDP and the selected fossil/renewable measures are absent. Not eligible for a common complete 2000-2018 five-analysis sample under these variables. A narrower total/per-capita comparison may be considered after source-definition and geographic-overlap review; retain the original blank ISO field. |
| Netherlands Antilles | exclude_pending_geographic_harmonization | Historical combined territory with a documented 2010 geographic change. Rows continuing to 2021 do not prove consistent boundaries. Exclude from the proposed main sample unless source definitions and harmonization are justified; GDP and energy-mix measures are also absent in 2000-2018. |
| Serbia and Montenegro | exclude_combined_entity_from_main_sample | Combined historical entity with only six rows in the proposed period, ending in 2005. Keep separate from Serbia and Montenegro; no automatic joining of predecessor and successor series. |
| USSR | exclude_historical_entity_from_main_sample | Historical combined entity. Although 19 year rows and GDP values exist, primary energy is absent throughout 2000-2018. Do not treat these rows as a contemporary country or infer energy-GDP feasibility from row presence. |
| Wake Island (EIA) | exclude_from_main_country_comparisons | Source-specific area series. Primary energy exists, but population, per-capita energy, GDP and energy-mix measures are absent in the proposed period. Do not count the EIA and Shift labels as two countries. |
| Wake Island (Shift) | exclude_from_main_country_comparisons | Source-specific area series with 17 year rows; selected primary energy, per-capita, GDP and energy-mix measures are absent. Do not count the Shift and EIA labels as two countries. |
| West Germany (EIA) | exclude_from_2000_2018_sample | No rows in the proposed period. Do not combine this historical series automatically with Germany. |
| Yugoslavia | exclude_from_2000_2018_sample | No rows in the proposed period. Do not concatenate the historical series with successor entities. |

## Outstanding evidence and next decision

This step records the policy; it has not audited every candidate boundary or resolved every associated-area overlap. In step 7, use indicator/source definitions and coverage results to resolve the entity-analysis cases that could enter the sample. For each unresolved case, retain the original name/code and record the affected indicator, years, evidence URL/version, proposed handling, reason and review status. Apply approved rules through code; do not patch generated CSV cells manually.

Until then, all candidates retain their pending status. The policy does not turn the list of 217 candidates into 217 confirmed countries.

## References and provenance

- [R1] UN Statistics Division, M49 methodology, hierarchy, historical changes and FAQ: https://unstats.un.org/unsd/methodology/m49/
- Saved M49 retrieval date: 2026-10-07.
- Saved M49 HTML SHA256: 4d5cabcb10ad9ef184553b5e64c0a34ba8deeb20dab2e02cd0be3599b93bb01d.
- [R2] OWID energy-data documentation: https://github.com/owid/energy-data. Consulted 2026-10-07 for general source/aggregate context only. Its current documentation is NOT proof of indicator definitions or area coverage in our older Kaggle snapshot.
- Dataset SHA256 recorded in the exception evidence: 00cd4b34da817f8cdb3af3558424be0d122aeea328156cf2d1f948e2158e48d7. Script 03 performs the raw-file hash check; this documentation step reads its record.
- Policy rules, candidate scope review and exception proposals are project materials, not official UN inclusion decisions.
