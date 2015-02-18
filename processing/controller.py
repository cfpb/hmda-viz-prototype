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
from A_D_library import report_selector as selector
#instantiate library functions
#add a year column to the HMDA input file
#use the year column to select whichd databases to connect to (create more functions for each year)

parsed = parse() #for parsing inputs from rows
connection = connect() #connects to the DB
build31 = build() #table 3-1 build object
build32 = build() #table 3-2 build object
queries = queries() #query text for all tables
agg = agg() #aggregation functions for all tables
selector = selector() #holds lists of reports to be generated for each MSA
cur = connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
selector.get_report_lists('MSAinputs.csv') #fills the dictionary of lists of reports to be generated
build31.set_msa_names(cur)
build32.set_msa_names(cur)
for MSA in selector.report_list['A 3-1']:
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

#move this section into the library
	#aggregate/year/state name/msa name/ table number.json
	print build31.msa_names[MSA]
	#need to split the paths for each report
	path = "json"+"/"+table31['type']+"/"+table31['year']+"/"+build31.get_state_name(table31['msa']['state']).lower()+"/"+build31.msa_names[MSA].replace(' ', '-') + "/" +table31['table']#set path for writing the JSON file by geography
	if not os.path.exists(path): #check if path exists
		os.makedirs(path) #if path not present, create it
	build31.write_JSON('3_1.json', table31, path)

for MSA in selector.report_list['A 3-2']: #loop over all MSAs that had report 3-2 flagged for creation
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
		parsed.parse_t32(row) #parse the row into a dictionary
		if num == 0:
			build32.set_header(parsed.inputs, MSA, build32.table_headers('3-2'), 'aggregate', '3-2') #set the header information for the report
			table32 = build32.table_32_builder() #build the JSON object for the report
		agg.build_report_32(table32, parsed.inputs)
	agg.by_median(table32, parsed.inputs) #this stays outside the loop
	agg.by_mean(table32, parsed.inputs) #this stays outside the loop

	#move this section into the library
	MSA_name = 'council bluffs' # temp until sql table is modified: should be table31['msa']['name']
	path = "json"+"/"+table32['type']+"/"+table32['year']+"/"+build32.get_state_name(table32['msa']['state']).lower()+"/"+build32.msa_names[MSA].replace(' ', '-') + "/" + table32['table'] #directory path to store JSON object
	if not os.path.exists(path): #check if path exists
		os.makedirs(path) #if path not present, create it
	build32.write_JSON('3_2.json', table32, path) #write the json into the correct path


