#Developer Documentation for Aggregate and Disclsoure Processing

For information on dependancies and running the code see [readme.md](https://github.com/cfpb/hmda-viz-prototype/blob/gh-pages/processing/readme.md)


#Files
- parsing.py
	- Called by report_4x and report_x in constructor.py
	- Parses LAR rows by report series and stores rate lists for use in calculating means and medians
	- Imports msa_indexing, median_age_api, demographics_indexing, and connector

- aggregation.py
	- Called by constructor.py to fill dictionary objects prior to conversion to JSON objects
	- Calculates means, medians, weighted means, and weighted medians
	- Imports numpy and decimal

- builder.py


- connector.py
- controller.py
- constructor.py
- demographics_indexing.py
- file_check.py
- median_age_api.py

- queries.py
- report_list.py
- selector.py

#Explanation of Classes and Methods


## parse_inputs
- __init__
	- Initializes lists to hold weights and rates that are used to calculate means, medians, weighted means, and weighted medians
	- Initializes a dictionary for tract median age which stores the median age of housing stock as a value and an 11 digit census tract as a key
	- Initializes the inputs dictionary which holds all information parsed from the LAR row or derived from functions that index information for aggregation in dictionary objects and subsequent storage as JSON files


- parse_3_1
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Called by function report_x in class_report construction in file constructor.py
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
	- Called by function report_x in class_report construction in file constructor.py
	- Parses LAR rows and stores the components in a dictionary to bused as needed for processing report 3-2
	- Calls rate_spread_index_3_2 to assign an index to each rate spread



- parse_4_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 4 series of reports and stores them in the inputs dictionary
	- Called by function report_x in class_report construction in file constructor.py
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan
	- Calls set_gender from demographics to set a single index integer for the gender of the loan



- parse_5_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 5 series of reports and stores them in the inputs dictionary
	- Called by function report_x in class_report construction in file constructor.py
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
	- Called by function report_x in class_report construction in file constructor.py
	- Calls minority_percent from MSA_info to assign an integer index according to the minority population percent
	- Calls tract_to_MSA_income to assign an integer index to the tract to MSA income ratio


- parse_8_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 8 series of reports and stores them in the inputs dictionary
	- Called by function report_x in class_report construction in file constructor.py
	- Calls adjust_denial_index from parse_inputs in parsing.py to change the denial reason code to an integer index that matches the JSON structure for data ouput
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan
	- Calls set_gender from demographics to set a single index integer for the gender of the loan
	- Calls denial_reasons_list from parse_inputs in parsing.py to create a list of denial reasons and store it in puts


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
	- Called by function report_x in class_report construction in file constructor.py
	- Calls set_loan_index to change the loan type to match the index used in the JSON structure for report 9
	- Calls median_age_index to assign an integer index an integer index based on the median age of housing stock in the loan's census tract
	- Sets the median age for the loan by passing the 11 digit census tract number to  the tract_median_ages dictionary in parse_inputs in parsing.py

- set_loan_index
	- Called by parse_9_x
	- Takes loan_purpose as a string, loan_type as an integer and property_type as a string
	- Returns a single integer index to sort the loans into the JSON structure based on the passed parameters


- median_tract_age
	- Instantiates median_age_API from median_age_api.py
	- Called by the report_x function in the report_construction class in file constructor.py
	- Fills the tract_median_ages dictionary in parse_inputs with the median housing stock ages for each tract in an MSA by making queries agains the database holding LAR data
	- Queries the Census ACS 5 year API to get the median housing stock age for a tract using the B25035_001E end-point

- median_age_index
	- Called by parse_9_x in parse_inputs in parsing.py
	- Returns a single integer index based on current report format (this index changes approximately every 10 years) that is used to aggregate loans into the JSON structure


- parse_11_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 11 series of reports and stores them in the inputs dictionary
	- Called by the report_x function in the report_construction class in file constructor.py
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls tract_to_MSA_income to return a single integer index for the loan's tract to MSA income ratio
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls rate_spread_index_11_x from demographics to return a single integer index for the loan's rate spread variable
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan
	- Calls set_gender from demographics to set a single index integer for the gender of the loan


- parse_12_x
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the 12 series of reports and stores them in the inputs dictionary
	- Called by the report_x function in the report_construction class in constructor.py
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls tract_to_MSA_income to return a single integer index for the loan's tract to MSA income ratio
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls minority_percent from MSA_info to assign a single integer index to the loan based on the minority population percent in the loan's census tract
	- Calls rate_spread_index_11_x from demographics to return a single integer index for the loan's rate spread variable
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan
	- Calls set_gender from demographics to set a single index integer for the gender of the loan


- parse_A_x
	- Called by the report_x function the report_construction class in constructor.py
	- Parses a LAR row into components required for the A series of reports (excluding A 4) and stores them in the inputs dictionary


- action_taken_index
	- Called by parse_A_x in parse_inputs in parsing.py
	- Adjust the action taken code to match the JSON structure of the report


- purpose_index
	- Called by parse_A_x in parse_inputs in parsing.py
	- Adjust the loan purpose code to match the JSON structure of the report


- parse_A_4
	- Instantiates MSA_info from msa_indexing.py and demographics from demographics_indexing.py
	- Parses a LAR row into components required for the A 4 reports and stores them in the inputs dictionary
	- Called by the report_x function in the report_construction class in constructor.py
	- Calls make_race_list from the parse_inputs class in parsing.py to store applicant and co applicant races in two lists of length 5
	- Calls tract_to_MSA_income to return a single integer index for the loan's tract to MSA income ratio
	- Calls app_income_to_MSA from MSA_info to assign an index to the applicant's income relative to the median MSA income
	- Calls minority_percent from MSA_info to assign a single integer index to the loan based on the minority population percent in the loan's census tract
	- Calls rate_spread_index_11_x from demographics to return a single integer index for the loan's rate spread variable
	- Calls set_non_white from demographics to set a boolean to True if the list of races contains minority races
	- Calls minority_count from demographics to count the total number of minority races in the race list
	- Calls set_joint from demographics to determine if the loan meets the requirements for joint status
	- Calls set_race from demographics to assign a single index integer for the race of the loan
	- Calls set_loan_ethn from demographics to assing a single index integer for the ethnicity of the loan
	- Calls set_minority_status from demographics to assign a single index integer for the minority status of the loan
	- Calls set_gender from demographics to set a single index integer for the gender of the loan


- parse_B_x
	- Instantiates the demographics class from demographics_indexing.py
	- Parses a LAr row into components required for the B series of reports and stores them in the inputs dictionary
	- Calls rate_spread_index_11_X to assign a single integer index to the loan based on the loan's reported rate spread


##aggregate
- __init__
	- Initializes lists used for calculating means, medians, weighted means, and weighted medians
	- Holds lists used in other functions


- create_rate_list
	- called by __init__ to establish lists of length n
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
	- Called by fill_weidhted_medians_11_12 and fill_by_weighted_median_3_2 in aggregation.py
	- Calculates the weighted median value using a list of rate spreads and a list of loan values
	- The weighted median is found by taking n/2 steps through the sorted rate list where n is the length of the list and a step is the average loan value from the weight list.


- fill_weighted_medians_11_12
	- Called by report_x in constructor.py to fill the weighted median column in reports 11 and 12
	- Calls calc_weighted_median from aggregation.py to calculate the weighted medians
	- Takes a dictionary object as container and the a parsed LAR row as inputs


- fill_totals_3_1
	- Called by build_report_31 to fill the totals section of report 3-1
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_3_1
	- Called by report_x in constructor.py to fill the dictionary object
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
	- Called by report_x in constructor.py
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
	- Called by report_x in constructor.py
	- Aggregates loans by median for report 3-2
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_by_weighted_median_3_2
	- Called by report_x in constructor.py
	- Aggregates loans by weighted median for report 3-2
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_3_2
	- Called by report_x in constructor.py
	- Aggregates LAR rows for table 3-2 using by_pricing_status, by_rate_spread, by_hoepa_status, fil_rate_lists, and fill_weight_lists
	- Takes a dictionary object as table32 and a parsed LAR row as inputs


- compile_report_4_x
	- Called by report_x in constructor.py
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
	- Called by report_x in constructor.py
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
	- Called by report_x in constructor.py
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
	- Called by report_x in aggregation.py
	- Calls fill_by_tract_characteristics, fill_by_income_ethnic_combo, and fill_by_geo_type to fill the 7 series of reports
	- Takes a dictionary objet as table7x and a parsed LAR row as inputs


- fill_by_denial_percent
	- Called by report_x in constructor.py
	- Fills the percent (%) column for each denial reason by dividing the a cell's count by the total for the row
	- Takes a dictionary object as container, a parsed LAR row as inputs, index_num which determines the row on the report, and key which is a string used to access the sub-section of the container dictionary


- fill_by_denial_reason
	- Called by compile_report_8_x in aggregation.py
	- Aggregates parsed LAR rows by denial reason for rows determined by passed parameters, reason is used to select the column for aggregation
	- Takes a dictionary object as container, a parsed LAR row as inputs, index_num to determine the row for aggregation, a key and key_singular to access the appropriate sub-sec tion of the dictionary


- compile_report_8_x
	- Called by report_x in constructor.py
	- Calls fill_by_denial_reason from aggregation.py to fill the 8 series of reports with parsed LAR rows
	- Takes a dictionary object as table8x and a parsed LAR row as inputs


- compile_report_9_x
	- Called by report_x in construtor.py
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
	- Called by report_x in constructor.py
	- Calls fill_report_11_12 to aggregate parsed LAR rows by action taken (application disposition)
	- Takes a dictionary object as table12x and a parsed LAR row as inputs


- compile_report_12_2
	- Called by report_x in constructor.py
	- Calls fill_11_12_rates and fill_11_12_weights from aggregation.py to fill the rate lists used to calculate means and medians
	- Calls fill_report_11_12 from aggregation.py to aggregated parsed LAR rows by their rate spread index
	- Takes a dictionary object as table12x and a parsed LAR row as inputs


- compile_report_11_x
	- Called by report_x in constructor.py
	- Calls fill_11_12_rates and fill_11_12_weights from aggregation.py to fill the rate lists used to calculate means and medians
	- Calls fill_report_11_12 from aggregation.py to aggregated parsed LAR rows by their rate spread index
	- Takes a dictionary object as table11x and a parsed LAR row as inputs


- fill_means_11_12
	- Called by report_x in constructor.py
	- Calls calc_mean_11_12 to calculate a list of means and place them in the appropriate section of the dictionary
	- Takes a dictionary object as table_X to store aggregated loan data and a builder.py object as build_X to reference list names


- fill_medians_11_12
	- Called by report_x in constructor.py
	- Calls calc_median_11_12 to calculate a list of means and place them in the appropriate section of the dictionary
	- Takes a dictionary object as table_X to store aggregated loan data and a builder.py object as build_X to reference list names


- compile_report_A_x
	- Called by report_x in constructor.py
	- Aggregates parsed LAR rows by action taken (application disposition), lien status, loan type, loan purpose, and preapproval status
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_A_4
	- Called by report_x in constructor.py
	- Calls fill_by_characteristics to aggregate parsed LAR rows by race, ethnicity, minority status, income, gender, minority population percent, tract to MSA income category, and preapproval status
	- Takes a dictionary object as container and a parsed LAR row as inputs


- compile_report_B
	- Called by report_x in constructor.py
	- Calls fill_rates_B from aggregation.py to store rate spreads for calculating means and medians for report B
	- Aggregates parsed LAR rows by property type, lien status, loan purpose, hoepa status, reporting of pricing information, and means and medians of rate spreads
	- Takes a dictionary object as container and a parsed LAR row as inputs

- fill_table_B_mean
	- Called by report_x in constructor.py
	- Uses numpy to calculate means from table_B_rates and then inserts them into the appropriate section of the dictionary
	- Takes a dictionary object as container and a parsed LAR row as inputs


- fill_rates_B
	- Called by compile_report_B in aggregation.py
	- Appends to aggregation.table_B_rates rate spreads, as a decimal, for loans with reported pricing information
	- Table_B_rates is nested as follows: property_type, lien_status, loan purpose
	- Takes a parsed LAR row as inputs