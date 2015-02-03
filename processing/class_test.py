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


#get MSA from read file, may need a loop here to pass single tuples to psycopg2
#for msa in list, pass each MSA to location for use in psycop
MSA = '36540'
#store MSAs as tuples for psycopg2
location = (MSA,)



#if report 3-1 is selected: need a function to read in report generation parameters
SQL = queries.table_3_1()
cur.execute(SQL, location)
#fetch one row from the LAR
row = cur.fetchone()

#parse the row and store in the inputs dictionary - parse_inputs.inputs
parsed.parse_t31(row)
#build the report JSON object
build.set_header(parsed.inputs, MSA)
build.build_JSON(parsed.inputs, MSA)
#print JSON
#build.print_JSON()
#write JSON file

agg.by_race(build.container, parsed.inputs)
agg.by_ethnicity(build.container, parsed.inputs)
agg.by_minority_status(build.container, parsed.inputs)
build.write_JSON('test_report')
#build.container['year'] = parsed.inputs['year']
#print "\nparsed\n", "*"*20, "\n", parsed.inputs
#print "\ncontainer\n", "*"*20, "\n", build.container


#print row['censustractnumber']
#parse inputs function construction
