# How housed households spread across the three rental sizes: model against data (6 November)

For the response letters (AE A4, Referee 2 D1), not the paper. The author asked whether the data, measured more
closely to the model, support a distribution closer to the model's 1.1 / 13.2 / 85.7 percent in the smallest, middle
and largest rung (benchmark log, `renters_by_rental`).

Data: ACS 2023 1-year PUMS (`csv_hus.zip`, www2.census.gov/programs-surveys/acs/data/pums/2023/1-Year/), the
published ACS 2023 tables B25042 and B25020, and the AHS 2023 national PUF. The downloads are not kept here; the
scripts read them from paths given on the command line. The PUMS weights reproduce B25042's 13.2 / 24.1 / 62.7.

The measure the letters use (`universe3.py`, `published_out.txt`): the model's households, householders aged 26 to
85, where at ages 26 to 50 only households raising their own child under 18 count (every model household raises one
at those ages), weighted by the data's mass at each age; each unit put on the rung nearest it in rooms, a studio on the
smallest, one or two bedrooms on the middle, three or more on the largest. Result: 1.4 / 27.5 / 71.0. The same picture
by monthly housing spending at the paper's dollar scale, average labour income $112,500 (`measures2.py`,
`measures2_out.txt`): 3.9 / 30.8 / 65.2. Every measure that respects the model's 1:4:8 spacing puts too few households in
the middle rung and too many in the largest; the smallest is about right.

Note for the "one place" rule: the Fortran declares rung_ratio_h3 = 2, rung_ratio_h4 = 3 and h_2 = 0.142
(f90 5579-5580, 7315), while the benchmark handover sets 4, 8 and 0.0407, which is what the paper prints.
