from collections import OrderedDict
import json
container = OrderedDict({})
msa = OrderedDict({})
container['table'] = '3-1'
container['type'] = 'aggregate'
container['desc'] = 'Loans sold. By characteristics of borrower and census tract in which property is located and by type of purchaser (includes originations and purchased loans).'
container['year'] = '2012'
msa['id'] = '36540'
#msa['name'] = inputs['MSA name'] #need to add MSA names to a database or read-in file
msa['state'] = 'NE'
container['msa'] = msa

def set_purchasers():
	from collections import OrderedDict
	purchasers = []
	purchaser_names = ['Loan was not originated or was not sold in calendar year', 'Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
	for item in purchaser_names:

		purchasersholding = OrderedDict({})
		purchasersholding['name'] = "{}".format(item)
		purchasersholding['count'] = 0
		purchasersholding['value'] = 0

		purchasers.append(purchasersholding)
	#print json.dumps(purchasers, indent =4)
	return purchasers

def build_JSON():
	from collections import OrderedDict
	import json
	#rewrite this as a function
	#FFIEC report 3-1 labels
	purchaser_names = ['Loan was not originated or was not sold in calendar year', 'Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
	race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Pacific Islander', 'White', '2 or more minority races', 'Joint', 'Not Provided', 'Not Applicable', 'No co-applicant']
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
	purchasers1 = []
	#totals sums all the loan counts and values for each purchaser
	totals = {}

	Header = True
	top = OrderedDict({})
	for race in race_names:
		holding = OrderedDict({})

		if Header == True:
			top['characteristic'] = 'Race'
			top['races'] = []
		Header = False

		holding['race']= "{}".format(race) #race is overwritten each pass of the loop (keys are unique in dictionaries)
		purchasers = set_purchasers()
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
		purchasers = set_purchasers()
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
		purchasers = set_purchasers()
		holding['purchasers'] = purchasers
		top['minoritystatuses'].append(holding)
	borrowercharacteristics.append(top)

	#build applicant income to MSA/MD income brackets
	top = OrderedDict({})
	Header = True
	for bracket in applicant_income_bracket:
		holding = OrderedDict({})
		if Header == True:
			top['characteristic'] = 'Applicant Income'
			top['applicantincome'] = []
		Header = False
		holding['applicantincomes'] = "{}".format(bracket)
		purchasers = set_purchasers()
		holding['purchasers'] = purchasers
		top['applicantincome'].append(holding)
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
		purchasers = set_purchasers()
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
		purchasers = set_purchasers()
		holding['purchasers'] = purchasers
		top['incomelevel'].append(holding)
	censuscharacteristics.append(top)

	#build totals
	top = OrderedDict({})
	holding = OrderedDict({})
	purchasers = set_purchasers()
	totals['purchasers'] = purchasers

	container['borrowercharacteristics'] = borrowercharacteristics
	container['censuscharacteristics'] = censuscharacteristics
	container['total'] = totals
	#write_JSON('JSON_out.json')
	print json.dumps(container, indent=4)
	return container


	#def build_JSON(self, inputs, MSA):

bloop = build_JSON()
#print set_purchasers()
#print bloop
#print json.dumps(bloop, indent =4)
