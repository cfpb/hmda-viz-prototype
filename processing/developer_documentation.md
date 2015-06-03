#Developer Documentation for Aggregate and Disclosure Processing

For information on dependancies and running the code see [readme.md](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/readme.md)


#Files
- controller.py
	- Calls check_file
	- Calls report_lists
	- Runs a set of nested for loops to pass report names and MSAs to the constructor.py file
	- Establishes a database connection, parses the MSAinputs CSV file to determine which reports will be created
	- Builds the directory structure for report type, report year, and states
	- Times report processing for both CPU and clock time
	- Writes log files on processing speeds
	- During testing controller has extra lists of MSAs and report names to control output quickly
	- Imports time, psycopg2, psycopg2.extras, connector, builder, selector, constructor, file_check, and report_list


- selector.py
	- Called by controller.py and constructor.py
	- Creates a dictionary that controls which reports will be run for which MSAs
	- imports csv


- connector.py
	- Called by controller.py and median_age_api.py
	- Connects to the database hosting the hmda public files and tract to cbsa data
	- imports psycopg2 and psycopg2.extras
	- Uses a dictionary cursor to read inputs


- constructor.py
	- Called by controller.py
	- Selects LAR rows based on report specific columns and conditions and aggregates the LAR rows into JSON objects
	- Calls report specific functions to get small county flags and median housing stock age
	- Calculates means and medians and stores them in the JSON object
	- Writes JSON objects to files using report type, year, and geography as a path
	- Imports json, os, csv, psycopg2, psycopg2.extras, OrderedDict, parsing, connector, builder, aggregation, queries, selector, respondent_id_compiler

- queries.py
	- Called by constructor.py
	- Returns text for conditions and column selection for SQL queries
	- Currently only formatted for psycopg2 for use with postgreSQL
	- Planned development for pyodbc for use with microsoft server clients


- builder.py
	- Called by aggregate_report in constructor.py
	- Creates emtpy JSON objects used to hold the aggregated LAR rows
	- Imports json, os, OrderedDict, and datetime


- parsing.py
	- Called by report_constructor and aggregate_report in constructor.py
	- Parses LAR rows by report series and stores rate lists for use in calculating means and medians
	- Imports msa_indexing, median_age_api, demographics_indexing, and connector


- demographics_indexing.py
	- Called by parse_inputs in parsing.py
	- Takes parsed loan attributes and returns indexes and sets flags used in loan aggregation into the JSON structures for reports


- msa_indexing.py
	- Called by parse_inputs in parsing.py
	- Takes inputs regarding census tracts or combinations of applicant and census tract information and returns an integer index used in aggregating data into JSON structures


- aggregation.py
	- Called by constructor.py to fill dictionary objects prior to conversion to JSON objects
	- Calculates means, medians, weighted means, and weighted medians
	- Imports numpy and decimal


- median_age_api.py
	- Called by the median_tract_age function in the parse_inputs class in the parsing.py file
	- Returns an integer for the median housing stock age for the selected census tract


- file_check.py
	- Called by controller.py
	- Searches the report directory structure for MSAs that have reports and writes an 'msa-mds.json' to indicate to  Jekyll that reports exist in subfolders for that MSA
	- Imports os.path and json

 - report_list.py
	- Called by controller.py
	- Scans the directory of potential reports and creates a JSON object listing all the reports run for each MSA and writes the JSON to a file and stores it in the appropriate folder
	- Imports OrderedDict from collections, os.path, json, and builder.py



#Explanation of Classes and Methods

## controller
- Has no classes or methods
- Calls connect from connection to establish a cursor connection with the database
- Calls msas_in_state from builder to create a list of MSAs in each state for each report type directory
- Calls get_reports_list from selector to create a list of which reports for which MSAs are to be run based on the MSAinputs CSV
- Calls time.time and time.clock to log CPU and human clock time required to generate reports
- Writes processing times for each report and total times to a log file (processing_log.txt)
- Calls check_file from file_check.py to create msa-mds.json files showing which MSAs have reports in which sub-directories
- Calls report_lists from report_list.py to produce a list of all reports run for an MSA


## report_selector
- initialize_lists
	- Creates a master list of all possible report types to be run using the heads of the infile
	- Takes a CSV file as infile


- get_report_lists
	- Called by controller.py
	- Reads the CSV file and adds any MSA/report intersection cell marked with a 1 to the list of reports to be run
	- Takes a CSV file as infile


## connect_DB
	- connect
		- Reads a credentials file from the path /Users/roellk/Desktop/python/credentials.txt and parses the file to access the specified database
		- Prints on successful or unsuccessful connection to notify the user of potential errors


## constructor
- __init__
	- Instantiates parse_inputs from parsing.py, connection from connect.py, queries from queries.py, and aggregate from aggregation.py
	- Puts the report year and report number in the global class variables
	- Puts the parse_return, JSON_constructor_return, and aggregation_return in the global class variables
	- Calls parse_return, JSON_constructor_return, and aggregation_return from report_construction in constructor.py


