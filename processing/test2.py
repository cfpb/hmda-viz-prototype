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

    #build tract income level
    top = OrderedDict({})
    Header = True
    for level in tract_income:
    	holding = OrderedDict({})
    	if Header == True:
    		top['characteristic'] = 'Income'
    		top['incomelevel'] = []
    	Header = False
    	holding['incomelevel'] = "{}".format(level)
    	holding['purchasers'] = purchasers
    	top['incomelevel'].append(holding)
    censuscharacteristics.append(top)

    #build totals
    top = OrderedDict({})
    holding = OrderedDict({})
    totals['purchasers'] = purchasers

    container['borrowercharacteristics'] = borrowercharacteristics
    container['censuscharacteristics'] = censuscharacteristics
    container['total'] = totals
    return container
def print_json(container):
    print json.dumps(container, indent=4)

def write(container):
    name = 'sample'
    with open(name, 'w') as outfile:
         json.dump(container, outfile, indent = 4, ensure_ascii=False)
cont = build()
#print_json(cont)

print cont['borrowercharacteristics'][0]['races'][0]['purchasers'][0]['name']