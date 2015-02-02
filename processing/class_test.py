import json
import psycopg2
import psycopg2.extras
from collections import OrderedDict
#import the parse_inputs class to store the 'inputs' dictionary

from A_D_library import parse_inputs as parse
from A_D_library import connect_DB as connect

connection = connect()
cur = connection.connect()
'''
with open('/Users/roellk/Desktop/python/credentials.txt', 'r') as f:
    credentials = f.read()

cred_list = credentials.split(',')
dbname = cred_list[0]
user = cred_list[1]
host = cred_list[2]
password = cred_list[3]

#set a string for connection to SQL
connect_string = "dbname=%s user=%s host=%s password =%s" %(dbname, user, host, password)

try:
    conn = psycopg2.connect(connect_string)
    print "i'm connected"
#if database connection results in an error print the following
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
'''

#get MSA from read file, may need a loop here to pass single tuples to psycopg2
#for msa in list, pass each MSA to location for use in psycop
MSA = '36540'
#store MSAs as tuples for psycopg2
location = (MSA,)

#pull SQL from report query class
#use read file to specify which queries, may need a loop to execute multiple report types
#load queries class and instantiate it
from A_D_library import queries
queries = queries()
#if report 3-1 is selected: need a function to read in report generation parameters
SQL = queries.table_3_1()



cur.execute(SQL, location)

row = cur.fetchone()
#print row
parsed = parse()
parsed.parse_t31(row)
print parsed.inputs


#print row['censustractnumber']
#parse inputs function construction