- aggregate_report
	- Called by controller.py
	- Takes an MSA as a string and a cursor object as arguments
	- Determines report type (aggregate, disclosure, or national)
	- Runs  a loop which pulls one LAR row from the cursor at a time, parses it, and aggregates it into a JSON structure
	- Calls median_tract_age from parsing to pull median housing stock age from the Census ACS5 API for each tract in the MSA of the current report
	- Calls get_small_county_flag from aggregation.py to determine if a loan is in a small county
	- Calls the report specific conditions and columns query strings from queries.py
	- Calls aggregation_return, JSON_constructor_return, and parse_return from constructor.py to get the function names used with aggregation.py, builder.py and parsing.py
	- Calls functions to calculate means and medians from aggregation.py if needed for the report
	- Writes the report's JSON object to a file path that includes, report type, data year, state, MSA, and report number


- aggregation_return
	- Called by aggregate_report in report_constructor
	- Takes a year and report_number as strings and returns a function name used to call an aggregation function from aggregation.py


- JSON_constructor_return
	- Called by aggregate_report in report_constructor
	- Takes a report_number as a string and returns a function name used to call a JSON object building function from builder.py


- parse_return
	- Called by aggregate_report in report_constructor
	- Takes a report_number as a string and returns a function name used to call a parsing function from parsing.py


## queries
- __init__
	- Holds the base SQL string for getting counts of selected LAR rows with formatting sections to variabalize MSA and year
	- Holds the base SQL string for selecting columns of HMDA data with formatting sections in which columns, year, and MSA are variabalized


- Condition functions
	- Called by aggregate_report in report_construction in constructor.py
	- Returns the conditions for the report with function name format as table_type_series_number_conditions (IE table_A_3_1_conditions)


- Column select functions
	- Called by aggregate_report in report_construction in constructor.py
	- Returns the columns required to aggregate LAR rows for the report with function name format as table_series_number_columns(IE table_3_1_columns)


## build_JSON
- __init__
	- Instantiates lists and dictionaries used in subsequent functions


- msas_in_state
	- Called by controller.py
	- Queries the tract_to_cbsa_2010 data table for a distinct list of MSAs and MDs
	- Creates a dictionary of all MSAs and MDs in a state
	- Calls jekyll_for_state from builder.py


- jekyll_for_msa
	- Called by constructor.py
	- Takes a path as an argument that includes report type, year, msa, and state
	- Writes a jekyll file to the passed path


- jekyll_for_state
	- Called by msas_in_state in builder.py
	- Takes a path as an argument that includes report type, year, and state
	- Writes a jekyll file to the passed path


- jekyll_for_report
	- Called by constructor.py
	- Takes a path as an argument that includes report type, year, state, MSA, and report number
	- Writes a jekyll file to the passed path


- set_msa_names
	- Called by aggregate_report in constructor.py
	- Builds a dictionary containing MSA/MD numbers and the associated names
	- Takes a cursor argument and queries the tract_to_cbsa_2010 data table to return the names and numbers of all MSAs and MDs


- get_state_name
	- Called by constructor.py
	- Takes a state abbreviation and returns the full state name


- table_headers
	- Called by aggregate_report in constructor.py
	- Takes a table number argument as a string and returns the descriptive text for the table


- set_header
	- Called by aggregate_report in constructor.py
	- Takes a dictionary as inputs, MSA as a string, table_type as a string and table_num as a string
	- Populates the header information for tables


- set_list
	- Called by set_gender_disps, table_3_1_builder, table_3_1_characteristics, table_3_2_builder, build_rate_spreads, set_4_x_race, set_4_x_ethnicity, set_4_x_minority, set_4_x_incomes, table_5_x_builder, table_7_x_builder, table_8_helper, table_9_x_builder, table_11_x_characteristics, table_A_x_builder, table_B_builder in builder.py
	- Takes end_points as a list, key_list as a list, key_name as a string, and ends_bool as a boolean
	- Creates a list of dictionary objects and returns it
	- If ends_bool is false each element of the end_points list is added to each dictionary object as a key with a value of 0


- print_JSON
	- Called during testing to check outputs
	- Prints the JSON structure to the terminal


- write_JSON
	- Called by aggregate_report in constructor.py
	- Writes the dictionary container to a .json file at the specified path
	- Takes name as a string, data as a json compatibile object, and path as a string


- set_purchasers_NA
	- Called by build_rate_spreads in builder.py
	- Takes holding_list as a list and returns a list of dictionaries containing a purchaser name for each item in the holding_list
	- If the holding list item is juniorliencount or juniorlienvalue then 'NA' is stored as the value, else the value is '0'


- set_gender_disps
	- Called by table_4_x_builder
	- Calls set_list from builder.py
	- Specifies a path to which set_list appends a list of dictionaries


- table_3_1_builder
	- Called by aggregate_report in constructor.py
	- Calls table_3_1_characteristics in builder.py
	- Builds the JSON structure for report 3-1


