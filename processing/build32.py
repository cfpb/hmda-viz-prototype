from collections import OrderedDict

class AD_report(object):
	pass

class build_JSON(AD_report):

	def __init__(self):
		self.container = OrderedDict({})
		self.msa = OrderedDict({})
		#self.table32_cats = ['No reported pricing data', 'pricing data reported', 'percentage points above average prime offer rate: only includes loans with APR above the threshold', 'mean', 'median', 'HOEPA Loans']
		self.table32_cats = ['pricing-information', 'points', 'mean', 'median', 'hoepa']
		self.table32_rates = ['1.50 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.49', '3.50 - 4.49', '4.50 - 5.49', '5.50 - 6.49', '6.5 or more']

	def table_headers(self, table_num): #holds table descriptions
		if table_num == '3-1':
			return 'Loans sold. By characteristics of borrower and census tract in which property is located and by type of purchaser (includes originations and purchased loans).'
		elif table_num =='3-2':
			return 'Pricing Information for First and Junio Lien Loans Sold by Type of Purchaser (includes originations only).'

	def set_header32(self, inputs, MSA, desc, table_type, table_num): #add a variable for desc_string
		msa = OrderedDict({})
		self.container['table'] = table_num
		self.container['type'] = table_type
		self.container['desc'] = desc
		self.container['year'] = inputs['year']
		self.msa['id'] = MSA
		#self.msa['name'] = inputs['MSA name'] #need to add MSA names to a database or read-in file
		self.msa['state'] = inputs['state name']
		self.container['msa'] = self.msa
		return self.container

	def set_purchasers(self):
		from collections import OrderedDict
		purchasers = []
		purchaser_names = ['Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
		for item in purchaser_names:
			purchasersholding = OrderedDict({})
			purchasersholding['name'] = "{}".format(item)
			purchasersholding['count'] = 0
			purchasersholding['value'] = 0
			purchasers.append(purchasersholding)
		return purchasers

	def set_purchasers32(self):
		from collections import OrderedDict
		purchasers = []
		purchaser_names = ['Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
		for item in purchaser_names:
			purchasersholding = OrderedDict({})
			purchasersholding['name'] = "{}".format(item)
			purchasersholding['first lien count'] = 0
			purchasersholding['first lien value'] = 0
			purchasersholding['junior lien count'] = 0
			purchasersholding['junior lien value'] = 0
			purchasers.append(purchasersholding)
		return purchasers

	def set_purchasers32v2(self):
		from collections import OrderedDict
		purchasers = []
		purchaser_names = ['Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
		for item in purchaser_names:
			purchasersholding = OrderedDict({})
			purchasersholding['name'] = "{}".format(item)
			purchasersholding['first lien'] = 0
			purchasersholding['junior lien'] = 0
			purchasers.append(purchasersholding)
		return purchasers
	def build_JSON32(self):
		pricinginformation = []
		categories = ['No reported pricing data', 'reported pricing data']
		for cat in categories:
			holding = OrderedDict({})
			holding['pricing']= "{}".format(cat) #race is overwritten each pass of the loop (keys are unique in dictionaries)
			holding['purchasers']  = self.set_purchasers32() #purchasers is overwritten each pass in the holding dictionary
			pricinginformation.append(holding)
		self.container['pricinginformation'] = pricinginformation



		holding = OrderedDict({})
		points = self.build_rate_spreads()
		self.container['points'] = points

		hoepa = OrderedDict({})
		hoepa['pricing'] = 'hoepa loans'
		hoepa['purchasers'] = self.set_purchasers32()
		self.container['hoepa'] = hoepa
		return self.container

	def build_rate_spreads(self):
		spreads = []
		rate_spreads = ['1.50 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.49', '3.50 - 4.49', '4.50 - 5.49', '5.50 - 6.49', '6.5 or more', 'mean', 'median']
		for rate in rate_spreads: #change to self.table32_rates
			 holding = OrderedDict({})
			 holding['point'] = "{}".format(rate)
			 if rate_spreads.index(rate) < 8:
			 	holding['purchasers'] = self.set_purchasers32()
			 else:
			 	holding['purchasers'] = self.set_purchasers32v2()
			 spreads.append(holding)
		return spreads

	def build_JSON31(self):
		from collections import OrderedDict
		import json
	def build_JSON(self):
		from collections import OrderedDict
		import json
		#rewrite this as a function
		#FFIEC report 3-1 labels
		#move these lists to a self. area or use a function area to return lists
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
			#purchasers = self.set_purchasers()
			holding['purchasers'] = self.set_purchasers() #purchasers is overwritten each pass in the holding dictionary
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
			#purchasers = self.set_purchasers()
			holding['purchasers'] = self.set_purchasers()
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
			holding['purchasers'] = self.set_purchasers()
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
			#purchasers = self.set_purchasers()
			holding['purchasers'] = self.set_purchasers()
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
			#purchasers = self.set_purchasers()
			holding['purchasers'] = self.set_purchasers()
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
			#purchasers = self.set_purchasers()
			holding['purchasers'] = self.set_purchasers()
			top['incomelevel'].append(holding)
		censuscharacteristics.append(top)

		#build totals
		top = OrderedDict({})
		holding = OrderedDict({})
		#purchasers = self.set_purchasers()
		totals['purchasers'] = self.set_purchasers()

		self.container['borrowercharacteristics'] = borrowercharacteristics
		self.container['censuscharacteristics'] = censuscharacteristics
		self.container['total'] = totals
		#self.write_JSON('JSON_out.json')
		return self.container

	def print_JSON(self):
		import json
		print json.dumps(self.container, indent=4)

	def write_JSON(self, name):
		#writes the JSON structure to a file
		import json
		with open(name, 'w') as outfile:
		 json.dump(self.container, outfile, indent = 4, ensure_ascii=False)

inputs = {}
build32 = build_JSON()
build32.build_JSON32()
#build32.print_JSON()
build32.write_JSON('superderper.json')
inputs['rate spread index'] = 1
inputs['purchaser'] =0

#print build32.container['points'][1]['purchasers'][0]