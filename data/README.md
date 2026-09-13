# How to Obtain the Raw Data Files

None of the three raw data files are committed to this repo (size and/or license terms).
Here's exactly how to get each one.

## 1. `cps_00001.dat` (IPUMS CPS extract)

1. Register for a free account at [cps.ipums.org/cps](https://cps.ipums.org/cps/).
2. Click **"Get Data"** under "Create an Extract."
3. Under **Select Samples**, choose the monthly basic CPS samples from January 2022
   through the most recent available month.
4. Under **Select Variables**, search for and add: `AGE`, `OCC`, `EMPSTAT`, `WTFINL`.
   (`YEAR` and `MONTH` are auto-included by default.)
5. Submit the extract, wait for the completion email (can take minutes to hours
   depending on size), then download the `.dat` file from your extract history page.
6. Also download the **DDI codebook** (small `.xml` file, same extract page) - this
   documents the exact column positions used in `scripts/01_parse_cps_data.py`. If IPUMS
   changes anything about extract formatting in the future, re-check this file against
   the column positions hardcoded in the script.
7. Place the `.dat` file at `data/cps_00001.dat`.

**Note:** IPUMS deletes extract files after 72 hours - save your own copy once downloaded.

## 2. `job_exposure.csv` (Anthropic Economic Index)

1. Go to [huggingface.co/datasets/Anthropic/EconomicIndex](https://huggingface.co/datasets/Anthropic/EconomicIndex).
2. Click the **"Files and versions"** tab.
3. Find the **"Labor market impacts"** release folder and download `job_exposure.csv`.
4. Place it at `data/job_exposure.csv`.

## 3. `2018-occupation-code-list-and-crosswalk.xlsx` (Census Bureau crosswalk)

1. Go to the [Census Bureau's Industry and Occupation Code Lists & Crosswalks page](https://www.census.gov/topics/employment/industry-occupation/guidance/code-lists.html).
2. Under **Occupation → "2018 Census Occupation Code Lists (Derived from the 2018 SOC)"**,
   download **"2018 Census Occupation Code List with Crosswalk"** (a small `.xls` file).
3. Place it at `data/2018-occupation-code-list-and-crosswalk.xlsx`.