- table_3_1_characteristics
	- Called by table_3_1_builder in builder.py
	- Calls set_list in builder.py
	- Takes characteristic as a string, container_name as a string, and item_list as a list
	- Returns a dictionary strucure for a row section of report 3-1


- table_3_2_builder
	- Called by aggregate_report in constructor.py
	- Calls set_list  and build_rate_spreads from builder.py
	- Builds the JSON structure for report 3-2


- build_rate_spreads
	- Called by table_3_2_builder in builder.py
	- Returns a list of dictionaries for each item in table_3_2_rates
	- Sets values of firstliencount and firstlien value to 0
	- Sets juniorliencount and juniorlienvalue to 0 if the rate's index is greater than or equal to 4 and to 'NA' if the index is below 4


- set_4_x_races
	- Called by table_4_x_builder in builder.py
	- Calls set_list from builder.py
	- Builds the race section for the 4 series of JSON objects


- set_4_x_ethnicity
	- Called by table_4_x_builder in builder.py
	- Calls set_list from builder.py
	- Builds the ethnicity section for the 4 series JSON objects


- set_4_x_minority
	- Called by table_4_x_builder in builder.py
	- Calls set_list from builder.py
	- Builds the minority section for the 4 series JSON objects


- set_4_x_incomes
	- Called by table_4_x_builder in builder.py
	- Calls set_list from builder.py
	- Builds the income section for the 4 series JSON objects


- table_4_x_builder
	- Called by aggregate_report in constructor.py
	- Calls set_4_x_races, set_4_x_ethnicity, set_4_x_minority, set_4_x_incomes, and set_gender_disps from builder.py
	- Builds the JSON object for the 4 series of reports


- table_5_x_builder
	- Called by aggregate_report in constructor.py
	- Calls set_list from builder.py
	- Builds the JSON object for the 5 series of reports


- table_7_x_builder
	- Called by aggregate_report in constructor.py
	- Calls set_list from builder.py
	- Builds the JSON object for the 7 series of reports


- table_8_x_builder
	- Called by aggregate_report in constructor.py
	- Calls table_8_helper from builder.py
	- Builds the JSON object for the 8 series of reports


- table_8_helper
	- Called by table_8_x_builder in builder.py
	- Calls set list from builder.py
	- Builds a section of the JSON object for the 8 series of reports


- table_9_x_builder
	- Called by aggregate_report in constructor.py
	- Calls set_list from builder.py
	- Builds the JSON object for report 9


- table_11_x_characteristics
	- Called by table_11_x_builder and table_11_12_helper from builder.py
	- Calls set_list from builder.py
	- Builds a JSON structure section for 11 or 12 series reports


- table_11_x_builder
	- Called by aggregate_report in constructor.py
	- Calls table_11_12_helper from builder.py
	- Builds the JSON object for the 11 series of reports


- table_12_1_builder
	- Called by aggregate_report in constructor.py
	- Calls table_11_12_helper from builder.py
	- Builds the JSON object for the 12-1 report


- table_12_2_builder
	- Called by aggregate_report in constructor.py
	- Calls table_11_12_helper from builder.py
	- Builds the JSON object for the 12-2 report


- table_A_4_builder
	- Called by aggregate_report in constructor.py
	- Calls table_11_12_helper
	- Builds the JSON object for the A-4 report


- table_11_12_helper
	- Called by table_11_x_builder, table_12_1_builder, table_12_2_builder, and table_A_4_builder from builder.py
	- Calls table_11_x_characteristics from builder.py
	- Takes key as a string, key_singular as a string, and end_point_list as a list of strings
	- Builds sections of 11 series, 12 series and the A-4 report


- table_A_x_builder
	- Called by aggregate_report in constructor.py
	- Calls set_list from builder.py
	- Builds the JSON object for the A-1, A-2, and A-3 reports


- table_B_builder
	- Called by aggregate_report in constructor.py
	- Calls set_list from builder.py
	- Builds the JSON object for report B


## parse_inputs
- __init__
	- Initializes lists to hold weights and rates that are used to calculate means, medians, weighted means, and weighted medians
	- Initializes a dictionary for tract median age which stores the median age of housing stock as a value and an 11 digit census tract as a key
	- Initializes the inputs dictionary which holds all information parsed from the LAR row or derived from functions that index information for aggregation in dictionary objects and subsequent storage as JSON files


- parse_3_1
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Called by function aggregate_report in class_report construction in file constructor.py
	- Parses a LAR row into the components required for report 3-1 and stores them in the inputs dictionary
	- Calls make_race_list from the demographics class in demographics_indexing.py to convert applicant and coapplicant race strings to integer lists
	- Calls tract_to_MSA_income from MSA_info to convert the tract to FFIEC median MSA income ratio to an index for use in loan aggregation
	- Calls app_income_to_MSA from MSA_info to convert the applicant income to FFIEC median MSA income ratio to an index for loan aggregation
	- Calls minority_percent from MSA_info to convert the minority population percent to an index number for loan aggregation
	- Calls set_non_white from demographics to set boolean flags for applicant and coapplicant race lists to show if either race list contains a minority (true), exclusively white (false) or neither (none)
	- Calls minority_count from demographics to determine the number of minority races the applicant selected
	- Calls set_joint from demographics to determine if the loan is joint status (true) or not joint status (false)
	- Calls set_race from demographics to determine a single integer race code for the loan
	- Calls set_loan_ethnicity to determine a single integer ethnicity code for the loan
	- Calls set_minority_status to determine a single integer code for the loan's minority status



