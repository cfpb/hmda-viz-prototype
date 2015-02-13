import json
import os
import csv
import psycopg2
import psycopg2.extras
from collections import OrderedDict
#import the parse_inputs class to store the 'inputs' dictionary
from A_D_library import parse_inputs as parse
from A_D_library import connect_DB as connect
from A_D_library import build_JSON as build
from A_D_library import aggregate as agg
from A_D_library import queries

#instantiate library functions
parsed = parse() #for parsing inputs from rows
connection = connect() #connects to the DB
build31 = build() #table 3-1 build object
build32 = build() #table 3-2 build object
queries = queries() #query text for all tables
agg = agg() #aggregation functions for all tables
cur = connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres

def build_report_31(num):
	#aggregate loans by types
	agg.by_race(table31, parsed.inputs) #aggregate loan by race
	agg.by_ethnicity(table31, parsed.inputs) #aggregate loan by ethnicity
	agg.by_minority_status(table31, parsed.inputs) #aggregate loan by minority status (binary determined by race and ethnicity)
	agg.by_applicant_income(table31, parsed.inputs) #aggregates by ratio of appicant income to tract median income (census)
	agg.by_minority_composition(table31, parsed.inputs) #aggregates loans by percent of minority residents (census)
	agg.by_tract_income(table31, parsed.inputs) #aggregates loans by census tract income rating - low/moderate/middle/upper
	agg.totals(table31, parsed.inputs) #aggregate totals for each purchaser
	return table31

def build_report_32(num):
	table_type = 'aggregate' #this will be in the input file

	#aggregate loans by types
	agg.by_pricing_status(table32, parsed.inputs) #aggregate count by lien status
	agg.by_rate_spread(table32, parsed.inputs) #aggregate loans by percentage points above APOR as ##.##%
	agg.by_hoepa_status(table32, parsed.inputs) #aggregates loans by presence of HOEPA flag
	agg.rate_sum(table32, parsed.inputs) #sums spreads above APOR for each loan purchaser, used to determine medians
	agg.fill_median_lists(parsed.inputs) #fills the median rate spread for each purchaser
	return table32

report31_list = [] #holds the list of MSAs that will have report 3-1 built
report32_list = [] #holds the list of MSAs that will have report 3-2 built

#file has MSA list (entire population)
#flag for aggregate
#flag for each aggregate report (1 print, 0 don't print)
#list of FIs in MSA to generate reports for?
#open the controller file that tells which reports to generate
with open('MSAinputs.csv', 'r') as csvfile:
    msareader = csv.reader(csvfile, delimiter = ',', quotechar='"')
    for row in msareader:
        if row[4] =='1':
            report31_list.append(row[0])
        #command_rows.append(row)
        if row[5] == '1':
            report32_list.append(row[0])
#for disclosure reports pass a list of FIs and MSAs to the control loop (does this need to be a separate control loop? can there be an optional parameter for FI?)

for MSA in report31_list:
	location = (MSA,)
	SQL = queries.count_rows_2012() #get query text for getting count of loans for the MSA
	cur.execute(SQL, location) #ping the database for numbers!
	count = cur.fetchone() #get count of rows for the MSA
	end = int(count[0]) #set count to an integer from a list of long type
	print end, 'LAR rows in MSA %s, for report 3-1' %MSA
	SQL = queries.table_3_1() #set query text to table 3-1
	cur.execute(SQL, location) #execute the query in postgres

	for num in range(0, end): #loop through all LAR rows in the MSA
		row = cur.fetchone() #fetch one row from the LAR
		parsed.parse_t31(row) #parse the row and store in the inputs dictionary - parse_inputs.inputs
		if num == 0:
			build31.set_header(parsed.inputs, MSA, build31.table_headers('3-1'), 'aggregate', '3-1') #set the header information for the report
			table31 = build31.table_31_builder() #build the JSON object for the report
		agg.build_report_31(table31, parsed.inputs) #aggregate loan files into the JSON structure
	#aggregate/year/state name/msa name/ table number.json
	MSA_name = 'council bluffs' #should be table31['msa']['name']
	#need to split the paths for each report
	path = "json"+"/"+table31['type']+"/"+table31['year']+"/"+build31.get_state_name(table31['msa']['state'])+"/"+MSA_name #set path for writing the JSON file by geography
	if not os.path.exists(path): #check if path exists
		os.makedirs(path) #if path not present, create it
	build31.write_JSON('3_1.json', table31, path)


for MSA in report32_list: #loop over all MSAs that had report 3-2 flagged for creation
	location = (MSA,)
	SQL = queries.count_rows_2012()
	cur.execute(SQL, location) #Query the database for number of rows in the LAR in the MSA
	count = cur.fetchone() #get tuple of LAR rows in MSA
	end = int(count[0]) #convert the tuple to int for use in the control loop
	print end, 'LAR rows in MSA %s, for report 3-2' %MSA
	SQL = queries.table_3_2() #set query text for table 3-3
	cur.execute(SQL, location)

	for num in range(0,end):
		row = cur.fetchone() #pull a single row for parsing and aggregation
		parsed.parse_t31(row) #parse the row into a dictionary
		if num == 0:
			build32.set_header(parsed.inputs, MSA, build32.table_headers('3-2'), 'aggregate', '3-2') #set the header information for the report
			table32 = build32.table_32_builder() #build the JSON object for the report
		agg.build_report_32(table32, parsed.inputs)
	agg.by_median(table32, parsed.inputs) #this stays outside the loop
	agg.by_mean(table32, parsed.inputs) #this stays outside the loop

	MSA_name = 'council bluffs' # temp until sql table is modified: should be table31['msa']['name']
	path = "json"+"/"+table32['type']+"/"+table32['year']+"/"+build32.get_state_name(table32['msa']['state'])+"/"+MSA_name #directory path to store JSON object
	if not os.path.exists(path): #check if path exists
		os.makedirs(path) #if path not present, create it
	build32.write_JSON('3_2.json', table32, path) #write the json into the correct path


