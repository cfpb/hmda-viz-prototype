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
queries = queries() #query text for all tables
agg = agg() #aggregation functions for all tables
selector = selector() #holds lists of reports to be generated for each MSA

cur = connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
selector.get_report_lists('MSAinputs2013.csv') #fills the dictionary of lists of reports to be generated

build_msa = build() #instantiate the build object
build_msa.msas_in_state(cur, selector) #creates a list of all MSAs in each state and places the file in the state's folder
print selector.report_list['year']
for MSA in selector.report_list['A 3-1']:
	build31 = build() #table 3-1 build object
	build31.set_msa_names(cur)
	location = (MSA,) #pass a tuple list to psycopg2, the library only takes tuples as inputs

	if selector.report_list['year'][1] == '2012': #use the year on the first line of the MSA inputs file to set the query
		SQL = queries.count_rows_2012() #get query text for getting count of loans for the MSA
	elif selector.report_list['year'][1] == '2013': #use the year on the first line of the MSA inputs file to set the query
		SQL = queries.count_rows_2013() #get query text for getting count of loans for the MSA

	cur.execute(SQL, location) #ping the database for numbers!
	count = int(cur.fetchone()[0]) #get count of rows for the MSA
	#add md numbers to input file list of msas, check name against last 5 digits if msa name has 0 rows or errors on check
	print count, "LAR rows in MSA %s, for report 3-1" %MSA
	if count > 0:
		print count, 'LAR rows in MSA %s, for report 3-1, in %s' %(MSA, selector.report_list['year'][1])
		if selector.report_list['year'][1] == '2013': #use the year on the first line of the MSA inputs file to set the query
			SQL = queries.table_3_1_2013() #set query text to table 3-1 2013
		elif selector.report_list['year'][1] == '2012': #use the year on the first line of the MSA inputs file to set the query
			SQL = queries.table_3_1_2012() #set query text to table 3-1 2012
		else:
			print "something is wrong"
		cur.execute(SQL, location) #execute the query in postgres

		for num in range(0, count): #loop through all LAR rows in the MSA
			row = cur.fetchone() #fetch one row from the LAR
			parsed.parse_t31(row) #parse the row and store in the inputs dictionary - parse_inputs.inputs
			if num == 0:
				build31.set_header(parsed.inputs, MSA, build31.table_headers('3-1'), 'Aggregate', '3-1') #set the header information for the report
				table31 = build31.table_31_builder() #build the JSON object for the report
			agg.build_report_31(table31, parsed.inputs) #aggregate loan files into the JSON structure


		path = "json"+"/"+table31['type']+"/"+table31['year']+"/"+build31.get_state_name(table31['msa']['state']).lower()+"/"+build31.msa_names[MSA].replace(' ', '-').lower() + "/" +table31['table']#set path for writing the JSON file by geography
		if not os.path.exists(path): #check if path exists
			os.makedirs(path) #if path not present, create it
		build31.write_JSON('3-1.json', table31, path)
		build31.jekyll_for_report(path) #create and write jekyll file to report path
		#year in the path is determined by the asofdate in the LAR entry
		path2 = "json"+"/"+table31['type']+"/"+table31['year']+"/"+build31.get_state_name(table31['msa']['state']).lower()+"/"+build31.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
		build31.jekyll_for_msa(path2) #create and write jekyll file to the msa path
	else:
		pass #do nothing if no LAR rows exist for the MSA

for MSA in selector.report_list['A 3-2']: #loop over all MSAs that had report 3-2 flagged for creation
	build32 = build() #table 3-2 build object
	build32.set_msa_names(cur)
	location = (MSA,)
	if selector.report_list['year'][1] == '2013': #use the year on the first line of the MSA inputs file to set the query
		SQL = queries.count_rows_2013()
	elif selector.report_list['year'][1] == '2012': #use the year on the first line of the MSA inputs file to set the query
		SQL = queries.count_rows_2012()
	cur.execute(SQL, location) #Query the database for number of rows in the LAR in the MSA
	count = int(cur.fetchone()[0]) #get tuple of LAR rows in MSA
	#end = int(count[0]) #convert the tuple to int for use in the control loop
	if count > 0:
		print count, 'LAR rows in MSA %s, for report 3-2' %(MSA, selector.report_list['year'][1])
		if selector.report_list['year'][1] == '2013':
			SQL = queries.table_3_2_2013() #set query text for table 3-2
		elif selector.report_list['year'][1] == '2012':
			SQL = queries.table_3_2_2012() #set query text for table 3-2
		else:
			print "something is wrong"
		cur.execute(SQL, location)
		for num in range(0,count):
			row = cur.fetchone() #pull a single row for parsing and aggregation
			parsed.parse_t32(row) #parse the row into a dictionary
			if num == 0:
				build32.set_header(parsed.inputs, MSA, build32.table_headers('3-2'), 'Aggregate', '3-2') #set the header information for the report
				table32 = build32.table_32_builder() #build the JSON object for the report
			agg.build_report_32(table32, parsed.inputs)
		agg.by_median(table32, parsed.inputs) #this stays outside the loop
		agg.by_mean(table32, parsed.inputs) #this stays outside the loop

		#move this section into the library
		MSA_name = 'council bluffs' # temp until sql table is modified: should be table31['msa']['name']
		path = "json"+"/"+table32['type']+"/"+table32['year']+"/"+build32.get_state_name(table32['msa']['state']).lower()+"/"+build32.msa_names[MSA].replace(' ', '-').lower() + "/" + table32['table'] #directory path to store JSON object
		if not os.path.exists(path): #check if path exists
			os.makedirs(path) #if path not present, create it
		build32.write_JSON('3-2.json', table32, path) #write the json into the correct path
		build32.jekyll_for_report(path)#create and write jekyll file to report path
		#year in the path is determined by the asofdate in the LAR entry
		path2 = "json"+"/"+table32['type']+"/"+table32['year']+"/"+build32.get_state_name(table32['msa']['state']).lower()+"/"+build32.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
		build32.jekyll_for_msa(path2) #create and write jekyll file to the msa path

	else:
		pass #do nothing if no LAR rows exist for the MSA