- parse_3_2
	- Instantiates the demographics class from demographics.py
	- Called by function aggregate_report in class_report construction in file constructor.py
	- Parses LAR rows and stores the components in a dictionary to be  used as needed for processing report 3-2
	- Calls rate_spread_index_3_2 to assign an index to each rate spread



- parse_4_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 4 series of reports and stores them in the inputs dictionary
	- Called by function aggregate_report in class_report construction in file constructor.py
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan or application
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan or application
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan or application
	- Calls set_gender from demographics to set a single index integer for the gender of the loan or application



- parse_5_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 5 series of reports and stores them in the inputs dictionary
	- Called by function aggregate_report in class_report construction in file constructor.py
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan


- parse_7_x
	- Instantiates MSA_info from msa_indexing.py
	- Parses a LAR row into components required for the 7 series of reports and stores them in the inputs dictionary
	- Called by function aggregate_report in class_report construction in file constructor.py
	- Calls minority_percent from MSA_info to assign an integer index according to the minority population percent
	- Calls tract_to_MSA_income to assign an integer index to the tract to MSA income ratio


- parse_8_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 8 series of reports and stores them in the inputs dictionary
	- Called by function aggregate_report in class_report construction in file constructor.py
	- Calls adjust_denial_index from parse_inputs in parsing.py to change the denial reason code to an integer index that matches the JSON structure for data ouput
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in lists with a length of 5
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan or application
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan or application
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan or application
	- Calls set_gender from demographics to set a single index integer for the gender of the loan or application
	- Calls denial_reasons_list from parse_inputs in parsing.py to create a list of denial reasons and store it in the inputs dictionary


- adjst_denial_index
	- Called by parse_8_x in parse_inputs in parsing.py
	- Takes an integer input of one denial reason
	- Returns an integer index
	- Subracts 1 from the code of a denial reason to match the JSON data storage structure index


- denial_reasons_list
	- Called by parse_8_x in parse_inputs in parsing.py
	- Takes 3 integer inputs of denial reasons
	- Returns a list containing the 3 inputs


- parse_9_x
	- Parses a LAR row into components required for the 9 series of reports and stores them in the inputs dictionary
	- Called by function aggregate_report in class_report construction in file constructor.py
	- Calls set_loan_index to change the loan type to match the index used in the JSON structure for report 9
	- Calls median_age_index to assign an integer index based on the median age of housing stock in the loan's census tract
	- Sets the median age for the loan by passing the 11 digit census tract number to  the tract_median_ages dictionary in parse_inputs in parsing.py

- set_loan_index
	- Called by parse_9_x
	- Takes loan_purpose as a string, loan_type as an integer and property_type as a string
	- Returns a single integer index to sort the loans into the JSON structure based on the passed parameters


- median_tract_age
	- Instantiates median_age_API from median_age_api.py
	- Called by the aggregate_report function in the report_construction class in file constructor.py
	- Fills the tract_median_ages dictionary in parse_inputs with the median housing stock ages for each tract in an MSA by making queries agains the database holding LAR data
	- Queries the Census ACS 5 year API to get the median housing stock age for a tract using the B25035_001E end-point

- median_age_index
	- Called by parse_9_x in parse_inputs in parsing.py
	- Returns a single integer index based on current report format (this index changes approximately every 10 years) that is used to aggregate loans into the JSON structure


- parse_11_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 11 series of reports and stores them in the inputs dictionary
	- Called by the aggregate_report function in the report_construction class in file constructor.py
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls tract_to_MSA_income to return a single integer index for the loan's tract to MSA income ratio
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls rate_spread_index_11_x from demographics to return a single integer index for the loan's rate spread variable
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan or application
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan
	- Calls set_gender from demographics to set a single index integer for the gender of the loan or application


- parse_12_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 12 series of reports and stores them in the inputs dictionary
	- Called by the aggregate_report function in the report_construction class in constructor.py
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls tract_to_MSA_income to return a single integer index that represents the bucket of the loan's tract to MSA income ratio (buckets determined by FFIEC A&D report format)
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls minority_percent from MSA_info to assign a single integer index to the loan based on the minority population percent in the loan's census tract
	- Calls rate_spread_index_11_x from demographics to return a single integer index for the loan's rate spread variable
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan or application
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan or application
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan or application
	- Calls set_gender from demographics to set a single index integer for the gender of the loan or application


- parse_A_x
	- Called by the aggregate_report function the report_construction class in constructor.py
	- Parses a LAR row into components required for the A series of reports (excluding A 4) and stores them in the inputs dictionary


