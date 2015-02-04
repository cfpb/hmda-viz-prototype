import json
import psycopg2
import psycopg2.extras
from collections import OrderedDict

def build():
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

    #FFIEC report 3-1 labels
    purchaser_names = ['Loan was not originated or was not sold in calendar year', 'Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
    race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Pacific Islander', 'White', 'Not Provided', 'Not Applicable', 'No co-applicant']
    ethnicity_names = ['Hispanic or Latino', 'Not Hispanic or Latino', 'Not provided', 'Not applicable', 'No co-applicant']
    minority_statuses = ['White Non-Hispanic', 'Others, Including Hispanic']
    applicant_income_bracket = ['Less than 50% of MSA/MD median', '50-79% of MSA/MD median', '80-99% of MSA/MD median', '100-119% of MSA/MD median', '120% or more of MSA/MD median', 'income not available']
    tract_pct_minority = ['Less than 10% minority', '10-19% minority', '20-49% minority', '50-79% minority', '80-100% minority']
    tract_income = ['Low income', 'Moderate income', 'Middle income', 'Upper income']

    #borrowercharacterisitics holds all the lists and dicts for the applicant portion table
    borrowercharacteristics = []
    #censuscharacteristics holds all the lists and dicts for the census portion of the table
    censuscharacteristics = []
    #purchasers holds the dictionary of all purchasers, values and counts for use in the JSON object
    purchasers = []
    #totals sums all the loan counts and values for each purchaser
    totals = {}

    #build purchaser dictionaries inside a list
    for purchaser in purchaser_names:
    	purchasersholding = OrderedDict({})
    	purchasersholding['name'] = "{}".format(purchaser)
    	purchasersholding['count'] = 0
    	purchasersholding['value'] = 0
    	purchasers.append(purchasersholding)

    #races = []
    #temp = {}
    Header = True
    top = OrderedDict({})
    for race in race_names:
    	holding = OrderedDict({})

    	if Header == True:
    		top['characteristic'] = 'Race'
    		top['races'] = []
    	Header = False

    	holding['race']= "{}".format(race) #race is overwritten each pass of the loop (keys are unique in dictionaries)
    	holding['purchasers'] = purchasers #purchasers is overwritten each pass in the holding dictionary
    	top['races'].append(holding)

    borrowercharacteristics.append(top)

    #build ethnicity
    top = OrderedDict({})
    Header = True
    for ethnicity in ethnicity_names:
    	holding = OrderedDict({})

    	if Header == True:
    		top['characteristic'] = 'Ethnicity'
    		top['ethnicities'] = []
    	Header = False

    	holding['ethnicity'] = "{}".format(ethnicity)
    	holding['purchasers'] = purchasers
    	top['ethnicities'].append(holding)

    borrowercharacteristics.append(top)

    #build minority status
    top = OrderedDict({})
    Header = True
    for status in minority_statuses:
    	holding = OrderedDict({})

    	if Header == True:
    		top['characteristic'] = 'Minority Status'
    		top['minoritystatuses'] = []
    	Header = False

    	holding['minoritystatus'] = "{}".format(status)
    	holding['purchasers'] = purchasers
    	top['minoritystatuses'].append(holding)
    borrowercharacteristics.append(top)

    #build applicant income to MSA/MD income brackets
    top = OrderedDict({})
    Header = True
    for bracket in applicant_income_bracket:
    	holding = OrderedDict({})
    	if Header == True:
    		top['characteristic'] = 'Income'
    		top['appincome'] = []
    	Header = False
    	holding['applicantincome'] = "{}".format(bracket)
    	holding['purchasers'] = purchasers
    	top['appincome'].append(holding)
    borrowercharacteristics.append(top)

    #build census characateristics
    #build racial ethnic composition of tracts
    top = OrderedDict({})
    Header = True
    for pct in tract_pct_minority:
    	holding = OrderedDict({})
    	if Header == True:
    		top['characteristic'] = 'Racial/Ethnic Composition'
    		top['tractpctminority'] = []
    	Header = False
    	holding['tractpctminority'] = "{}".format(pct)
    	holding['purchasers'] = purchasers
    	top['tractpctminority'].append(holding)
    censuscharacteristics.append(top)

    #build tract income levelimport json
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

#json_data = open('JSON_out.json')
#cont = OrderedDict(json.load(json_data))
cont = build.build_JSON(parsed.inputs, MSA)
print cont
print json.dumps(cont, indent=4)
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

build.set_header(parsed.inputs, MSA)
print "out of loop"
print json.dumps(cont, indent=4)
name = 'sample.json'
#uild.write_JSON(name)


