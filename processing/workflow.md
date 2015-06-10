#A&D report processing workflow

##Roadmap
* Add in modules and supporting software

* Initial code work
    1. Report Engines
    2. Controller
    3. Geo-aggregator
    4. Output files

* Known issues
    1. Unit testing required
    2. Not all loans are aggregating
    3. Objects must be aggregated to higher geography levels than tract
    4. Report 1 object needs a revised connect string and more articulation

* End state goal
## Add-in modules and supporting software
    Using Psycopg2 the report engines access a locally hosted SQL database to pull information from the HMDA LAR files

## Report Engines:

    ###1. Report 1
    Constructed to take a single tract and aggregate loans for aggregate Table 1
    Modified to be an initializable object with most methods called by an internal aggregator function
    Output is a JSON file dump

    ###2. Report 3
    Required significant time to address all the demographic logic prior to loan aggregation
    Constructed to take a single tract and aggregate loans for aggregate Table 3-1
    Modified to be an initializable object with demographic logic called by an internal fucntion
    Output is a JSON file dump
    This code was rewritten to incorporate Andrew's JSON structure

### Controller
    Controller is a script used to coordinate the use of an input file (yet to be built), the geo-aggregator and the report generation objects
    Constructed initially to instantiate report objects and run aggregation logic on a single tract
    Modified to use the geo-aggregator to build a tract list for passing to the report generator objects
    Report generators are now called in a loop and output one JSON object per tract inside a single county

### Geo-aggregator
    Constructed to find all the MSAs in the HMDA LAR file and build a dictionary holding all their sub geography
    The initial run-time on this file was approximately 15 hours, making it not very useful for articulated report generation
    Modified to take a single MSA from the Controller object and build a dictionary of all sub geographies and return it to the Controller

### Output files
    Output files are .JSON
    One object is made per tract per report
    There will need to be some aggregation across files to create county, state, and MSA level JSON objects

## Known issues
1. Unit testing will be required to ensure accuracy
    * This may be accomplished using SQL queries that mimic the python logic used in the report generators
2. Not all loans are aggregating according to each demographic data element
3. JSON objects need to be produced for geographies other than tracts
4. Need a test for the Geo-aggregator

## End-State goal
    A Controller object will take a file input (likely CSV) that will determine which reports are run on which geogprahies and financial institutions
        * Ideally this file can be created using scripts
    The Controller will pass MSAs to the Geo-aggregator to determine which tracts need to be run through the report generators
    The Controller will either aggregate the tracts to appropriate geography levels or call another object that does this
    The Controller will determine which reports are run for which FIs or geographies
    Report generators will take arguments based on the input file that determine whether:
        * the report is aggregate or disclosure
        * for which geography to aggregate loans
    A master JSON object file will be contain all the JSON structures for the reports, each report generator will pull a piece of this file to use in aggregation