- action_taken_index
	- Called by parse_A_x in parse_inputs in parsing.py
	- Adjusts the action taken code to match the JSON structure of the report


- purpose_index
	- Called by parse_A_x in parse_inputs in parsing.py
	- Adjusts the loan purpose code to match the JSON structure of the report


- parse_A_4
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the A 4 reports and stores them in the inputs dictionary
	- Called by the aggregate_report function in the report_construction class in constructor.py
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls tract_to_MSA_income to return a single integer index that represents the bucket of the loan's tract to MSA income ratio (buckets determined by the FFIEC A&D report format)
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls minority_percent from MSA_info to assign a single integer index to the loan based on the minority population percent in the loan's census tract
	- Calls rate_spread_index_11_x from demographics to return a single integer index for the loan's rate spread variable
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan or application
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan or application
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan or application
	- Calls set_gender from demographics to set a single index integer for the gender of the loan or application


- parse_B_x
	- Instantiates the demographics class from demographics_indexing.py
	- Parses a LAr row into components required for the B series of reports and stores them in the inputs dictionary
	- Calls rate_spread_index_11_X to assign a single integer index to the loan based on the loan's reported rate spread


## demographics

- set_gender
	- Called by parse_4_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes a parsed LAR row as inputs and returns an index value for aggregating loans
	- Returns \"None\" if conditions for available indices are not met


- rate_spread_index_3_2
	- Called by parse_3_2
	- Takes a rate spread value as a string, converts to floats for bucket comparison and returns an integer index based on the buckets for report 3-2
	- Returns \"None\" if the input does not map to an available bucket


- rate_spread_index_11_x
	- Called by parse_11_x, parse_12_x, and parse_A_4
	- Takes a rate spread value as a string, converts to floats for bucket comparison and returns an integer index based on the buckets for the 11 series of reports
	- Returns \"None\" if the input does not map to an available bucket

- minority_count
	- Called by parse_3_1, parse_4_x, parse_5_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes the applicant's list of races from a parsed LAR row and returns the integer count of minority races selected


- set_non_white
	- Called by parse_3_1, parse_4_x, parse_5_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes a list of races and returns a boolean that is True if 2 or more minority races were selected, False if no minority races were selected, or None if none of those conditions were met


- set_joint
	- Called by parse_3_1, parse_4_x, parse_5_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes a parsed LAR row dictionary as inputs and returns True if one applicant is listed as non-white and the other as white
	- Uses app non white flag and co non white flag from inputs


- set_minority_status
	- Called by parse_3_1, parse_4_x, parse_5_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes a dictionary as inputs and returns an index for the minority status of the loan or application
	- Uses race and ethnicity of the loan to determine minority status


- set_ethnicity
	- Called by parse_3_1, parse_4_x, parse_5_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes a dictionary as inputs to return an index for the ethnicity of a loan or application
	- Uses a ethn and co ethn from inputs


- make_race_list
	- Called by parse_3_1, parse_4_x, parse_5_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes a list of strings length 5 that holds the race information for an applicant or co applicant and returns an integer list with blanks converted to 0s (zeros)


- set_race
	- Called by parse_3_1, parse_4_x, parse_5_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes race_list, a list of integers length 5, and inputs, a dictionary, as arguments
	- Returns a single integer index for the race of a a loan, this index is used to aggregate loans for all reports using race


## MSA_info
- app_income_to_MSA
	- Called by, parse_3_1, parse_4_x, parse_5_x, parse_8_x, parse_11_x, parse_12_x, and parse_A_4 in parse_inputs in parsing.py
	- Takes a dictionary as inputs and returns a single integer index based on the ratio of applicant income to MSA median income which is used to aggregate loans into a JSON object


- minority_percent
	- Called by parse_3_1, parse_7_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes a dictionary as inputs and returns a single integer index based on the minority population percent in a tract which is used to aggregate loans into a JSON object


- tract_to_MSA_income
	- Called by parse_3_1, parse_7_x, parse_11_x, parse_12_x, and parse_A_4
	- Takes a dictionary as inputs and returns a single integer based on the ratio of tract to MSA median income which is used to aggregate loans into a JSON object


##aggregate
- __init__
	- Initializes lists used for calculating means, medians, weighted means, and weighted medians
	- Holds lists used in other functions


- create_rate_list
	- Called by __init__ to establish lists of length n
	- Takes an integer input that determines list length


- fill_by_characteristics
	- Called by compile_report_3_1, fill_report_11_12, and compile_report_A_4
	- Takes a dictionary object as container, a parsed LAR row as inputs, and parametarized arguments to determine placement in the dictionary object
	- Increments count and value of loans by passed parameters


- fill_by_characteristics_NA
	- Called by compile_report_A_4 in aggregation.py
	- Takes a dictionary object as container, a parsed LAR row as inputs, and parametarized arguments to determine placement in the dictionary object
	- Fill the object's count and value fields with 'NA' according to passed parameters
	- This function is used to fill reports that have hard-coded NA fields


