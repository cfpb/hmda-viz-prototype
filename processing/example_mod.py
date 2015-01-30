import json
import psycopg2
import psycopg2.extras
from collections import OrderedDict

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

SQL = '''SELECT
            censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
            coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
            applicantethnicity, coapplicantethnicity, applicantincome, ratespeed, lienstatus, hoepastatus,
            purchasertype, loanamount,sequencenumber, asofdate, statecode, censustractnumber, countycode
        FROM hmda_lar_public_final_2012 WHERE msaofproperty = %s limit 10; '''


MSA = '36540'
location = (MSA,)
cur.execute(SQL, location)

container = OrderedDict({})
container['table'] = '3-1'
container['type'] = 'aggregate'
container['desc'] = 'Loans sold. By characteristics of borrower and census tract in which property is located and by type of purchaser (includes originations and purchased loans).'
container['year'] = '2013'

msa = OrderedDict({})
msa['id'] = '11500'
msa['name'] = 'Anniston-Oxford'
msa['state'] = 'AL'
container['msa'] = msa

borrowercharacteristcs = []

rows = cur.fetchall()
for index, row in enumerate(rows):
    holding = {}

    purchasers = []
    purchasersholding = OrderedDict({})
    purchasersholding['name'] = "{} {}".format("name", index)
    purchasersholding['count'] = index
    purchasersholding['value'] = index+100
    purchasers.append(purchasersholding)

    races = []
    racesholding = OrderedDict({})
    racesholding['race'] = "{} {}".format("race", index)
    racesholding['purchasers'] = purchasers
    races.append(racesholding)

    holding['characteristic'] = "{} {}".format("Race", index)
    holding['races'] = races

    borrowercharacteristcs.append(holding)

container['borrowercharacteristcs'] = borrowercharacteristcs

print json.dumps(container, indent=4)




