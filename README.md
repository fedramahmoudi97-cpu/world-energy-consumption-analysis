# World Energy Consumption Analysis

TMU DS8003 — Big Data Management group project.

## Project question and current status

**Is growth in renewable energy consumption accompanied by a decline in fossil fuel consumption, or do both increase alongside rising total primary energy consumption?**

This repository contains the preparation environment, geographic review scripts, supporting outputs and proposed methodology. It does not yet contain the five completed analytical findings or an approved final sample.

The current Compose configuration runs **one Spark container in local mode**. NiFi ingestion, HDFS storage and Hive analytical queries belong to the proposed wider workflow; those services are not configured by this Compose file. Their implementation and mapping to course requirements remain group decisions.

The initial proposed study period is **2000–2018**, with one separately reported country or area per year. Coverage and comparability checks may justify a different period or explicitly documented analysis-specific samples.

## Repository structure

Paths below are relative to the project root, beside `docker-compose.yml`. Use these exact filenames, without download suffixes such as `(1)`.

| Path | Purpose |
| --- | --- |
| `README.md` | Setup, execution order and collaboration guide |
| `docker-compose.yml` | Spark container, mounts and local UI port |
| `conf/spark-defaults.conf` | Spark execution settings |
| `apps/` | Numbered preparation scripts `00`–`09` |
| `outputs/` | Generated review tables, methodology documents, checksum and cached geographic-source evidence |
| `scope_rules.md` | Earlier scope draft; read alongside later proposed rules, not as an automatically reconciled master document |
| `data/World Energy Consumption.csv` | Unchanged local dataset; deliberately not included in this repository |
| `data/geography_candidate_region_reference.csv` | Local input for step 05, copied from step 04's output |
| `warehouse/` | Local Spark warehouse directory; runtime contents are not project source code |

Create `data/` and `warehouse/` locally if absent. Each member runs their own environment; the repository shares code and configuration, not a running container.

## Obtain and verify the dataset

1. Open the professor's dataset source: [World Energy Consumption on Kaggle](https://www.kaggle.com/datasets/pralabhpoudel/world-energy-consumption).
2. Download and extract **World Energy Consumption.csv**, then place it at `data/World Energy Consumption.csv`.
3. Verify its SHA256 against `outputs/dataset_checksum.csv` **before running the preparation scripts**.

The agreed snapshot has this SHA256 (letter case does not matter):

```text
00cd4b34da817f8cdb3af3558424be0d122aeea328156cf2d1f948e2158e48d7
```

In PowerShell, from the project root:

```powershell
(Get-FileHash -LiteralPath '.\data\World Energy Consumption.csv' -Algorithm SHA256).Hash
```

On macOS use `shasum -a 256 "data/World Energy Consumption.csv"`; on Linux use `sha256sum "data/World Energy Consumption.csv"`.

**A download with the same filename is not necessarily the same snapshot.** If the hash differs, stop and ask Fedra for the unchanged project copy through the group's shared Drive folder. Do not edit the expected hash or substitute a newer OWID release merely to make the checks pass. The exact Kaggle version identifier and a direct shared-copy link still need to be recorded by the group; the hash currently identifies the required bytes.

Keep the CSV unchanged, including its encoding and line endings. Do not open and resave the raw file through a spreadsheet editor. Keep raw data out of commits; check staged files before committing and exclude `data/World Energy Consumption.csv` in `.gitignore` if that rule is not already present.