- calc_weighted_median
	- Called by fill_weighted_medians_11_12 and fill_by_weighted_median_3_2 in aggregation.py
	- Calculates the weighted median value using a list of rate spreads and a list of loan values
	- The weighted median is found by taking n/2 steps through the sorted rate list where n is the length of the list and a step is the average loan value from the weight list.


- fill_weighted_medians_11_12
	- Called by aggregate_report in constructor.py to fill the weighted median column in reports 11 and 12
	- Calls calc_weighted_median from aggregation.py to calculate the weighted medians
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_totals_3_1
	- Called by build_report_31 to fill the totals section of report 3-1
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_3_1
	- Called by aggregate_report in constructor.py to fill the dictionary object
	- Aggregates LAR rows for report 3-1 and returns the filled dictionary object
	- Takes a dictionary object as table31 and a parsed LAR row


- fill_by_pricing_status_3_2
	- Called by compile_report_3_2 aggregation.py
	- Aggregates LAR rows by whether or not rate spread was reported for report 3-2
	- Takes a dictionary object as container and a parsed LAR row


- fill_by_rate_spread_3_2
	-Called by compile_report_3_2 in aggregation.py
	- Aggregates LAR rows for report 3-2 with reported rate spread by the index assigned by rate_spread_index_32 in demographics_indexing.py
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_by_hoepa_status_3_2
	- Called by compile_report_3_2 in aggregation.py
	- Aggregates LAR rows for report 3-2 by status of HOEPA flag
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_by_mean_3_2
	- Called by compile_report_3_2 in aggregation.py
	- Aggregates LAR rows for report 3-2 by mean of rate spreads of the selected loans
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_by_weighted_mean_3_2
	- Called by aggregate_report in constructor.py
	- Aggregates LAR rows for report 3-2 by weighted mean of rate spreads
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_weight_lists_3_2
	- Called by compile_report_3_2 in aggregation.py
	- Fills the weight lists with loan values used for calculating means and medians for report 3-2
	- Weights are stored by lien status and only for loans with a rate spread value
	- Takes a parsed LAR row as inputs


- fill_rate_lists_3_2
	- Called by compile_report_3_2 in aggregation.py
	- Fills the rate lists with rate spreads used for calculating means and medians for report 3-2
	- Rates are stored by lien status and only for loans with a rate spread value


- fill_by_median_3_2
	- Called by aggregate_report in constructor.py
	- Aggregates loans by median for report 3-2
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_by_weighted_median_3_2
	- Called by aggregate_report in constructor.py
	- Aggregates loans by weighted median for report 3-2
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_3_2
	- Called by aggregate_report in constructor.py
	- Aggregates LAR rows for table 3-2 using by_pricing_status, by_rate_spread, by_hoepa_status, fil_rate_lists, and fill_weight_lists
	- Takes a dictionary object as table32 and a parsed LAR row as inputs


- compile_report_4_x
	- Called by aggregate_report in constructor.py
	- Calls fill_by_4_x_demographics, by_aplicant_income, and totals_4x in aggregation.py to aggregate LAR rows for tables in the 4 series
	- Takes a dictionary object as table4x and a parsed LAR row as inputs


- fill_by_applicant_income_4_x
	- Called by compile_report_4_x in aggregation.py
	- Aggregates loans by applicant income and action taken (loan disposition) for the 4 series of tables
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_by_4_x_demographics
	- Called by compile_report_4_x
	- Aggregates loans by minority status, gender, and action taken.
	- Takes a dictionary object as container, a parsed LAR row as inputs, a dictionary key, and list index which are used to call fill_4x from aggregation.py


- fill_4x
	- Called by fill_by_4_x_demographics in aggregation.py
	- Aggregates LAR rows by disposition and gender and disposition of loan
	- Takes a dictionary object as container, a key, key_index, and gender_bool
	- key and key_index are used to determine which section of the dictionary to use
	- gender_bool determines which dictionary path to use


- fill_totals_4x
	- Called by aggreage_report4x in aggregation.py
	- Aggregates totals row by action taken (application disposition) for the 4 series of reports
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_by_5x_totals
	- Called by compile_report_5_x in aggregation.py
	- Aggregates totals by action taken (application disposition) for the 5 series of reports
	- Takes a dictionary object as container and a parsed LAR row as inputs


- by_5x_demographics
	- Aggregates LAR rows by income bracket and action taken (disposition)
	- Takes a dictionary object as container, a parsed LAR row index_num, index_name, index_code
	- Index parameters are used to variabalize which part of the table are filled


- compile_report_5_x
	- Called by aggregate_report in constructor.py
	- Calls fill_by_5x_demographics, fill_by_5x_totals to aggregate parsed LAR rows by applicant income, and action taken (application disposition)
	- Takes a dictionary object as table5x and a parsed LAR row as inputs


- fill_by_tract_characteristics
	- Called by compile_report_7_x in aggregation.py
	- Aggregates parsed LAR rows by action taken (application disposition) and passed demographic information
	- Takes a dictionary object as container, a parsed LAR row as inputs, action taken as action_index
	- json_index, key, and key_index determine into which row and column of the report the loan is sorted


