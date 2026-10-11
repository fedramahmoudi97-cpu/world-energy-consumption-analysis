# Proposed Project Scope Rules

Status: Draft for group review.
These rules guide the feasibility review; they do not establish the final sample.

## 1. Reference dataset
Use the unchanged World Energy Consumption.csv file.
The reference SHA256 is recorded in outputs/dataset_checksum.csv.
Do not combine this snapshot with a newer release without documenting
and reviewing the differences.

## 2. Unit of analysis
The intended unit is one country-level geographic entity in one year.
Review countries, territories, and other separately reported areas explicitly.
An ISO code alone does not establish eligibility.
A missing ISO code alone is not a reason for exclusion.

## 3. Geographic aggregates
Exclude World, continents, income groups, and multi-country aggregates
from the country comparison sample.
If used as contextual benchmarks, keep them separate from that sample.
Never add an aggregate to its constituent countries.

## 4. Geographic comparability
Flag historical entities, combined territories, and possible boundary changes
for review before inclusion.
Do not automatically merge predecessor and successor entities.
Record the reason for each inclusion, exclusion, or unresolved case.

## 5. Proposed period
Assess 2000–2018 as the initial common analysis period.
Confirm the period using the availability of the required energy and GDP data.
A row for a year does not establish that the required values are available.

## 6. Analysis-specific eligibility
For each of the five analyses, specify the required columns and years.
Assess their joint availability before selecting the final sample.
Distinguish analyses requiring annual series from endpoint comparisons.
Report the number of eligible entities and any differences between samples.

## 7. Missing values
Keep missing values distinct from observed zeros.
Do not replace missing values with zero to qualify an entity for analysis.
Document and validate any derived values before using them.

## 8. Interpretation
The project examines historical trends and associations.
It does not establish that renewable energy growth causes fossil fuel decline.
Findings from the selected sample must not be described as global findings
without evidence supporting that interpretation.