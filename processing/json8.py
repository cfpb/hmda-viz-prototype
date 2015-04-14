#this file holds the classes used to create the A&D reports using the HMDA LAR files combined with Census demographic information
import datetime as foo
import numpy
import weighted
import psycopg2
import psycopg2.extras
from collections import OrderedDict
import json
import os
import csv
class AD_report(object): #parent class for A&D report library
	pass

class build_JSON(AD_report):

	def __init__(self):
		self.container = OrderedDict({}) #master container for the JSON structure
		self.msa = OrderedDict({}) #stores header information for the MSA
		self.borrowercharacteristics = [] #holds all the borrower lists and dicts for the borrower portion of table 3-1
		self.censuscharacteristics = [] #censuscharacteristics holds all the lists and dicts for the census portion of the table 3-1
		self.table32_categories = ['pricinginformation', 'points', 'hoepa']
		self.table32_rates = ['1.50 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.49', '3.50 - 4.49', '4.50 - 5.49', '5.50 - 6.49', '6.5 or more', 'Mean', 'Median']
		self.purchaser_names = ['Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
		self.race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Other Pacific Islander', 'White', '2 or more minority races', 'Joint (White/Minority Race)', 'Race Not Available']
		self.ethnicity_names = ['Hispanic or Latino', 'Not Hispanic or Latino', 'Joint (Hispanic or Latino/Not Hispanic or Latino)', 'Ethnicity Not Available']
		self.minority_statuses = ['White Non-Hispanic', 'Others, Including Hispanic']
		self.applicant_income_bracket = ['Less than 50% of MSA/MD median', '50-79% of MSA/MD median', '80-99% of MSA/MD median', '100-119% of MSA/MD median', '120% or more of MSA/MD median', 'Income Not Available']
		self.tract_pct_minority = ['Less than 10% minority', '10-19% minority', '20-49% minority', '50-79% minority', '80-100% minority']
		self.tract_income = ['Low income', 'Moderate income', 'Middle income', 'Upper income']
		self.state_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE':'Delaware', 'DC':'District of Columbia',
			'FL':'Florida', 'GA':'Georgia', 'HI':'Hawaii', 'ID':'Idaho', 'IL':'Illinois', 'IN':'Indiana', 'IA':'Iowa', 'KS':'Kansas', 'KY': 'Kentucky', 'LA':'Louisiana', 'ME': 'Maine', 'MD':'Maryland',
			'MA':'Massachusetts', 'MI':'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE':'Nebraska', 'NV':'Nevada', 'NH':'New Hampshire', 'NJ':'New Jersey', 'NM':'New Mexico',
			'NY':'New York', 'NC':'North Carolina', 'ND':'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR':'Oregon','PA':'Pennsylvania', 'RI':'Rhode Island', 'SC':'South Carolina',
			'SD':'South Dakota', 'TN':'Tennessee', 'TX':'Texas', 'UT':'Utah', 'VT':'Vermont', 'VA':'Virginia', 'WA': 'Washington', 'WV':'West Virginia', 'WI':'Wisconsin', 'WY':'Wyoming', 'PR':'Puerto Rico', 'VI':'Virgin Islands'}
		self.state_codes = {'WA':'53', 'WI':'55', 'WV':'54', 'FL':'12', 'WY':'56', 'NH':'33', 'NJ':'34', 'NM':'33', 'NC':'37', 'ND':'38', 'NE':'31', 'NY':'36', 'RI':'44', 'NV':'32', 'CO':'08', 'CA':'06', 'GA':'13', 'CT':'09', 'OK':'40', 'OH':'39',
					'KS':'20', 'SC':'45', 'KY':'21', 'OR':'41', 'SD':'46', 'DE':'10', 'HI':'15', 'PR':'43', 'TX':'48', 'LA':'22', 'TN':'47', 'PA':'42', 'VA':'51', 'VI':'78', 'AK':'02', 'AL':'01', 'AR':'05', 'VT':'50', 'IL':'17', 'IN':'18',
					'IA':'19', 'AZ':'04', 'ID':'16', 'ME':'23', 'MD':'24', 'MA':'25', 'UT':'49', 'MO':'29', 'MN':'27', 'MI':'26', 'MT':'30', 'MS':'29', 'DC':'11'}
		self.msa_names = {} #holds the msa names for use in directory paths when writing JSON objects
		self.state_msa_list = {} #holds a dictionary of msas in state by id number and name
		self.dispositions_list = ['Applications Received', 'Loans Originated', 'Apps. Approved But Not Accepted', 'Applications Denied', 'Applications Withdrawn', 'Files Closed For Incompleteness']
		self.gender_list = ['Male', 'Female', 'Joint (Male/Female)']
		self.gender_list2 = ['Male', 'Female', 'Joint (Male/Female)', 'Gender Not Available']
		self.end_points = ['count', 'value']
		self.denial_reasons = ['Debt-to-Income Ratio', 'Employment History', 'Credit History', 'Collateral', 'Insufficient Cash', 'Unverifiable Information', 'Credit App. Incomplete', 'Mortgage Insurance Denied', 'Other', 'Total']
	def msas_in_state(self, cursor, selector, report_type):
		#this function builds a list of MSA numbers and names in each state
		#set sql query text to pull MSA names for each MSA number
		SQL = '''SELECT DISTINCT name, geoid_msa
			FROM tract_to_cbsa_2010
			WHERE geoid_msa != '     ' and state = %s;'''

		SQL2 = '''SELECT DISTINCT name, geoid_metdiv
			FROM tract_to_cbsa_2010
			WHERE geoid_metdiv != '          ' and state = %s;'''
		#state_list = ['WA', 'WI', 'WV', 'FL', 'WY', 'NH', 'NJ', 'NM', 'NC', 'ND', 'NE', 'NY', 'RI', 'NV', 'CO', 'CA', 'GA', 'CT', 'OK', 'OH', 'KS', 'SC', 'KY', 'OR', 'SD', 'DE', 'HI', 'PR', 'TX', 'LA', 'TN', 'PA', 'VA', 'VI', 'AK', 'AL', 'AR', 'VT', 'IL', 'IN', 'IA', 'AZ', 'ID', 'ME', 'MD', 'MA', 'UT', 'MO', 'MN', 'MI', 'MT', 'MS']

		for state, code in self.state_codes.iteritems():

			state_msas = {}
			state_holding = {}
			location = (code,) #convert state to tuple for psycopg2
			cursor.execute(SQL, location) #execute SQL statement against server
			msas = [] #holding list for MSA id and names for entire state
			for row in cursor.fetchall(): #get all MSA numbers and names for the state
				temp = {} #holding dict for single MSA id and name
				cut_point =str(row['name'])[::-1].find(' ')+2 #find index to remove state abbreviations
				temp['id'] = row['geoid_msa'] #set MSA number to id in dict
				temp['name'] = str(row['name'])[:-cut_point].replace(' ', '-').upper()
				state_holding[row['geoid_msa']] = str(row['name'])[:-cut_point].replace(' ', '-').lower()
				self.msa_names[row['geoid_msa']] = str(row['name'])[:-cut_point].replace(' ', '-').lower()
				msas.append(temp)

			cursor.execute(SQL2, location)
			for row2 in cursor.fetchall(): #get all MD numbers and names for the state
				temp = {}
				cut_point = str(row2['name'])[::-1].find(' ')+2 #find last space before state names
				temp['id'] = row2['geoid_metdiv'][5:] #take only last 5 digits from metdiv number
				temp['name'] = str(row2['name'])[:-cut_point].replace(' ', '-').upper() #remove state abbrevs
				state_holding[row2['geoid_metdiv'][5:]] = str(row2['name'])[:-cut_point].replace(' ', '-').lower()
				self.msa_names[row2['geoid_metdiv'][5:]] = str(row2['name'])[:-cut_point].replace(' ', '-').lower()
				msas.append(temp) #add one metdiv name to the list of names

			self.state_msa_list[state] = state_holding
			state_msas['msa-mds'] = msas
			name = 'msa-mds-all.json'
			#this year path uses the year from the input file

			path = '../'+report_type+"/"+selector.report_list['year'][1]+"/"+self.state_names[state].replace(' ', '-').lower()
			print path #change this to a log file write
			if not os.path.exists(path): #check if path exists
				os.makedirs(path) #if path not present, create it
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
			cut_point =str(row['name'])[::-1].find(' ') +2#find the point where the state abbreviations begin
			self.msa_names[row['geoid_msa']] = str(row['name'])[:-cut_point].replace(' ', '-').replace('--','-')
			geoid_metdiv = str(row['geoid_metdiv'])[5:] #take the last 5 digits of the geoid number, this is what the FFIEC uses as an MSA number for MDs
			self.msa_names[geoid_metdiv] = str(row['name'])[:-cut_point].replace(' ', '_').replace('--','-')

	def get_state_name(self, abbrev):
		#this is a dictionary function that returns a state name when given the abbreviation
		return self.state_names[abbrev]

	def table_headers(self, table_num): #holds table descriptions
		if table_num == '3-1':
			return 'Loans sold, by characteristics of borrower and census tract in which property is located and by type of purchaser (includes originations and purchased loans)'
		elif table_num == '3-2':
			return 'Pricing Information for First and Junior Lien Loans Sold by Type of Purchaser (includes originations only)'
		elif table_num == '4-1':
			return 'Disposition of applications for FHA, FSA/RHS, and VA home-purchase loans, 1- to 4- family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-2':
			return 'Disposition of applications for conventional home-purchase loans 1- to 4- family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-3':
			return 'Disposition of applications to refinace loans on 1- to 4- family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-4':
			return 'Disposition of applications for home improvement loans, 1- to 4- family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-5':
			return 'Disposition of applications for loans on dwellings for 5 or more families, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-6':
			return 'Disposition of applications from nonoccupants for home-purchase, home improvement, or refinancing loans, 1- to 4- family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-7':
			return 'Disposition of applications for home-purchase, home improvement, or refinancing loans, manufactured home dwellings by race, ethnicity, gender and income of applicant'
		elif table_num == '5-1':
			return 'Disposition of applications for FHA, FSA/RHS, and VA home-purchase loans, 1- to 4-family and manufactured home dwellings, by income, race and ethnicity of applicant'
		elif table_num == '5-2':
			return 'Disposition of applications for conventional home-purchase loans, 1- to 4-family and manufactured home dwellings, by income race, and ethnicity of applicant'
		elif table_num == '5-3':
			return 'Disposition of applications to refinance loans on 1- to 4-family and manufactured home dwellings, by income, race and ethnicity of applicant'
		elif table_num == '5-4':
			return 'Disposition of applications for home improvement loans, 1- to 4-family and manufactured home dwellings, by income, race and ethnicity of applicant'
		elif table_num == '5-6':
			return 'Disposition of applications from nonoccupants for home-purchase, home improvement, or refinancing loans, 1- to 4-family and manufactured home dwellings, by income, race and ethnicity of applicant'
		elif table_num == '5-7':
			return 'Disposition of applications for home-purchase, home improvement, or refinancing loans, manufactured home dwellings, by income, race and ethnicity of applicant'
		elif table_num =='7-1':
			return 'Disposition of applications for FHA, FSA/RHS, and VA home-purchase loans, 1- to 4-family and manufactured home dwellings, by characteristics of census tract in which property is located'
		elif table_num =='7-2':
			return 'Disposition of applications for conventional home-purchase loans, 1- to 4-family and manufactured home dwellings, by characteristics of census tract in which property is located'
		elif table_num =='7-3':
			return 'Disposition of applications to refinance loans on 1- to 4-family and manufactured home dwellings, by characteristics of census tract in which property is located'
		elif table_num =='7-4':
			return 'Disposition of applications for home improvement loans, 1- to 4-family and manufactured home dwellings, by characteristics of census tract in which property is located'
		elif table_num =='7-5':
			return 'Disposition of applications for loans on dwellings for 5 or more families, by characteristics of census tract in which property is located'
		elif table_num =='7-6':
			return 'Disposition of applications from nonoccupatns for home-purchase, home improvement, or refinancing loans, 1- to 4-family and manufactured home dwellings, by characteristics of census tract in which property is located'
		elif table_num =='7-7':
			return 'Disposition of applications for home-purchase, home improvement, or refinancing loans, manufactured home dwellings, by characteristics of census tract in which property is located'
		elif table_num =='8-1':
			return 'Reasons for denial of applications for FHA, FSA/RHS, and VA home-purchase loans, 1- to 4-family and manufacutred home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num =='8-2':
			return 'Reasons for denial of applications for conventional home-purchase loans, 1- to 4-family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num =='8-3':
			return 'Reasons for denial of applications to refinance loans on 1- to 4-family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num =='8-4':
			return 'Reasons for denial of applications for home improvement loans, 1- to 4-family and manufactured home dwellings, by race, ethinicity, gender and income of applicant'
		elif table_num =='8-6':
			return 'Reasons for denial of applications from nonoccupants for home-purchase, home improvement, or refinancing loans, 1- to 4- family and manufactured home dwellings, by race, ehtnicity, gender and income of applicant'
		elif table_num =='8-7':
			return 'Reasons for denial of applications for home-purchase, home improvement, or refinancing loans, manufactured home dwellings, by race, ethinicity, gender and income of applicant'
		elif table_num == '9':
			return 'Disposition of loan applications, by median age of homes in census tract in which property is located and type of loan'

	def set_header(self, inputs, MSA, table_type, table_num): #sets the header information of the JSON object
		now = foo.datetime.now()
		d = now.day
		m = now.month
		y = now.year
		msa = OrderedDict({})
		self.container['table'] = table_num
		self.container['type'] = table_type
		self.container['desc'] = self.table_headers(table_num)
		self.container['year'] = inputs['year']
		self.container['report-date'] = "{:0>2d}".format(m)+'/'+"{:0>2d}".format(d)+'/'+"{:0>4d}".format(y)
		self.msa['id'] = MSA
		self.msa['name'] = self.msa_names[MSA]
		self.msa['state'] = inputs['state name'] #this is the two digit abbreviation
		self.msa['state_name'] = self.state_names[self.msa['state']]
		self.container['msa'] = self.msa
		return self.container

	def table_7x_builder(self):
		self.container['censuscharacteristics'] = []
		holding = OrderedDict({})
		holding['characteristic'] = 'Racial/Ethnic Composition'
		holding['compositions'] = self.set_list(self.end_points, self.tract_pct_minority, 'composition', False)
		for i in range(0, len(holding['compositions'])):
			holding['compositions'][i]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		self.container['censuscharacteristics'].append(holding)

		holding = OrderedDict({})
		holding['characteristic'] = 'Income Characteristics'
		holding['incomes'] = self.set_list(self.end_points, self.tract_income, 'income', False)
		for i in range(0, len(holding['incomes'])):
			holding['incomes'][i]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		self.container['censuscharacteristics'].append(holding)

		extra_level = []
		holding = OrderedDict({})
		holding['characteristic'] = 'Income & Racial/Ethnic Composition'
		holding['incomes'] = self.set_list(self.end_points, self.tract_income, 'income', False)
		for i in range(0, len(holding['incomes'])):
			holding['incomes'][i]['compositions'] = self.set_list(self.end_points, self.tract_pct_minority, 'composition', False)
			for j in range(0, len(holding['incomes'][i]['compositions'])):
				holding['incomes'][i]['compositions'][j]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		extra_level.append(holding)
		self.container['incomeRaces'] = extra_level

		holding = OrderedDict({})
		holding['type'] = 'Small County'
		holding['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		self.container['types'] = []
		self.container['types'].append(holding)

		holding = OrderedDict({})
		holding['type'] = 'All Other Tracts'
		holding['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		self.container['types'].append(holding)
		self.container['total'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		return self.container

	def table_5x_builder(self):
		self.container['applicantincomes'] = self.set_list(self.end_points, self.applicant_income_bracket[:-1], 'applicantincome', False)




		#make lists of borrower characterisitics
		for i in range(0,len(self.container['applicantincomes'])):

			self.container['applicantincomes'][i]['borrowercharacteristics'] = []

			race_holding = OrderedDict({})
			race_holding['characteristic'] = 'Race'
			race_holding['races'] = self.set_list(self.end_points, self.race_names, 'race', False)
			for j in range(0,len(race_holding['races'])):
				race_holding['races'][j]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
			self.container['applicantincomes'][i]['borrowercharacteristics'].append(race_holding)

			ethnicity_holding = OrderedDict({})
			ethnicity_holding['characteristic'] = 'Ethnicity'
			ethnicity_holding['ethnicities'] = self.set_list(self.end_points, self.ethnicity_names, 'ethnicity', False)
			for j in range(0,len(ethnicity_holding['ethnicities'])):
				ethnicity_holding['ethnicities'][j]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
			self.container['applicantincomes'][i]['borrowercharacteristics'].append(ethnicity_holding)

			minoritystatus_holding = OrderedDict({})
			minoritystatus_holding['characteristic'] = 'Minority Status'
			minoritystatus_holding['minoritystatus'] = self.set_list(self.end_points, self.minority_statuses, 'minoritystatus', False)
			for j in range(0,len(minoritystatus_holding['minoritystatus'])):
				minoritystatus_holding['minoritystatus'][j]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', False)
			self.container['applicantincomes'][i]['borrowercharacteristics'].append(minoritystatus_holding)

		self.container['total'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		return self.container

	def set_gender_disps(self):
		for i in range(0, len(self.race_names)):
			for g in range(0, len(self.gender_list)):
				self.container['races'][i]['genders'][g]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		for i in range(0, len(self.ethnicity_names)):
			for g in range(0, len(self.gender_list)):
				self.container['ethnicities'][i]['genders'][g]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		for i in range(0, len(self.minority_statuses)):
			for g in range(0, len(self.gender_list)):
				self.container['minoritystatuses'][i]['genders'][g]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
	def set_4x_races(self):
		self.container['races'] = self.set_list(self.end_points, self.race_names, 'race', False)
		for i in range(0,len(self.container['races'])):
			self.container['races'][i]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
			self.container['races'][i]['genders'] = self.set_list(self.end_points, self.gender_list, 'gender', False)

	def set_4x_ethnicity(self):
		self.container['ethnicities'] = self.set_list(self.end_points, self.ethnicity_names, 'ethnicity', False)
		for i in range(0, len(self.container['ethnicities'])):
			self.container['ethnicities'][i]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
			self.container['ethnicities'][i]['genders'] = self.set_list(self.end_points, self.gender_list, 'gender', False)

	def set_4x_minority(self):
		self.container['minoritystatuses'] = self.set_list(self.end_points, self.minority_statuses, 'minoritystatus', False)
		for i in range(0, len(self.container['minoritystatuses'])):
			self.container['minoritystatuses'][i]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
			self.container['minoritystatuses'][i]['genders'] = self.set_list(self.end_points, self.gender_list, 'gender', False)

	def set_4x_incomes(self):
		self.container['incomes'] = self.set_list(self.end_points, self.applicant_income_bracket, 'income', False)
		for i in range(0, len(self.container['incomes'])):
			self.container['incomes'][i]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		self.container['total'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)

	def table_4x_builder(self): #builds the table 4-1 JSON object: disposition of application by race and gender
		self.set_4x_races()
		self.set_4x_ethnicity()
		self.set_4x_minority()
		self.set_4x_incomes()
		self.set_gender_disps()
		return self.container

	def set_purchasers_NA(self, holding_list):
		purchasers = []
		for item in self.purchaser_names:
			purchasersholding = OrderedDict({})
			purchasersholding['name'] = "{}".format(item)
			for item in holding_list: #pass in the appropriate holding list for each set_purchasers call
				if item == 'juniorliencount' or item == 'juniorlienvalue':
					purchasersholding[item] = 'NA'
				else:
					purchasersholding[item] = 0
			purchasers.append(purchasersholding)
		return purchasers

	def build_rate_spreads(self): #builds the rate spreads section of the report 3-2 JSON
		spreads = []
		for rate in self.table32_rates:
			holding = OrderedDict({})
			holding['point'] = "{}".format(rate)
			if self.table32_rates.index(rate) < 4:
				holding['purchasers'] = self.set_purchasers_NA(['firstliencount', 'firstlienvalue', 'juniorliencount', 'juniorlienvalue'])
			else:
				#holding['purchasers'] = self.set_purchasers(['firstliencount', 'firstlienvalue', 'juniorliencount', 'juniorlienvalue'])
				holding['purchasers'] = self.set_list(['firstliencount', 'firstlienvalue', 'juniorliencount', 'juniorlienvalue'], self.purchaser_names, 'name', True)
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
			holding['purchasers'] = self.set_list(self.end_points, self.purchaser_names, 'name', True)
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
			holding['purchasers'] = self.set_list(self.end_points, self.purchaser_names, 'name', True)
			top[container_name].append(holding)
		self.censuscharacteristics.append(top)

	def table_32_builder(self): #builds the JSON structure for report 3-2
		pricinginformation = []
		categories = ['No reported pricing data', 'reported pricing data']
		for cat in categories:
			holding = OrderedDict({})
			holding['pricing']= "{}".format(cat)
			holding['purchasers']  = self.set_list(['firstliencount', 'firstlienvalue', 'juniorliencount', 'juniorlienvalue'], self.purchaser_names, 'name', True) #purchasers is overwritten each pass in the holding dictionary
			pricinginformation.append(holding)
		self.container['pricinginformation'] = pricinginformation
		holding = OrderedDict({})
		points = self.build_rate_spreads()
		self.container['points'] = points
		hoepa = OrderedDict({})
		hoepa['pricing'] = 'hoepa loans'
		hoepa['purchasers'] = self.set_list(['firstliencount', 'firstlienvalue', 'juniorliencount', 'juniorlienvalue'], self.purchaser_names, 'name', True)
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
		totals['purchasers'] = self.set_list(self.end_points, self.purchaser_names, 'name', True)
		self.container['total'] = totals
		return self.container

	def set_list(self, end_points, key_list, key_name, ends_bool):
		holding_list = []
		for item in key_list:
			holding_dict = OrderedDict({})
			holding_dict[key_name] = "{}".format(item)
			if ends_bool == True:
				for point in end_points:
					holding_dict[point] = 0
			holding_list.append(holding_dict)
		return holding_list

	def table_8x_builder(self):
		holding = OrderedDict({})
		self.container['applicantcharacteristics'] = []
		holding = self.table_8_helper('Races', 'race', self.race_names)
		self.container['applicantcharacteristics'].append(holding)
		holding = self.table_8_helper('Ethnicities', 'ethnicity', self.ethnicity_names)
		self.container['applicantcharacteristics'].append(holding)
		holding = self.table_8_helper('Minority Status', 'minoritystatus', self.minority_statuses)
		self.container['applicantcharacteristics'].append(holding)
		holding = self.table_8_helper('Genders', 'gender', self.gender_list2)
		self.container['applicantcharacteristics'].append(holding)
		holding = self.table_8_helper('Incomes', 'income', self.applicant_income_bracket)
		self.container['applicantcharacteristics'].append(holding)
		return self.container

	def table_8_helper(self, key, key_singular, row_list):
		temp = OrderedDict({})
		temp['characteristic'] = key
		if key == 'Minority Status':
			key = 'minoritystatuses'
		temp[key.lower()] = self.set_list(self.end_points, row_list, key_singular, False)

		for i in range(0, len(temp[key.lower()])):
			temp[key.lower()][i]['denialreasons'] = self.set_list(self.end_points, self.denial_reasons, 'denialreason', True)
		return temp


	def table_9x_builder(self):
		age_list = ['2000 - 2010', '1990 - 1999', '1980 - 1989', '1970 - 1979', '1969 or Earlier', 'Age Unknown']
		loan_category = ['FHA, FSA/RHS & VA', 'Conventional', 'Refinancings', 'Home Improvement Loans', 'Loans on Dwellings For 5 or More Families', 'Nonoccupant Loans from Columns A, B, C & D', 'Loans on Manufactured Home Dwellings From Columns A, B, C & D']
		holding = OrderedDict({})
		holding['characteristic'] = 'Census Tracts by Median Age of Homes'
		holding['medianages'] = self.set_list(self.end_points, age_list, 'medianage', False)

		for i in range(0, len(holding['medianages'])):
			holding['medianages'][i]['loancategories'] = self.set_list(self.end_points, loan_category, 'loancategory', False)
		for i in range(0, len(holding['medianages'])):
			for j in range(0, len(holding['medianages'][i]['loancategories'])):
				holding['medianages'][i]['loancategories'][j]['dispositions'] = self.set_list(self.end_points, self.dispositions_list[:6], 'disposition', True)
		return holding

	def print_JSON(self): #prints a json object to the terminal
		import json
		print json.dumps(self.container, indent=4)

	def write_JSON(self, name, data): #writes a json object to file
		with open(name, 'w') as outfile: #writes the JSON structure to a file for the path named by report's header structure
			json.dump(data, outfile, indent=4, ensure_ascii = False)

build = build_JSON()
#table_31 = build.table_31_builder()
#build.print_JSON()
#table_32 = build.table_32_builder()
#build.print_JSON()
#table_4x = build.table_4x_builder()
#build.print_JSON()
table_5x = build.table_5x_builder()
build.print_JSON()
#table_7x = build.table_7x_builder()
#build.print_JSON()
#table_8x = build.table_8x_builder()
#build.print_JSON()
#build.write_JSON('report8.json', table_8x)
#table_9x = build.table_9x_builder()
#build.print_JSON()
table_5x['applicantincomes'][0]['borrowercharacteristics'][0]['races'][2]['dispositions'][1]['count'] +=100

build.write_JSON('report5.json', table_5x)