- fill_by_income_ethnic_combo
	- Called by compile_report_7_x in aggregation.py
	- Aggregates parsed LAR rows by tract to MSA income category (low, moderate, middle, upper) and minorty population percentage of the tract in which the property related to the application sits
	- Takes a dictionary object as container and a parsed LAR row as inputs


- get_small_county_flag
	- Called by aggregate_report in constructor.py
	- Queries the tract_to_cbsa_201 data table to return all tracts in an MSA; these tracts are used to fill the dictionary small_tract_flags in aggregation.py with tract numbers and the binary flag for small county status
	- Takes a Psycopg2 dictionary cursor as cur and an 5 digit MSA number as MSA

- fill_by_geo_type
	- Called by compile_report_7_x in aggregation.py
	- Aggregates parsed LAR rows by action taken (application disposition), small county status, and if the reported census tract had no income data available from the Census
	- Takes a dictionary object as container, a parsed LAR row as inputs, action taken (application disposition) as action_index (an integer with range 1 through 8)


- fill_totals_7x
	- Called by compile_report_7_x in aggregation.py
	- Aggregates parsed LAR rows for total applications received and then by action taken (application disposition); action taken is an integer range 1 through 8
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_7_x
	- Called by aggregate_report in aggregation.py
	- Calls fill_by_tract_characteristics, fill_by_income_ethnic_combo, and fill_by_geo_type to fill the 7 series of reports
	- Takes a dictionary objet as table7x and a parsed LAR row as inputs


- fill_by_denial_percent
	- Called by aggregate_report in constructor.py
	- Fills the percent (%) column for each denial reason by dividing the a cell's count by the total for the row
	- Takes a dictionary object as container, a parsed LAR row as inputs, index_num which determines the row on the report, and key which is a string used to access the sub-section of the container dictionary


- fill_by_denial_reason
	- Called by compile_report_8_x in aggregation.py
	- Aggregates parsed LAR rows by denial reason for rows determined by passed parameters, reason is used to select the column for aggregation
	- Takes a dictionary object as container, a parsed LAR row as inputs, index_num to determine the row for aggregation, a key and key_singular to access the appropriate sub-section of the dictionary


- compile_report_8_x
	- Called by aggregate_report in constructor.py
	- Calls fill_by_denial_reason from aggregation.py to fill the 8 series of reports with parsed LAR rows
	- Takes a dictionary object as table8x and a parsed LAR row as inputs


- compile_report_9_x
	- Called by aggregate_report in construtor.py
	- Aggregates parsed LAR rows by the median age of housing stock for the property location's census tract, occupancy type, property type, loan type, and action taken (application disposition)
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_11_12_weights
	- Called by aggregate_report11x and compile_report_12_2 in aggregation.py
	- Fills the weight lists with loan values used for calculating weighted medians, only loans with a reported rate spread are added to this list
	- Takes a parsed LAR row as inputs


- fill_11_12_rates
	- Called by aggregate_report11x and compile_report_12_2 in aggregation.py
	- Fills the rate lists with rate spreads used for calculating means, medians, and weighted medians, only loans with a reported rate spread are added to the list
	- Takes a parsed LAR row as inputs


- calc_mean_11_12
	- Called by fill_means_11_12 in aggreation.py
	- Uses Numpy to calculate the mean, using decimal precision, of the passed list ratespread_list and put the total in the mean column of report 11.x or 12-2
	- Takes a dictionary object as container, a list_name which is a list of lists containing rate spreads,  section as a string, section_index as an integer and key_plural as a string
	- Section, section_index and key_plural are used to access the appropriate dictionary section


- calc_weighted_mean_11_12
	- Called by fill_weighted_means_11_12 in aggregation.py
	- Calls calc_weighted_mean_11_12 in aggregation.py to calculate the weighted mean using decimal precision of a rate_list using weight_list where weight_list is a list of associated loan amounts
	- This function was written to deal with a type mismatch error when using numpy.average
	- Takes a list of rate spreads as rate_list and a list of loan amounts as weight_list


- calc_median_11_12
	- Called by fill_medians_11_12 in aggregation.py
	- Uses numpy.median to calculate the median of a list of rate spreads
	- Takes a dictionary object as container, a list of lists containing section headings as list_name, section as a string, section_index as an integer, key_plural as a string, and a list of rates as ratespread_list
	- Section, section_index and key_plural are used to access layers of the  dictionary


- fill_by_characteristics
	- Called by compile_report_3_1, fill_report_11_12, compile_report_A_4 which are all in aggregation.py
	- Increments count and sums values of parsed LAR rows into different sections of a dictionary
	- Takes a dictionary object as container, a parsed LAR row as inputs, section as a string, section_index as an integer, key as a string, key_index as an integer, section2 as a string, and section2_index as an integer
	- Section, section_index, key, key_index, section2, section2_index are all used to access different levels of the dictionary


