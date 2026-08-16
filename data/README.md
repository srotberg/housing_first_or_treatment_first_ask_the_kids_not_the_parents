# Data

Every number in the calibration that comes from outside the model traces to a
file here. `raw/` holds the source exports exactly as downloaded; the scripts
turn them into the small CSVs the Fortran reads. `FINDINGS.md` records what each
one implied, including the three targets it called into question.

Regenerate everything:

```bash
python3 make_life_table.py    --ssa-xlsx raw/SSA_period_life_table_table4c6.xlsx
python3 make_housing_dist.py  --xlsx     raw/ACS_B25042_2023_tenure_by_bedrooms_occupied_units.xlsx
python3 make_overdose.py      --wonder   raw/CDCWONDER_provisional_mortality_drug_alcohol_induced_by_5yr_age.txt
```

## Model inputs

| file | read by | contents |
|---|---|---|
| `us_life_table.csv` | `params.f90::load_life_table` | `age,qx`, ages 26–85 |
| `us_housing_dist.csv` | not yet wired | housed shares by unit size |
| `us_overdose_mortality.csv` | not yet wired | overdose deaths and rates by 5-year age |

`load_life_table` warns and falls back to a smooth hazard if its file is
missing, so the model runs without it — but that fallback is *not* a data
source and must not survive into the paper.

## Raw sources

| file in `raw/` | source | vintage | universe / notes |
|---|---|---|---|
| `SSA_period_life_table_table4c6.xlsx` | SSA, `oact/STATS/table4c6` | current | Period life table by sex. Sexes combined by survivor weight, not averaged. |
| `ACS_B25042_2023_tenure_by_bedrooms_occupied_units.xlsx` | Census ACS 1-year | 2023 | **Occupied housing units**, N = 131,332,360. The one to use. |
| `ACS_B25041_2023_bedrooms_all_housing_units.xlsx` | Census ACS 1-year | 2023 | *Housing units* — includes ~10% vacant. Wrong universe, kept for comparison. |
| `HUD_PIT_counts_by_state_2007_2024.xlsb` | HUD Exchange PIT/HIC | 2007–2024 | Point-in-time literal homelessness. Sheltered / unsheltered / chronic. |
| `HUD_picture_subsidized_households_2023_by_program_US.xlsx` | HUD Picture of Subsidized Households | 2023 | **By programme.** Use the tenant-based voucher row — that is the model's voucher. |
| `HUD_picture_subsidized_households_2023_all_programs_US.csv` | same | 2023 | All-programmes summary; averages over public housing and project-based. |
| `CDCWONDER_provisional_mortality_drug_alcohol_induced_by_5yr_age.txt` | CDC WONDER provisional mortality | 2018– | Grouped by `MCD - Drug/Alcohol Induced Cause` × five-year age. **The right grouping.** |
| `CDCWONDER_..._113_cause_list_..._SUPERSEDED.txt` | same | 2018– | Grouped by the ICD-10 113 Cause List. Its poisoning category is X40–X49, unintentional only. Superseded; kept so the difference is checkable. |
| `NSDUH_2023_detailed_tables.zip` | SAMHSA NSDUH | 2023 | Detailed tables, HTML. Query with `nsduh_query.py`. |
| `CEX_all_consumer_units_detailed_means_2024.xlsx` | BLS Consumer Expenditure Survey, table 2500, detailed means | 2024 | All consumer units, owners included. **Shelter plus utilities is 26.8 per cent of total expenditure**, which is `gamma`'s object; shelter alone is 20.8 and the whole Housing category is 33.4. Owners enter at **outlay**, not imputed rent, so the true figure is higher and the model's 25 per cent is at the low end. Computed by `cex_housing_share.py`. |
| `FRED_UNRATE_monthly_1948_2024.xlsx` | FRED series `UNRATE`, St. Louis Fed, from the BLS CPS | 1948–01 to 2024–05 | Headline civilian unemployment rate, **ages 16 and over**, monthly, seasonally adjusted. The 2014 to 2024 mean is **4.852 per cent**, which is where `u_0` comes from. Note the universe: `u_1` is NSDUH ages 26+, so the two are not on the same age base. A 25+ series (`LNS14000048`) would be lower than the headline and would widen the gap. |

Despite its filename, `HUD_picture_subsidized_households_2023_by_program_US.xlsx`
arrived named `US_2025_2020census.xlsx`. It is not census population data.

## Querying NSDUH

```bash
unzip -q raw/NSDUH_2023_detailed_tables.zip -d /tmp/nsduh && cp nsduh_query.py /tmp/nsduh
cd /tmp/nsduh
python3 nsduh_query.py --list "Substance Use Disorder"   # find a table
python3 nsduh_query.py "Table 5.4B"                      # dump it
```

Tables already used: **5.1B** disorder by substance, **5.4B** drug use disorder
by employment, **5.10B** all SUD by employment, **5.35B** reasons for not
receiving treatment, **6.10B** co-occurring SUD and mental illness.

## Two traps that would produce plausible but wrong numbers

**CDC "All other drug-induced causes" is not non-overdose SUD mortality.** The
drug-induced list carries therapeutic adverse effects — drug-induced anaemia,
thyroiditis, polyneuropathy, osteoporosis — which dominate at older ages: 600
per 100,000 at 80–84 against 6 for overdose. Overdose is the sum of the four
`Drug poisonings` rows only.

**NSDUH "substance use disorder" includes alcohol.** It is 16.6% at ages 26+,
against 8.6% for drug use disorder and 5.5% for marijuana alone. The model's
3.68% is drugs excluding marijuana. Comparing against the NSDUH headline makes
the model look wrong by a factor of four.
