# HMDA Viz Prototype Processing

This is the **prototype** processing code for the HMDA aggregate and disclosure reports. It is based on the current [FFIEC On-Line Reports](http://www.ffiec.gov/hmda/online_rpts.htm).

Working prototype processing code can be found running in [gh-pages](http://cfpb.github.io/hmda-viz-prototype/processing).

## Processing Dependancies
- Python
    - [Psycopg2](http://initd.org/psycopg/)
    - [Numpy](http://www.numpy.org)
    - Requests
    - json
- [PostgresSQL](http://www.postgresql.org/download/)
- [Internet access](http://www.broadbandmap.gov)
- A full list of packages used can be found in [requirements.txt](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/requirements.txt)
    - `pip install -r requirements.txt` to install the requirements


## Data Dependancies
- Public HMDA LAR data
    - Available from the [CFPB](Consumerfinance.gov/HMDA) and [the FFIEC](www.FFIEC.gov/HMDA). Note: the load script runs on pipe delimited files and requires certain fields appended from Census data.
- Tract to CBSA 2010 crosswalk
    - Load script available [here](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/tract%20to%20CBSA%20Load%20Script%20PostgreSQL-2.txt).
    - Tract to CBSA data is available [here](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/tract_to_cbsa_2010.csv) and from the [Census](www.census.gov)
- Census ACS 2010 API
    - available at [the Census website](http://www.census.gov/data/developers/data-sets/acs-survey-5-year-data.html). The processing code uses the B25035_001E source field to get median housing stock age by tract. The API requires state, county, and tract inputs.


## File Dependancies
The controller.py file requires an input CSV titled 'MSAinputs2013.csv' to run, an example file can be found [here](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/MSAinputs2013.csv). The first row of the file is all the CSV is a header row with. Column 1 is a list of all Metropolitan Statistical Areas (MSA) and Metropolitan Divisions (MD). MDs are listed as the last 5 numbers of the complete MD number. Column 2 is the year for which the report(s) will be generated. The headers for columns 3+ are report numbers. The first letter shows which type of report 'A' is aggregate, 'D' is disclosure and 'N' is national. Cells in columns 3+ are binary flags, if a 1 is entered in a cell, then the report at that row will be generated when the controller.py file is run.


## Loading SQL Data
- To load HMDA LAR data to a Postgres database use [this script](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/HMDApub%20data%20load%20to%20SQL.txt). This script creates tables for HMDA data from 2009 to 2013 and then fills the tables from files referenced in the paths of the copy statements at the end of the script. To use the file, change the copy path at the bottom to match the location of the HMDA data. This script is set to read pipe (|) delimited text files into varchar tables.

- If you do not have the data files for any year from 2009 to 2013 then the relevant copy command(s) need to be removed.

-The dataset used for processing requires several Census fields. In addition to the standard HMDA fields, the following fields have been appended from Census data: areapopulation, minoritypopulationpct, ffiec_median_family_income, tract_to_msa_md_income, num_of_owner_occupied_units, num_of_1_to_4_family_units, application_date_indicator, fipscode, latitude, longitude. Of these fields only minority populationpct, ffiec_median_family_income, and tract_to_msa_md_income are used in the processing code.

- To load tract to CBSA data use [this script](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/tract%20to%20CBSA%20Load%20Script%20PostgreSQL-2.txt). This will create the tract to CBSA data table which contains the crosswalks between MSAs/MDs and census tracts and then copy the data into the tables from the path specified at the bottom of the script.

## Back-end Installation
To launch the processing script, enter:
```shell
$ python controller.py
```
The controller.py file will run all reports in each MSA/MD that have a 1 in the MSAinputs2013.csv file.
## Usage
Currently the code produces only aggregate reports. The most thorough testing and validation has been done with Alabama 2013. Testing has not been done for previous years, and schema changes to the HMDA LAR will affect the processing code.

## Known issues

We are still in the prototyping phase so there is a lot of work happening on both the front-end and processing sides.
- Only certain paths currently work for the front-end.
- Only 2013 data has been tested for code compatability.
- Disclosure and national reports are not yet produced.
- Selector.py does not return a list of reports, only MSAs to run for each report.
- Report 11-1 requires over 10x processing time of other reports in the 11 series. This may be due to index errors in the demographic_indexing.py file.

## Getting help

If you have questions, concerns, bug reports, etc, please file an issue in this repository's [Issue Tracker](https://github.com/cfpb/hmda-viz-prototype/issues).

## Getting involved

TBD

----
## Open source licensing info
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
----
## Credits and references

1. [FFIEC](http://www.ffiec.gov/HmdaAdWebReport/AggWelcome.aspx)
2. [Federal Register] (http://www.gpo.gov/fdsys/pkg/FR-2004-12-20/pdf/04-27425.pdf)
3. <http://cfpb.github.io/hmda-viz-prototype/aggregate/2013>