- fill_report_11_12
	- Called by compile_report_11_x, compile_report_12_1, compile_report_12_2 which are all in aggregation.py
	- Calls fill_by_characteristics to aggregate parsed LAR rows into appropriate sections of the dictionary
	- Takes a dictionary object as container, a parsed LAR row as inputs, a key as a string, and key_index as an integer
	- Key and key_index are pased to fill_by_characteristics and are used to access different sections of the dictionary


- compile_report_12_1
	- Called by aggregate_report in constructor.py
	- Calls fill_report_11_12 to aggregate parsed LAR rows by action taken (application disposition)
	- Takes a dictionary object as table12x and a parsed LAR row as inputs


- compile_report_12_2
	- Called by aggregate_report in constructor.py
	- Calls fill_11_12_rates and fill_11_12_weights from aggregation.py to fill the rate lists used to calculate means and medians
	- Calls fill_report_11_12 from aggregation.py to aggregated parsed LAR rows by their rate spread index
	- Takes a dictionary object as table12x and a parsed LAR row as inputs


- compile_report_11_x
	- Called by aggregate_report in constructor.py
	- Calls fill_11_12_rates and fill_11_12_weights from aggregation.py to fill the rate lists used to calculate means and medians
	- Calls fill_report_11_12 from aggregation.py to aggregated parsed LAR rows by their rate spread index
	- Takes a dictionary object as table11x and a parsed LAR row as inputs


- fill_means_11_12
	- Called by aggregate_report in constructor.py
	- Calls calc_mean_11_12 to calculate a list of means and place them in the appropriate section of the dictionary
	- Takes a dictionary object as table_X to store aggregated loan data and a builder.py object as build_X to reference list names


- fill_medians_11_12
	- Called by aggregate_report in constructor.py
	- Calls calc_median_11_12 to calculate a list of means and place them in the appropriate section of the dictionary
	- Takes a dictionary object as table_X to store aggregated loan data and a builder.py object as build_X to reference list names


- compile_report_A_x
	- Called by aggregate_report in constructor.py
	- Aggregates parsed LAR rows by action taken (application disposition), lien status, loan type, loan purpose, and preapproval status
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_A_4
	- Called by aggregate_report in constructor.py
	- Calls fill_by_characteristics to aggregate parsed LAR rows by race, ethnicity, minority status, income, gender, minority population percent, tract to MSA income category, and preapproval status
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_B
	- Called by aggregate_report in constructor.py
	- Calls fill_rates_B from aggregation.py to store rate spreads for calculating means and medians for report B
	- Aggregates parsed LAR rows by property type, lien status, loan purpose, hoepa status, reporting of pricing information, and means and medians of rate spreads
	- Takes a dictionary object as container and a parsed LAR row as inputs

- fill_table_B_mean
	- Called by aggregate_report in constructor.py
	- Uses numpy to calculate means from table_B_rates and then inserts them into the appropriate section of the dictionary
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_rates_B
	- Called by compile_report_B in aggregation.py
	- Appends to aggregation.table_B_rates rate spreads, as a decimal, for loans with reported pricing information
	- Table_B_rates is nested as follows: property_type, lien_status, loan purpose
	- Takes a parsed LAR row as inputs


## median_age_API
- get_age
	- Called by median_tract_age in parse_inputs in parsing.py
	- Uses the requests library to query the Census ACS5 API using the B25035_001E endpoint by supplying state, tract, and county information to return the median housing stock age of a census tract
	- For bulk use, an API key is required, this is parsed in from a file using the directory path /Users/roellk/Documents/api_key.txt
	- API keys are free from Census.gov


## check_file
- __init__
	- Imports a dictionary of state names and abbreviations
	- Imports a dictionary of MSA names and numbers
	- Takes a builder.py object as build_object


- write_JSON
	- Called by the is_file function in the check_file class in file_check.py
	- Takes report_type as a string, report_year as a string, and report_list as a list of strings
	- Writes the msa-mds.json file to a path using report_type, report_year and report_list[key]


- is_file
	- Called by controller.py
	- Takes report_type as a string, report_year as a string, and report_list as a list of strings
	- Loops over all states and MSAs to determine which MSAs have reports in sub-folders, if reports exist an msa-mds.json file is written into the state folder
	- The msa-mds.json file lists MSA names and numbers


## report_list_maker
- __init__
	- Initializes  a build_JSON object from builder.py
	- Uses a build_object (a build_object) passed from controller.py to create a dictionary with state names and abbreviations and a dictionary with MSA numbers and names


- write_JSON
	- Called by report_lists in class report_list_maker in report_list.py
	- Takes a file name, data, and file path and writes a JSON object with the given file name to the given path


- report_lists
	- Called by controller.py
	- Searches the directory structure containing the JSON report objects and creates a json file listing all reports created for each MSA
	- Takes a report_type as a string to use in search and write paths
	- Takes a report_year as a string to use in search and write paths
	- Takes a report_list as a list of strings from which the function pulls elements to use in search and write paths