The [OWID energy-data repository](https://github.com/owid/energy-data) provides documentation context. Its current definitions must be checked for compatibility with the selected Kaggle snapshot.

## Start Docker and Spark

Install and start Docker Desktop with Linux containers and Docker Compose v2. Git is needed if using a local clone; downloading the appropriate branch as a ZIP is also possible. A separate host installation of Spark, Java or PySpark is not needed for the commands below.

Use a terminal in the project root. The examples below use PowerShell; the `docker compose` commands also work in a Unix shell.

```powershell
New-Item -ItemType Directory -Force -Path data, outputs, warehouse | Out-Null
Test-Path '.\conf\spark-defaults.conf'
docker --version
docker compose version
docker compose config
docker compose pull spark
docker compose up -d spark
docker compose ps
```

`Test-Path` must return `True`. Review any configuration error before proceeding. Download the dataset and check its hash before running step 00.

| Setting | Current project value |
| --- | --- |
| Compose project / service | `ds8003-energy` / `spark` |
| Container | `energy-spark` |
| Image | `apache/spark:3.5.9-scala2.12-java17-python3-r-ubuntu` |
| Spark master | `local[2]` |
| Driver memory | `2g` |
| Shuffle partitions / session timezone | `4` / `UTC` |
| UI mapping | `127.0.0.1:4041` on the host to `4040` in the container |
| Read-only mounts | `data/`, `conf/spark-defaults.conf` |
| Writable mounts | `apps/`, `outputs/`, `warehouse/` |

The container waits for commands; starting it does not automatically run an analysis. Run the environment check:

```powershell
docker compose exec spark /opt/spark/bin/spark-submit /opt/spark/apps/00_check_environment.py
```

It prints the Spark version, master, dataset dimensions and example geography keys. Successful loading is not a validation of every measurement.

The [Spark UI](http://localhost:4041) is available while a Spark application is running. The short preparation scripts stop their sessions when finished, so an unavailable UI afterward is expected. Run jobs sequentially in this container.

To stop the environment:

```powershell
docker compose stop spark
```

## Preparation sequence

Review existing outputs before rerunning: some scripts overwrite their generated tables, while others refuse to replace differing files. Keep manual decisions separately and review changes before committing generated outputs.

| Step | Script | Runner | Main result |
| --- | --- | --- | --- |
| 00 | `00_check_environment.py` | Spark | Console environment and data-loading check |
| 01 | `01_scope_inventory.py` | Spark | `geography_year_inventory.csv` |
| 02 | `02_build_geography_review.py` | Spark | `geography_scope_review_draft.csv` |
| 03 | `03_build_exception_decisions.py` | Python | `geography_exception_decisions_proposed.csv`, `dataset_checksum.csv` |
| 04 | `04_build_region_reference.py` | Python | `geography_candidate_region_reference.csv`, `un_m49_source.html`, `un_m49_source_metadata.json` |
| 05 | `05_build_candidate_scope_review.py` | Spark | `geography_candidate_scope_review.csv` |
| 06 | `06_record_geography_policy.py` | Python | `geography_policy_proposed.md` |
| 07 | `07_record_proposed_scope.py` | Python | `proposed_scope_countries_timeframes.md` |
| 08 | `08_record_proposal_contribution.py` | Python | `fedra_proposal_contribution.md` |
| 09 | `09_record_calculation_rules.py` | Python | `common_calculation_rules_proposed.md` |

All result filenames in the table are inside `outputs/`. The canonical numbering is **03 = exceptions, 04 = region reference**. Use the commands listed below.

After step 00 succeeds, run each command in order and stop if it reports an error:

```powershell
docker compose exec spark /opt/spark/bin/spark-submit /opt/spark/apps/01_scope_inventory.py
docker compose exec spark /opt/spark/bin/spark-submit /opt/spark/apps/02_build_geography_review.py
docker compose exec spark python3 /opt/spark/apps/03_build_exception_decisions.py
docker compose exec spark python3 /opt/spark/apps/04_build_region_reference.py
```

**Required handoff before step 05:** inspect the generated reference and copy it on the host. The container's `data/` mount is read-only.

```powershell
Copy-Item -LiteralPath '.\outputs\geography_candidate_region_reference.csv' -Destination '.\data\geography_candidate_region_reference.csv'
```

On macOS/Linux the equivalent is `cp outputs/geography_candidate_region_reference.csv data/geography_candidate_region_reference.csv`. If a local destination already exists, compare it first; this handoff should use the reviewed step-04 result.

Then continue:

```powershell
docker compose exec spark /opt/spark/bin/spark-submit /opt/spark/apps/05_build_candidate_scope_review.py
docker compose exec spark python3 /opt/spark/apps/06_record_geography_policy.py
docker compose exec spark python3 /opt/spark/apps/07_record_proposed_scope.py
docker compose exec spark python3 /opt/spark/apps/08_record_proposal_contribution.py
docker compose exec spark python3 /opt/spark/apps/09_record_calculation_rules.py
```

Step 04 uses the [official UN M49 geographic reference](https://unstats.un.org/unsd/methodology/m49/). Preserve the cached HTML and metadata together to reproduce the source context. Without a usable cache, the script may need internet access; a newer source can change outputs and downstream provenance. A current regional match is not proof of historically consistent boundaries or analytical eligibility.

### Reruns and version consistency

- Steps 01, 02 and 04 write generated tables. Review any changes before committing.
- Steps 03 and 05–07 protect differing existing outputs. A mismatch requires review, not automatic deletion of the previous work.
- The updated step 08 writes **`fedra_proposal_contribution.md`**, without `_draft`. Its `--replace-existing` option preserves a SHA256-labelled backup before replacing a differing output; use it only after reviewing the intended changes.
- Step 09 must read that same current filename. The synchronized version accompanying this README fixes the earlier `_draft` reference and regenerates the calculation-rules document with current input hashes. Its analytical rules are unchanged.
- Step 09 also protects differing existing output. If regeneration is needed after a reviewed input change, preserve the old document outside its output path, then rerun and review the regenerated document. Do not keep an obsolete `_draft` copy just to satisfy an outdated dependency.
- Update a document's source script and regenerate it together; do not leave generated Markdown inconsistent with its script. Older planning documents may still mention the former output name.

## Planned analyses and open decisions

These are questions to investigate, not completed findings:

| Analysis | Purpose |
| --- | --- |
| 1. Consumption trends and energy mix | Track total primary energy and fossil, renewable and nuclear shares over time |
| 2. Renewable and fossil consumption changes | Directly address the main question using absolute changes alongside total demand |
| 3. Total versus per-capita consumption | Compare the same eligible locations in the same reference year |
| 4. Renewable-share change | Rank comparable endpoint changes in percentage points |
| 5. GDP and energy growth | Compare growth over matching periods; energy intensity is optional supporting context |

Read [Fedra's contribution](outputs/fedra_proposal_contribution.md), [geography policy](outputs/geography_policy_proposed.md), [proposed scope](outputs/proposed_scope_countries_timeframes.md) and [calculation and nuclear rules](outputs/common_calculation_rules_proposed.md).

The following remain proposed or require documented confirmation:

- Final countries/areas, treatment of overlap and historical boundaries, study period and annual-coverage requirements.
- Common versus analysis-specific samples; valid joint coverage for each analysis. A row or nonempty cell does not establish a valid measurement.
- Snapshot-specific indicator definitions, units, GDP price/currency/PPP basis and any scaling.
- Reference year for rankings, tie handling, “approximately stable” thresholds and numerical-validation tolerances.
- Whether to derive nuclear share as `low_carbon_share_energy - renewables_share_energy`. This is a candidate method requiring compatible definitions, numerical validation and group agreement; it is not approved imputation. Nuclear stays separate from renewables.
- Whether to include energy intensity and how to validate it without unnecessarily restricting Analysis 5.
- Final course-tool workflow, implementation responsibilities and lecture mapping.

Keep missing values distinct from observed zeros. Use comparable entities and years within paired comparisons. Report renewable-share changes in percentage points. Do not infer causal displacement, emissions reductions, policy effectiveness or global representativeness from these descriptive comparisons.

Rules G01–G10, C01–C08 and N01–N05 document proposals. Recording them does not mean they have been approved or that the five analyses have been implemented.

## Group workflow and pull requests

Each member works on their own branch. Keep `main` for reviewed, integrated work.

1. Add changes to your assigned branch, including the relevant code and regenerated outputs together.
2. Review the file diff: exclude the raw dataset, local warehouse contents and temporary/backup files.
3. Include input identity, commands actually run, observed results and remaining limitations in the pull request.
4. Open the pull request with **base `main`** and **compare your working branch**. Request group review before merging and follow the repository's configured rules.
5. Record analytical decisions with the evidence, reviewer and method version; code integration does not itself approve proposed methods.

Suggested README commit title: `docs: add project setup and collaboration guide`.

For the related dependency fix, use a separate commit: `fix: align step 09 with current proposal filename`.

## Troubleshooting and validation status

| Symptom | Check |
| --- | --- |
| Compose cannot find configuration | Run from the directory containing `docker-compose.yml` |
| Dataset not found | Check the exact filename and `data/` location, then verify the hash |
| Raw snapshot mismatch in step 03 | Obtain the agreed bytes; do not change the expected hash |
| Reference missing in step 05 | Complete the host-side copy from `outputs/` to `data/` |
| Step 09 asks for `_draft.md` | Replace the outdated step-09 script with the synchronized version |
| Existing-output mismatch | Review provenance and content changes; preserve the prior version before regeneration |
| `energy-spark` name or port conflict | Check for another copy of this environment; do not remove unrelated containers |
| UI unavailable after a job | Spark may already have stopped; container uptime alone does not keep the UI active |

This guide was checked against the supplied Compose file, Spark settings and preparation scripts. The step-08/09 document generation was checked locally. The full Docker/Spark pipeline has **not** been rerun as part of preparing this README; include a teammate's setup/run results in the PR before claiming end-to-end reproducibility.

Official command references: [Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/) and [Spark application submission](https://spark.apache.org/docs/3.5.7/submitting-applications.html).
