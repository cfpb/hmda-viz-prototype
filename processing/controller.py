import json
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
build = build()
queries = queries()
agg = agg()

#set cursor object
cur = connection.connect()

#set MSA list
MSA = '36540'
location = (MSA,)

#get count for looping over rows in the MSA
SQL = queries.count_rows_2012() #get query text for getting count of loans for the MSA
cur.execute(SQL, location) #ping the database for numbers!
count = cur.fetchone() #get cont of rows for the MSA
end = int(count[0]) #set count to an integer from a list of long type
print end

#if report 3-1 is selected: need a function to read in report generation parameters
SQL = queries.table_3_1()
cur.execute(SQL, location)

json_data = open('JSON_out.json')
cont = OrderedDict(json.load(json_data))

for num in range(0,end):
	#print "in loop"
	#fetch one row from the LAR
	row = cur.fetchone()
	parsed.parse_t31(row) #parse the row and store in the inputs dictionary - parse_inputs.inputs

	#aggregate the loan into appropriate rows for the table
	agg.by_race(cont, parsed.inputs) #aggregate loan by race
	agg.by_ethnicity(cont, parsed.inputs) #aggregate loan by ethnicity
	agg.by_minority_status(cont, parsed.inputs) #aggregate loan by minority status
	agg.by_applicant_income(cont, parsed.inputs)
	agg.by_minority_composition(cont, parsed.inputs)
	agg.by_tract_income(cont, parsed.inputs)
	agg.totals(cont, parsed.inputs) #aggregate totals for each purchaser

print "out of loop"
print json.dumps(cont, indent=4)
name = 'sample.json'
build.write_JSON(name)


