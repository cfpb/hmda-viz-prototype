import json
import psycopg2
import psycopg2.extras
from collections import OrderedDict
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
parsed = parse()
connection = connect()
build31 = build()
build32 = build()
queries = queries()
agg = agg()

#set cursor object
cur = connection.connect()

#set MSA list
MSA = '36540' #this will be a list that comes from the input file
table_31 = '3-1'
table_32 = '3-2'
report_desc32 = build32.table_headers(table_31) #this will come from the input file
report_desc31 = build31.table_headers(table_32)
location = (MSA,)

table_type = 'aggregate' #this will be in the input file
#get count for looping over rows in the MSA

SQL = queries.count_rows_2012() #get query text for getting count of loans for the MSA
cur.execute(SQL, location) #ping the database for numbers!
count = cur.fetchone() #get cont of rows for the MSA
end = int(count[0]) #set count to an integer from a list of long type
#end = 5
print end

#if report 3-1 is selected: need a function to read in report generation parameters
SQL = queries.table_3_1()
cur.execute(SQL, location)

#json_data = open('JSON_out.json')
#cont = OrderedDict(json.load(json_data))
table31 = build31.table_31_builder()
table32 = build32.build_JSON32()
#print cont
#print json.dumps(cont, indent=4)
for num in range(0, end):
	#print "in loop"
	#fetch one row from the LAR
	row = cur.fetchone()
	parsed.parse_t31(row) #parse the row and store in the inputs dictionary - parse_inputs.inputs
	if num == 0:
		build31.set_header32(parsed.inputs, MSA, report_desc31, table_type, table_31)
		build32.set_header32(parsed.inputs, MSA, report_desc32, table_type, table_32)

		#aggregate the first loan into appropriate rows for the table
		if parsed.inputs['purchaser'] >=0:
			agg.by_race(table31, parsed.inputs) #aggregate loan by race
			agg.by_ethnicity(table31, parsed.inputs) #aggregate loan by ethnicity
			agg.by_minority_status(table31, parsed.inputs) #aggregate loan by minority status
			agg.by_applicant_income(table31, parsed.inputs)
			agg.by_minority_composition(table31, parsed.inputs)
			agg.by_tract_income(table31, parsed.inputs)
			agg.totals(table31, parsed.inputs) #aggregate totals for each purchaser
			agg.by_pricing_status(table32, parsed.inputs) #aggregate count by lien status
			agg.by_rate_spread(table32, parsed.inputs)
			agg.by_hoepa_status(table32, parsed.inputs)
			agg.rate_sum(table32, parsed.inputs)
			agg.fill_median_lists(parsed.inputs)
	else:
		#aggregate the subsequent loan into appropriate rows for the table
		#table 3-1

		if parsed.inputs['purchaser'] >= 0:
			agg.by_race(table31, parsed.inputs) #aggregate loan by race
			agg.by_ethnicity(table31, parsed.inputs) #aggregate loan by ethnicity
			agg.by_minority_status(table31, parsed.inputs) #aggregate loan by minority status
			agg.by_applicant_income(table31, parsed.inputs)
			agg.by_minority_composition(table31, parsed.inputs)
			agg.by_tract_income(table31, parsed.inputs)
			agg.totals(table31, parsed.inputs) #aggregate totals for each purchaser
			#table 3-2
			agg.by_pricing_status(table32, parsed.inputs) #aggregate count by lien status
			agg.by_rate_spread(table32, parsed.inputs)
			agg.by_hoepa_status(table32, parsed.inputs)
			agg.rate_sum(table32, parsed.inputs)
			agg.fill_median_lists(parsed.inputs)

agg.by_median(table32, parsed.inputs) #this stays outside the loop
agg.by_mean(table32, parsed.inputs) #this stays outside the loop

#write reports in json format
name = 'report31_' + MSA + '.json'
build31.write_JSON(name, table31)
name2 = 'report32_' + MSA + '.json'
build32.write_JSON(name2, table32)

#build.set_header32(self, inputs, MSA, desc, table_type, table_num)