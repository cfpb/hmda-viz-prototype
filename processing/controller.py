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

print "headed into loop"
for num in range(0,end):
    #fetch one row from the LAR
    row = cur.fetchone()
    parsed.parse_t31(row) #parse the row and store in the inputs dictionary - parse_inputs.inputs
    if num == 0:
        #build the report JSON object
        build.set_header(parsed.inputs, MSA)
        build.build_JSON(parsed.inputs, MSA)

    #aggregate the loan into appropriate rows for the table
    agg.by_race(build.container, parsed.inputs) #aggregate loan by race
    agg.by_ethnicity(build.container, parsed.inputs) #aggregate loan by ethnicity
    agg.by_minority_status(build.container, parsed.inputs) #aggregate loan by minority status

build.write_JSON('test_report')
build.print_JSON()


