from collections import OrderedDict

class AD_report(object):
	pass
class build_JSON(AD_report):

	def __init__(self):
		self.container = OrderedDict({}) #master container for the JSON structure
		self.msa = OrderedDict({}) #stores header information for the MSA
		self.borrowercharacteristics = [] #holds all the borrower lists and dicts for the borrower portion of table 3-1
		self.censuscharacteristics = [] #censuscharacteristics holds all the lists and dicts for the census portion of the table 3-1
		self.table32_categories = ['pricinginformation', 'points', 'hoepa']
		self.table32_rates = ['1.50 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.49', '3.50 - 4.49', '4.50 - 5.49', '5.50 - 6.49', '6.5 or more', 'mean', 'median']
		self.purchaser_names = ['Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
		self.race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Other Pacific Islander', 'White', '2 or more minority races', 'Joint (White/Minority Race', 'Not Available']
		self.ethnicity_names = ['Hispanic or Latino', 'Not Hispanic or Latino', 'Joint (Hispanic or Latino/Not Hispanic or Latino', 'Ethnicity Not Available']
		self.minority_statuses = ['White Non-Hispanic', 'Others, Including Hispanic']
		self.applicant_income_bracket = ['Less than 50% of MSA/MD median', '50-79% of MSA/MD median', '80-99% of MSA/MD median', '100-119% of MSA/MD median', '120% or more of MSA/MD median', 'income not available']
		self.tract_pct_minority = ['Less than 10% minority', '10-19% minority', '20-49% minority', '50-79% minority', '80-100% minority']
		self.tract_income = ['Low income', 'Moderate income', 'Middle income', 'Upper income']
		self.state_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE':'Delaware',
			'FL':'Florida', 'GA':'Georgia', 'HI':'Hawaii', 'ID':'Idaho', 'IL':'Illinois', 'IN':'Indiana', 'IA':'Iowa', 'KS':'Kansas', 'KY': 'Kentucky', 'LA':'Louisiana', 'ME': 'Maine', 'MD':'Maryland',
			'MA':'Massachusetts', 'MI':'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE':'Nebraska', 'NV':'Nevada', 'NH':'New Hampshire', 'NJ':'New Jersey', 'NM':'New Mexico',
			'NY':'New York', 'NC':'North Carolina', 'ND':'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR':'Oregon','PA':'Pennsylvania', 'RI':'Rhode Island', 'SC':'South Carolina',
			'SD':'South Dakota', 'TN':'Tennessee', 'TX':'Texas', 'UT':'Utah', 'VT':'Vermont', 'VA':'Virginia', 'WA': 'Washington', 'WV':'West Virginia', 'WI':'Wisconsin', 'WY':'Wyoming', 'PR':'Puerto Rico', 'VI':'Virgin Islands'}
		self.msa_names = {} #holds the msa names for use in directory paths when writing JSON objects
		self.state_msa_list = {} #holds a dictionary of msas in state by id number and name

	def msas_in_state(self, cursor, selector):
		#this function builds a list of MSA numbers and names in each state
		#set sql query text to pull MSA names for each MSA number
		SQL = '''SELECT DISTINCT name, geoid_msa
			FROM tract_to_cbsa_2010
			WHERE geoid_msa != '     ' and state = %s;'''

		state_list = ['WA', 'WI', 'WV', 'FL', 'WY', 'NH', 'NJ', 'NM', 'NC', 'ND', 'NE', 'NY', 'RI', 'NV', 'CO', 'CA', 'GA', 'CT', 'OK', 'OH', 'KS', 'SC', 'KY', 'OR', 'SD', 'DE', 'HI', 'PR', 'TX', 'LA', 'TN', 'PA', 'VA', 'VI', 'AK', 'AL', 'AR', 'VT', 'IL', 'IN', 'IA', 'AZ', 'ID', 'ME', 'MD', 'MA', 'UT', 'MO', 'MN', 'MI', 'MT', 'MS']
		state_msas = {}
		for state in state_list:
			location = (state,) #convert state to tuple for psycopg2
			cursor.execute(SQL, location) #execute SQL statement against server
			msas = [] #holding list for MSA id and names for entire state
			for row in cursor.fetchall():
				temp = {} #holding dict for single MSA id and name
				cut_point =str(row['name'])[::-1].find(' ')+1 #find index to remove state abbreviations
				temp['id'] = row['geoid_msa'] #set MSA number to id in dict
				temp['name'] = str(row['name'])[:-cut_point].replace(' ', '-').upper()
				msas.append(temp)

			state_msas['msa-mds'] = msas
			name = 'msa-mds.json'
			#this year path uses the year from the input file
			path = 'json'+"/"+'aggregate'+"/"+selector.report_list['year'][1]+"/"+self.state_names[state].lower()
			print path #change this to a log file write
			if not os.path.exists(path): #check if path exists
				os.makedirs(path) #if path not present, create it
			self.write_JSON(name, state_msas, path)
			self.jekyll_for_state(path) #create and write jekyll file to state path

	def jekyll_for_msa(self, path):
		#creates and writes a jekyll file for use in serving the front end
		file_text = '---\nlayout: tables\n---'

		with open(os.path.join(path, 'index.md'), 'w') as f:
			f.write(file_text)

	def jekyll_for_state(self, path):
		#creates and writes a jekyll file for use in serving the front end
		file_text = '---\nlayout: msas\n---'

		with open(os.path.join(path, 'index.md'), 'w') as f:
			f.write(file_text)

	def jekyll_for_report(self, path):
		#creates and writes a jekyll file for use in serving the front end
		file_text = '---\nlayout: aggregate/table\n---'

		with open(os.path.join(path, 'index.md'), 'w') as f:
			f.write(file_text)

	def set_msa_names(self, cursor):
		#this function sets the MSA names for MSA numbers
		#MSA names are stored with state abbreviations appended at the end, these must be removed
		#set SQL text for query
		SQL = '''SELECT DISTINCT name, geoid_msa, geoid_metdiv
			FROM tract_to_cbsa_2010'''
		cursor.execute(SQL,) #execute query against server
		for row in cursor.fetchall():
			cut_point =str(row['name'])[::-1].find(' ')+1 #find the point where the state abbreviations begin
			self.msa_names[row['geoid_msa']] = str(row['name'])[:-cut_point].replace(' ', '-')

	def get_state_name(self, abbrev):
		#this is a dictionary function that returns a state name when given the abbreviation
		state_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE':'Delaware',
				'FL':'Florida', 'GA':'Georgia', 'HI':'Hawaii', 'ID':'Idaho', 'IL':'Illinois', 'IN':'Indiana', 'IA':'Iowa', 'KS':'Kansas', 'KY': 'Kentucky', 'LA':'Louisiana', 'ME': 'Maine', 'MD':'Maryland',
				'MA':'Massachusetts', 'MI':'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE':'Nebraska', 'NV':'Nevada', 'NH':'New Hampshire', 'NJ':'New Jersey', 'NM':'New Mexico',
				'NY':'New York', 'NC':'North Carolina', 'ND':'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR':'Oregon','PA':'Pennsylvania', 'RI':'Rhode Island', 'SC':'South Carolina',
				'SD':'South Dakota', 'TN':'Tensessee', 'TX':'Texas', 'UT':'Utah', 'VT':'Vermont', 'VA':'Virginia', 'WA': 'Washington', 'WV':'West Virginia', 'WI':'Wisconsin', 'WY':'Wyoming', 'PR':'Puerto Rico', 'VI':'Virgin Islands'}
		return state_names[abbrev]

	def table_headers(self, table_num): #holds table descriptions
		if table_num == '3-1':
			return 'Loans sold, by characteristics of borrower and census tract in which property is located and by type of purchaser (includes originations and purchased loans),'
		elif table_num =='3-2':
			return 'Pricing Information for First and Junior Lien Loans Sold by Type of Purchaser (includes originations only).'

	def set_header(self, inputs, MSA, desc, table_type, table_num): #sets the header information of the JSON object
		msa = OrderedDict({})
		self.container['table'] = table_num
		self.container['type'] = table_type
		self.container['desc'] = desc
		self.container['year'] = inputs['year']
		self.msa['id'] = MSA
		self.msa['name'] = self.msa_names[MSA] #need to add MSA names to a database or read-in file
		self.msa['state'] = inputs['state name']
		self.msa['state_name'] = self.state_names[self.msa['state']]
		self.container['msa'] = self.msa
		return self.container
	def set_gender(self, end_point):
		genders = ['male', 'female', 'joint (male/female']
		for item in genders:
			end_point[item] = 0

	def table_41_builder(self):
		disposition_status = []
		categories = []
		for race in self.race_names:
			holding = OrderedDict({})
			holding['race']= "{}".format(race) #race is overwritten each pass of the loop (keys are unique in dictionaries)

			#holding['race']
			#holding['purchasers']  = self.set_purchasers(['first lien count', 'first lien value', 'junior lien count', 'junior lien value']) #purchasers is overwritten each pass in the holding dictionary
			disposition_status.append(race)
		self.container['races'] = disposition_status

		top = OrderedDict({})
		for item in self.race_names:
			holding = OrderedDict({})
			top['races'] = []
			holding[container[container_name]] = "{}".format(item)
			holding['purchasers'] = self.set_purchasers(['count', 'value'])
			top[container_name].append(holding)
		self.borrowercharacteristics.append(top)
		return self.container

	def set_purchasers(self, holding_list): #this function sets the purchasers section of report 3-2
		purchasers = []
		for item in self.purchaser_names:
			purchasersholding = OrderedDict({})
			purchasersholding['name'] = "{}".format(item)
			for item in holding_list: #pass in the appropriate holding list for each set_purchasers call
				purchasersholding[item] = 0
			purchasers.append(purchasersholding)
		return purchasers

	def build_rate_spreads(self): #builds the rate spreads section of the report 3-2 JSON
		spreads = []
		for rate in self.table32_rates:
			 holding = OrderedDict({})
			 holding['point'] = "{}".format(rate)
			 if self.table32_rates.index(rate) < 8:
				holding['purchasers'] = self.set_purchasers(['first lien count', 'first lien value', 'junior lien count', 'junior lien value'])
			 else:
				holding['purchasers'] = self.set_purchasers(['first lien', 'junior lien'])
			 spreads.append(holding)
		return spreads

	def table_31_borrower_characteristics(self, characteristic, container_name, item_list): #builds the borrower characteristics section of the report 3-1 JSON
		container = {'ethnicities':'ethnicity', 'minoritystatuses':'minoritystatus', 'races':'race', 'applicantincomes':'applicantincome'}
		Header = True
		top = OrderedDict({})
		for item in item_list:
			holding = OrderedDict({})
			if Header == True:
				top['characteristic'] = characteristic
				top[container_name] = []
			Header = False
			holding[container[container_name]] = "{}".format(item)
			holding['purchasers'] = self.set_purchasers(['count', 'value'])
			top[container_name].append(holding)
		self.borrowercharacteristics.append(top)

	def table_31_census_characteristics(self, characteristic, container_name, item_list): #builds the census characteristics section of the report 3-1 JSON
		container = {'incomelevels':'incomelevel', 'tractpctminorities':'tractpctminority'}
		Header = True
		top = OrderedDict({})
		for item in item_list:
			holding = OrderedDict({})
			if Header == True:
				top['characteristic'] = characteristic
				top[container_name] = []
			Header = False
			holding[container[container_name]] = "{}".format(item)
			holding['purchasers'] = self.set_purchasers(['count', 'value'])
			top[container_name].append(holding)
		self.censuscharacteristics.append(top)

	def table_32_builder(self): #builds the JSON structure for report 3-2
		pricinginformation = []
		categories = ['No reported pricing data', 'reported pricing data']
		for cat in categories:
			holding = OrderedDict({})
			holding['pricing']= "{}".format(cat)
			holding['purchasers']  = self.set_purchasers(['first lien count', 'first lien value', 'junior lien count', 'junior lien value']) #purchasers is overwritten each pass in the holding dictionary
			pricinginformation.append(holding)
		self.container['pricinginformation'] = pricinginformation
		holding = OrderedDict({})
		points = self.build_rate_spreads()
		self.container['points'] = points
		hoepa = OrderedDict({})
		hoepa['pricing'] = 'hoepa loans'
		hoepa['purchasers'] = self.set_purchasers(['first lien count', 'first lien value', 'junior lien count', 'junior lien value'])
		self.container['hoepa'] = hoepa
		return self.container

	def table_31_builder(self): #assembles all components of the 3-1 JSON object, appends totals section
		self.table_31_borrower_characteristics('Race', 'races', self.race_names)
		self.table_31_borrower_characteristics('Ethnicity', 'ethnicities', self.ethnicity_names)
		self.table_31_borrower_characteristics('Minority Status', 'minoritystatuses', self.minority_statuses)
		self.table_31_borrower_characteristics('Applicant Income', 'applicantincomes', self.applicant_income_bracket)
		self.table_31_census_characteristics('Racial/Ethnic Composition', 'tractpctminorities', self.tract_pct_minority)
		self.table_31_census_characteristics('Income', 'incomelevels', self.tract_income)
		self.container['borrowercharacteristics'] = self.borrowercharacteristics
		self.container['censuscharacteristics'] = self.censuscharacteristics
		totals = {} #totals sums all the loan counts and values for each purchaser
		top = OrderedDict({})
		holding = OrderedDict({})
		totals['purchasers'] = self.set_purchasers(['count', 'value'])
		self.container['total'] = totals
		return self.container

	def print_JSON(self): #prints a json object to the terminal
		import json
		print json.dumps(self.container, indent=4)

	def write_JSON(self, name, data, path): #writes a json object to file
		with open(os.path.join(path, name), 'w') as outfile: #writes the JSON structure to a file for the path named by report's header structure
			json.dump(data, outfile, indent=4, ensure_ascii = False)


build4 =  build_JSON()

table41 = build4.table_41_builder()
build4.print_JSON()