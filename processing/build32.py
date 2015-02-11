from collections import OrderedDict
class AD_report(object):
	pass

class build_JSON(AD_report):

	def __init__(self):
		self.container = OrderedDict({})
		self.msa = OrderedDict({})
		self.borrowercharacteristics = []
		self.censuscharacteristics = [] #censuscharacteristics holds all the lists and dicts for the census portion of the table
		#self.table32_cats = ['No reported pricing data', 'pricing data reported', 'percentage points above average prime offer rate: only includes loans with APR above the threshold', 'mean', 'median', 'HOEPA Loans']
		self.table32_categories = ['pricinginformation', 'points', 'hoepa']
		self.table32_rates = ['1.50 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.49', '3.50 - 4.49', '4.50 - 5.49', '5.50 - 6.49', '6.5 or more', 'mean', 'median']
		self.purchaser_names = ['Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
		self.race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Pacific Islander', 'White', '2 or more minority races', 'Joint', 'Not Provided', 'Not Applicable', 'No co-applicant']
		self.ethnicity_names = ['Hispanic or Latino', 'Not Hispanic or Latino', 'Not provided', 'Not applicable', 'No co-applicant']
		self.minority_statuses = ['White Non-Hispanic', 'Others, Including Hispanic']
		self.applicant_income_bracket = ['Less than 50% of MSA/MD median', '50-79% of MSA/MD median', '80-99% of MSA/MD median', '100-119% of MSA/MD median', '120% or more of MSA/MD median', 'income not available']
		self.tract_pct_minority = ['Less than 10% minority', '10-19% minority', '20-49% minority', '50-79% minority', '80-100% minority']
		self.tract_income = ['Low income', 'Moderate income', 'Middle income', 'Upper income']
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
		for item in self.purchaser_names:
			purchasersholding = OrderedDict({})
			purchasersholding['name'] = "{}".format(item)
			purchasersholding['count'] = 0
			purchasersholding['value'] = 0
			purchasers.append(purchasersholding)
		return purchasers

	def set_purchasers32(self):
		from collections import OrderedDict
		purchasers = []
		for item in self.purchaser_names:
			purchasersholding = OrderedDict({})
			purchasersholding['name'] = "{}".format(item)
			purchasersholding['first lien count'] = 0
			purchasersholding['first lien value'] = 0
			purchasersholding['junior lien count'] = 0
			purchasersholding['junior lien value'] = 0
			purchasers.append(purchasersholding)
		return purchasers

	def set_purchasers32v2(self): #this function is used for the 'mean' and 'median' sections as they do not have loan value sections
		from collections import OrderedDict
		purchasers = []
		for item in self.purchaser_names:
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
		for rate in self.table32_rates:
			 holding = OrderedDict({})
			 holding['point'] = "{}".format(rate)
			 if self.table32_rates.index(rate) < 8:
				holding['purchasers'] = self.set_purchasers32()
			 else:
				holding['purchasers'] = self.set_purchasers32v2()
			 spreads.append(holding)
		return spreads

	def table_31_borrower_characteristics(self, characteristic, container_name, item_list):
		#container_name = characteristic.lower()+'s'
		#borrowercharacteristics = []
		Header = True
		top = OrderedDict({})
		for item in item_list:
			holding = OrderedDict({})
			if Header == True:
				top['characteristic'] = characteristic
				top[container_name] = []
			Header = False
			holding[characteristic.lower()] = "{}".format(item)
			holding['purchasers'] = self.set_purchasers()
			top[container_name].append(holding)
		self.borrowercharacteristics.append(top)

	def table_31_census_characteristics(self, characteristic, container_name, item_list):
		Header = True
		top = OrderedDict({})
		for item in item_list:
			holding = OrderedDict({})
			if Header == True:
				top['characteristic'] = characteristic
				top[container_name] = []
			Header = False
			holding[characteristic.lower()] = "{}".format(item)
			holding['purchasers'] = self.set_purchasers()
			top[container_name].append(holding)
		self.censuscharacteristics.append(top)

	def json_controller(self):
		self.table_31_borrower_characteristics('Race', 'races', self.race_names)
		self.table_31_borrower_characteristics('Ethnicity', 'ethnicities', self.ethnicity_names)
		self.table_31_borrower_characteristics('Minority Status', 'minoritystatuses', self.minority_statuses)
		self.table_31_borrower_characteristics('Applicant Income', 'applicantincomes', self.applicant_income_bracket)
		self.table_31_census_characteristics('Racial/Ethnic Composition', 'tractpctminority', self.tract_pct_minority)
		self.table_31_census_characteristics('Income', 'incomelevel', self.tract_income)
		self.container['borrowercharacteristics'] = self.borrowercharacteristics
		self.container['censuscharacteristics'] = self.censuscharacteristics
		totals = {} #totals sums all the loan counts and values for each purchaser
		top = OrderedDict({})
		holding = OrderedDict({})
		totals['purchasers'] = self.set_purchasers()
		self.container['total'] = totals

	def print_JSON(self):
		import json
		print json.dumps(self.container, indent=4)

	def write_JSON(self, name, data):
		#writes the JSON structure to a file
		import json
		with open(name, 'w') as outfile:
		 json.dump(data, outfile, indent = 4, ensure_ascii=False)


build = build_JSON()
#build32.build_JSON32()
#build32.print_JSON()
#build32.write_JSON('superderper.json', build32.container)
#def test_json(self, characteristic, container_name, item_list):
build.json_controller()
build.write_JSON('superderper31.json', build.container)





