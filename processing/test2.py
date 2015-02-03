import json
import psycopg2
import psycopg2.extras
from collections import OrderedDict

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

purchaser_names = ['Loan was not originated or was not sold in calendar year', 'Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Pacific Islander', 'White', 'Not Provided', 'Not Applicable', 'No co-applicant']

borrowercharacteristics = []
purchasers = []

for purchaser in purchaser_names:
    purchasersholding =OrderedDict({})
    purchasersholding['name'] = "{}".format(purchaser)
    purchasersholding['count'] = 0
    purchasersholding['value'] = 0
    purchasers.append(purchasersholding)

races = []
temp = {}
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
container['borrower-characteristics'] = borrowercharacteristics

print json.dumps(container, indent=4)

