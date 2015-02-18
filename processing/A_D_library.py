#this file holds the classes used to create the A&D reports using the HMDA LAR files combined with Census demographic information
import numpy
import psycopg2
import psycopg2.extras
from collections import OrderedDict
import json
import os
import csv
class AD_report(object):
	pass

class report_selector(AD_report):
	def __init__(self):
		self.report_list = {} #fill this dictionary with the headers in the CSV as dict keys
		#how best inialize lists to avoid errors? key errors?

	def initalize_lists(self, infile):
		with open(infile, 'r') as csvfile:
			msareader = csv.DictReader(csvfile, delimiter = ',', quotechar='"')
			for row in msareader:
				for key in row: #does this happen on every row? how to stop in the first row?
					self.report_list[key] = []

	def get_report_lists(self, infile):
		#file will have MSA list (entire population)
		#list of FIs in MSA to generate reports for?
		#open the controller file that tells which reports to generate
		self.initalize_lists(infile) #initialize all reports lists
		with open(infile, 'r') as csvfile:
			msareader = csv.DictReader(csvfile, delimiter = ',', quotechar='"')
			for row in msareader:
				for key in row: # scan through keys to check all report flags in a row
					if row[key] == '1':
						self.report_list[key].append(row['MSA number']) #if an MSA has a report flagged as '1' add it to the generation list

		#need to find a work around to add lists for disclosure reports that will return lists of FIs and not flags

class parse_inputs(AD_report):
	#needs to take all the variables used in all the reports
	#use if exists logic to pass in a row and parse it to a dictionary
	#does this require standardization of the SQL query to return the same string?
	#check the psycopg2.extras docs on dictcursor
	inputs = {}
	def __init__(self):
		#initialize rate spread sum variables for first liens
		self.inputs['Fannie Mae first rates'] =0
		self.inputs['Ginnie Mae first rates'] =0
		self.inputs['Freddie Mac first rates'] =0
		self.inputs['Farmer Mac first rates'] =0
		self.inputs['Private Securitization first rates'] =0
		self.inputs['Commercial bank, savings bank or association first rates'] =0
		self.inputs['Life insurance co., credit union, finance co. first rates'] =0
		self.inputs['Affiliate institution first rates'] = 0
		self.inputs['Other first rates'] =0
		#initialize rate spread sum variables for junior liens
		self.inputs['Fannie Mae junior rates'] =0
		self.inputs['Ginnie Mae junior rates'] =0
		self.inputs['Freddie Mac junior rates'] =0
		self.inputs['Farmer Mac junior rates'] =0
		self.inputs['Private Securitization junior rates'] =0
		self.inputs['Commercial bank, savings bank or association junior rates'] =0
		self.inputs['Life insurance co., credit union, finance co. junior rates'] =0
		self.inputs['Affiliate institution junior rates'] = 0
		self.inputs['Other junior rates'] =0
		#initialize lists to hold rates for determining the median first lien rate
		self.inputs['Fannie Mae first lien list'] = []
		self.inputs['Ginnie Mae first lien list'] = []
		self.inputs['Freddie Mac first lien list'] = []
		self.inputs['Farmer Mac first lien list'] = []
		self.inputs['Private Securitization first lien list'] = []
		self.inputs['Commercial bank, savings bank or association first lien list'] = []
		self.inputs['Life insurance co., credit union, finance co. first lien list'] = []
		self.inputs['Affiliate institution first lien list'] = []
		self.inputs['Other first lien list'] = []
		#initialize lists to hold rates for determining the median junior lien rate
		self.inputs['Fannie Mae junior lien list'] = []
		self.inputs['Ginnie Mae junior lien list'] = []
		self.inputs['Freddie Mac junior lien list'] = []
		self.inputs['Farmer Mac junior lien list'] = []
		self.inputs['Private Securitization junior lien list'] = []
		self.inputs['Commercial bank, savings bank or association junior lien list'] = []
		self.inputs['Life insurance co., credit union, finance co. junior lien list'] = []
		self.inputs['Affiliate institution junior lien list'] = []
		self.inputs['Other junior lien list'] = []

	def parse_t31(self, row): #takes a row from a table 3-1 query and parses it to the inputs dictionary (28 tuples)
		#parsing inputs for report 3.1
		#self.inputs will be returned to for use in the aggregation function
		#instantiate classes to set loan variables
		MSA_index = MSA_info()
		demo=demographics()
		#race lists will hold 5 integers
		a_race = []
		co_race = []
		#fill race lists from the demographics class
		a_race = demo.co_race_list(row)
		co_race = demo.a_race_list(row)

		#add data elements to dictionary
		self.inputs['a ethn'] = row['applicantethnicity'] #ethnicity of the applicant
		self.inputs['co ethn'] = row['co_applicantethnicity'] #ethnicity of the co-applicant
		self.inputs['income'] = row['applicantincome'] #relied upon income rounded to the nearest thousand
		self.inputs['purchaser'] = int(row['purchasertype']) -1 #adjust purchaser index down 1 to match JSON
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode']
		self.inputs['state name'] = row['statename']
		self.inputs['census tract'] = row['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
		self.inputs['county code'] = row['countycode']
		self.inputs['county name'] = row['countyname']
		self.inputs['MSA median income'] = row['ffiec_median_family_income']
		self.inputs['minority percent'] = row['minoritypopulationpct']
		self.inputs['tract to MSA income'] = row['tract_to_msa_md_income']
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs)
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs)
		self.inputs['minority percent'] = MSA_index.minority_percent(self.inputs)
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs)
		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['ethnicity'] = demo.set_loan_ethn(self.inputs) #requires  ethnicity be parsed prior to running set_loan_ethn
		self.inputs['race'] = demo.set_race(self.inputs, a_race, co_race) #requires joint status be set prior to running set_race
		self.inputs['minority count'] = demo.minority_count(a_race)

	def parse_t32(self, row): #takes a row from a table 3-1 query and parses it to the inputs dictionary (28 tuples)
		#parsing inputs for report 3.1
		#self.inputs will be returned to for use in the aggregation function
		#instantiate classes to set loan variables
		demo=demographics()
		#add data elements to dictionary
		self.inputs['rate spread'] = row['ratespread']
		self.inputs['lien status'] = row['lienstatus']
		self.inputs['hoepa flag'] = int(row['hoepastatus'])
		self.inputs['purchaser'] = int(row['purchasertype']) -1 #adjust purchaser index down 1 to match JSON
		self.inputs['year'] = row['asofdate']
		self.inputs['state code'] = row['statecode']
		self.inputs['state name'] = row['statename']
		self.inputs['census tract'] = row['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
		self.inputs['county code'] = row['countycode']
		self.inputs['county name'] = row['countyname']
		self.inputs['rate spread index'] = demo.rate_spread_index(self.inputs['rate spread'])

class demographics(AD_report):
	#holds all the functions for setting race, minority status, and ethnicity for FFIEC A&D reports
	#this class is called when the parse_t31 function is called by the controller

	#set race_code to integers for use in JSON structure lists
	#American Indian/Alaska Native or 1 indexed at 0
	#Asian or 2 indexed at 1
	#Black or 3 indexed at 2
	#Pacific Islander or 4 indexed at 3
	#White or 5 indexed at 4
	#Not Provided indexed at 5
	#Not Applicable indexed at 6
	#2 minority indexed 7
	#joint indexed 8
	#not reported indexed 9
	def rate_spread_index(self, rate):
		if rate == 'NA   ' or rate == '     ':
			return 8
		elif float(rate) >= 1.5 and float(rate) <= 1.99:
			return 0
		elif float(rate) >= 2.00 and float(rate) <= 2.49:
			return 1
		elif float(rate) >= 2.50 and float(rate) <= 2.99:
			return 2
		elif float(rate) >= 3.00 and float(rate) <= 3.49:
			return 3
		elif float(rate) >= 3.50 and float(rate) <= 4.49:
			return 4
		elif float(rate) >= 4.50 and float(rate) <= 5.49:
			return 5
		elif float(rate) >= 5.50  and float(rate) <= 6.49:
			return 6
		elif float(rate) >= 6.50:
			return 7

	def minority_count(self, a_race):
		#the minority count is the count of minority races listed for the primary applicant
		minority_count = 0
		for race in a_race:
			if race < 5 and race > 0:
				minority_count += 1
		return minority_count

	def set_non_white(self, race_list): #pass in a list of length 5, return a boolean
		for i in range(0,5):
			if race_list[i] < 5 and race_list[i] != 0:
				return True #flag true if applicant listed a minority race
				break
			elif race_list[i] == 5:
				return False #flag false if the only race listed was white (5)

	def set_joint(self, inputs): #takes a dictionary 'inputs' which is held in the controller(?) object and used to process each loan row
		#joint status exists if one borrower is white and one is non-white
		#check to see if joint status exists
		if inputs['app non white flag'] == False and inputs['co non white flag'] == False:
			return False #flag false if both applicant and co-applicant are white
		elif inputs['app non white flag'] == True and inputs['co non white flag'] == True:
			return False #flag false if both applicant and co-applicant are minority
		elif inputs['app non white flag'] == True and inputs['co non white flag'] ==  False:
			return True #flag true if one applicant is minority and one is white
		elif inputs['app non white flag'] == False and inputs['co non white flag'] == True:
			return True #flag true if one applicant is minority and one is white

	def set_minority_status(self, inputs):
		#determine minority status
		#if either applicant reported a non-white race or an ethinicity of hispanic or latino then minority status is true
		if inputs['app non white flag'] == True or inputs['co non white flag'] == True or inputs['a ethn'] == '1' or inputs['co ethn'] == '1':
			return  1
		#if both applicants reported white race and non-hispanic/latino ethnicity then minority status is false
		elif inputs['app non white flag'] != True and inputs['co non white flag'] != True and inputs['a ethn']  != '1' and inputs['co ethn'] != '1':
			return 0
		else:
			print 'minority status not set'

	#this function outputs a number code for ethnicity: 0 - hispanic or latino, 1 - not hispanic/latino
	#2 - joint (1 applicant hispanic/latino 1 not), 3 - ethnicity not available
	def set_loan_ethn(self, inputs):
		#if both ethnicity fields are blank report not available(3)
		if inputs['a ethn'] == ' ' and inputs['co ethn'] == ' ':
			return  3 #set to not available

		#determine if the loan is joint hispanic/latino and non hispanic/latino(2)
		elif inputs['a ethn'] == '1' and inputs['co ethn'] != '1':
			return  2 #set to joint
		elif inputs['a ethn'] != '1' and inputs['co ethn'] == '1':
			return  2 #set to joint

		#determine if loan is of hispanic ethnicity (appplicant is hispanic/latino, no co applicant info or co applicant also hispanic/latino)
		elif inputs['a ethn'] == '1' and inputs['co ethn'] == '1':
			return  0
		elif inputs['a ethn'] == '1' and (inputs['co ethn'] == ' ' or inputs['co ethn'] == '3' or inputs['co ethn'] == '4' or inputs['co ethn']== '5'):
			return  0
		elif (inputs['a ethn'] == ' ' or inputs['a ethn'] == '3' or inputs['a ethn'] == '4' or inputs['a ethn'] == '5') and inputs['co ethn'] == '1':
			return  0
		#determine if loan is not hispanic or latino
		elif inputs['a ethn'] == '2' and inputs['co ethn'] != '1':
			return  1
		elif inputs['a ethn'] != '1' and inputs['co ethn'] == '2':
			return  1
		elif (inputs['a ethn'] == '3' or inputs['a ethn'] == '4') and (inputs['co ethn'] != '1' and inputs['co ethn'] != '2'):
			return  3
		else:
			print "error setting ethnicity"

	def a_race_list(self, row):
		#filling the loan applicant race code lists (5 codes per applicant)
		a_race = [race for race in row[1:6]]

		#convert ' ' entries to 0 for easier comparisons and loan aggregation
		for i in range(0, 5):
			if a_race[i] == ' ':
				a_race[i] = 0
		#convert string entries to int for easier comparison and loan aggregation
		return [int(race) for race in a_race]

	def co_race_list(self, row):
		#filling the loan co-applicant race code lists (5 codes per applicant)
		co_race = [race for race in row[6:11]]
		for i in range(0,5):
			if co_race[i] == ' ':
				co_race[i] = 0
		#convert string entries to int for easier comparison and loan aggregation

		return [int(race) for race in co_race]

	def set_race(self, inputs, a_race, co_race):
		#inputs is a dictionary, a_race and co_race are 5 element integer lists
		#if one white and one minority race are listed, use the minority race
		#race options are: joint, 1 through 5, 2 minority, not reported
		#if the entry is 'joint' then the loan is aggregated as 'joint'
		#create a single race item instead of a list to use in comparisons to build aggregates

		if inputs['joint status'] == True:
			return  8
		#determine if the loan will be filed as 'two or more minority races'
		#if two minority races are listed, the loan is 'two or more minority races'
		#if any combination of two or more race fields are minority then 'two or more minority races'
		elif self.minority_count(a_race) > 1:
			return  7

		#if only the first race field is used, use the first filed
		elif a_race[0] != 0 and a_race[1] == 0 and a_race[2] == 0 and a_race[3] == 0 and a_race[4] == 0:
			return  a_race[0] #if only one race is reported, and joint status and minority status are false, set race to first race

		elif a_race[0] == 0 and a_race[1] == 0 and a_race[2] == 0 and a_race[3] == 0 and a_race[4] == 0:
			return  9 #if all race fields are blank, set race to 'not reported'

		else:
			#does this code work for minority co applicants with non-minority applicants?
			for i in range(1,5):
				if i in a_race: #check if a minority race is present in the race array
					return  a_race[0]
					if a_race[0] == 5:
						for code in a_race:
							if code < 5 and code != 0: #if first race is white, but a minority race is reported, set race to the first minority reported
								return  code
								break #exit on first minority race


class build_JSON(AD_report):

	def __init__(self):
		self.container = OrderedDict({}) #master container for the JSON structure
		self.msa = OrderedDict({}) #stores header information for the MSA
		self.borrowercharacteristics = [] #holds all the borrower lists and dicts for the borrower portion of table 3-1
		self.censuscharacteristics = [] #censuscharacteristics holds all the lists and dicts for the census portion of the table 3-1
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
		self.state_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE':'Delaware',
			'FL':'Florida', 'GA':'Georgia', 'HI':'Hawaii', 'ID':'Idaho', 'IL':'Illinois', 'IN':'Indiana', 'IA':'Iowa', 'KS':'Kansas', 'KY': 'Kentucky', 'LA':'Louisiana', 'ME': 'Maine', 'MD':'Maryland',
			'MA':'Massachusetts', 'MI':'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE':'Nebraska', 'NV':'Nevada', 'NH':'New Hampshire', 'NJ':'New Jersey', 'NM':'New Mexico',
			'NY':'New York', 'NC':'North Carolina', 'ND':'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR':'Oregon','PA':'Pennsylvania', 'RI':'Rhode Island', 'SC':'South Carolina',
			'SD':'South Dakota', 'TN':'Tensessee', 'TX':'Texas', 'UT':'Utah', 'VT':'Vermont', 'VA':'Virginia', 'WA': 'Washington', 'WV':'West Virginia', 'WI':'Wisconsin', 'WY':'Wyoming', 'PR':'Puerto Rico', 'VI':'Virgin Islands'}
	def get_state_name(self, abbrev):
		state_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE':'Delaware',
				'FL':'Florida', 'GA':'Georgia', 'HI':'Hawaii', 'ID':'Idaho', 'IL':'Illinois', 'IN':'Indiana', 'IA':'Iowa', 'KS':'Kansas', 'KY': 'Kentucky', 'LA':'Louisiana', 'ME': 'Maine', 'MD':'Maryland',
				'MA':'Massachusetts', 'MI':'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE':'Nebraska', 'NV':'Nevada', 'NH':'New Hampshire', 'NJ':'New Jersey', 'NM':'New Mexico',
				'NY':'New York', 'NC':'North Carolina', 'ND':'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR':'Oregon','PA':'Pennsylvania', 'RI':'Rhode Island', 'SC':'South Carolina',
				'SD':'South Dakota', 'TN':'Tensessee', 'TX':'Texas', 'UT':'Utah', 'VT':'Vermont', 'VA':'Virginia', 'WA': 'Washington', 'WV':'West Virginia', 'WI':'Wisconsin', 'WY':'Wyoming', 'PR':'Puerto Rico', 'VI':'Virgin Islands'}
		return state_names[abbrev]

	def table_headers(self, table_num): #holds table descriptions
		if table_num == '3-1':
			return 'Loans sold. By characteristics of borrower and census tract in which property is located and by type of purchaser (includes originations and purchased loans).'
		elif table_num =='3-2':
			return 'Pricing Information for First and Junior Lien Loans Sold by Type of Purchaser (includes originations only).'

	def set_header(self, inputs, MSA, desc, table_type, table_num): #add a variable for desc_string
		msa = OrderedDict({})
		self.container['table'] = table_num
		self.container['type'] = table_type
		self.container['desc'] = desc
		self.container['year'] = inputs['year']
		self.msa['id'] = MSA
		#self.msa['name'] = inputs['MSA name'] #need to add MSA names to a database or read-in file
		self.msa['state'] = inputs['state name']
		self.msa['state_name'] = self.state_names[self.msa['state']]
		self.container['msa'] = self.msa
		return self.container

	def set_purchasers(self):
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

	def set_purchasers32v2(self): #this function is used for the 'mean' and 'median' sections as they do not have loan value sections
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

	def table_32_builder(self):
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
			holding[container_name[:-1]] = "{}".format(item)
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
			holding[container_name[:-1]] = "{}".format(item)
			holding['purchasers'] = self.set_purchasers()
			top[container_name].append(holding)
		self.censuscharacteristics.append(top)

	def table_31_builder(self):
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
		return self.container

	def print_JSON(self):
		import json
		print json.dumps(self.container, indent=4)

	def write_JSON(self, name, data, path):
		#with open(name, 'w') as outfile:
		#	json.dump(data, outfile, indent = 4, ensure_ascii=False)
		with open(os.path.join(path, name), 'w') as outfile: #writes the JSON structure to a file for the path named by report's header structure
			json.dump(data, outfile, indent=4, ensure_ascii = False)

class connect_DB(AD_report):

	def connect(self):
		with open('/Users/roellk/Desktop/python/credentials.txt', 'r') as f:
			credentials = f.read()
		cred_list = credentials.split(',')
		dbname = cred_list[0]
		user = cred_list[1]
		host = cred_list[2]
		password = cred_list[3]

		connect_string = "dbname=%s user=%s host=%s password =%s" %(dbname, user, host, password) #set a string for connection to SQL
		try:
			conn = psycopg2.connect(connect_string)
			print "i'm connected"
		#if database connection results in an error print the following
		except:
			print "I am unable to connect to the database"
		return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

class MSA_info(AD_report):

	def app_income_to_MSA(self, inputs):
		#set income bracket index
		if inputs['income'] == 'NA  ' or inputs['income'] == '    ':
			return 5
		elif inputs['MSA median income'] == 'NA      ' or inputs['MSA median income'] == '        ' :
			return 6 #placeholder for MSA median income unavailable
		else:
			inputs['percent MSA income'] = (float(inputs['income']) / (float(inputs['MSA median income'] )/1000)) *100
			#determine income bracket for use as an index in the JSON object
			if inputs['percent MSA income'] < 50:
				return 0
			elif inputs['percent MSA income'] <= 79:
				return 1
			elif inputs['percent MSA income'] <= 99:
				return 2
			elif inputs['percent MSA income'] <= 119:
				return 3
			elif inputs['percent MSA income'] >= 120:
				return 4
			else:
				print 'error setting percent MSA income bracket for index'

	def minority_percent(self, inputs):
		#set index codes for minority population percent
		if inputs['minority percent'] == '      ' or inputs['minority percent'] == 'NA    ':
			return  4
		elif float(inputs['minority percent']) < 10.0:
			return  0
		elif float(inputs['minority percent'])  <= 49.0:
			return  1
		elif float(inputs['minority percent'])  <= 79.0:
			return  2
		elif float(inputs['minority percent'])  <= 100.0:
			return  3
		else:
			print "minority percent index not set"
			print "value of", float(inputs['minority percent'])

	def tract_to_MSA_income(self, inputs):
		#set census MSA income level: low, moderatde, middle, upper
		if inputs['tract to MSA income'] == '      ' or inputs['tract to MSA income'] == 'NA    ':
			return 4
		elif float(inputs['tract to MSA income']) < 50.0:
			return 0
		elif float(inputs['tract to MSA income']) <= 79.0:
			return 1
		elif float(inputs['tract to MSA income']) <= 119.0:
			return 2
		elif float(inputs['tract to MSA income']) >= 119.0:
			return 3
		else:
			print "error setting tract to MSA income index"
			print inputs['tract to MSA income']

class queries(AD_report):
	#can I decompose these query parts into lists and concatenate them prior to passing to the cursor?
	def count_rows_2012(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s;'''
		return SQL

	def table_3_1(self):
		#create an index in PostGres to speed up this query
		#set the SQL statement to select the needed fields to aggregate loans for the table_3 JSON structure
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, co_applicantethnicity, applicantincome, hoepastatus,
			purchasertype, loanamount, asofdate, statecode, statename, countycode, countyname,
			ffiec_median_family_income, minoritypopulationpct, tract_to_msa_md_income
			FROM hmdapub2012 WHERE msaofproperty = %s;'''
		return SQL

	def table_3_2(self):
		#create an index in PostGres to speed up this query
		#set the SQL statement to select the needed fields to aggregate loans for the table_3 JSON structure
		SQL = '''SELECT
			censustractnumber,  ratespread, lienstatus, hoepastatus,
			purchasertype, asofdate, statecode, statename, countycode, countyname
			FROM hmdapub2012 WHERE msaofproperty = %s;'''
		return SQL

class aggregate(AD_report):
	def __init__(self):
		pass

	def index_list(self, item, listless):
		#returns the index of a an item in a list
		if item in listless:
			return listless.index(item)
		else:
			print "oops, your value is not in that list"

	def by_race(self, container, inputs):
	#aggregates loans by race category
		container['borrowercharacteristics'][0]['races'][inputs['race']]['purchasers'][inputs['purchaser']]['count'] += 1
		container['borrowercharacteristics'][0]['races'][inputs['race']]['purchasers'][inputs['purchaser']]['value'] += inputs['loan value']
			#print container['borrowercharacteristics'][0]['races'][inputs['race']]['purchasers'][inputs['purchaser']]['count'], "count after"
	def by_ethnicity(self, container, inputs):
		container['borrowercharacteristics'][1]['ethnicities'][inputs['ethnicity']]['purchasers'][inputs['purchaser']]['count'] += 1
		container['borrowercharacteristics'][1]['ethnicities'][inputs['ethnicity']]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def by_minority_status(self, container, inputs):
		container['borrowercharacteristics'][2]['minoritystatuses'][inputs['minority status']]['purchasers'][inputs['purchaser']]['count'] += 1
		container['borrowercharacteristics'][2]['minoritystatuses'][inputs['minority status']]['purchasers'][inputs['purchaser']]['value']+= int(inputs['loan value'])

	def by_applicant_income(self, container, inputs):
		if inputs['income bracket'] > 5:
			pass
		else:
			container['borrowercharacteristics'][3]['applicantincomes'][inputs['income bracket']]['purchasers'][inputs['purchaser']]['count'] += 1
			container['borrowercharacteristics'][3]['applicantincomes'][inputs['income bracket']]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def by_minority_composition(self, container, inputs):
		if inputs['minority percent'] == 4:
			pass
		else:
			container['censuscharacteristics'][0]['tractpctminority'][inputs['minority percent']]['purchasers'][inputs['purchaser']]['count'] += 1
			container['censuscharacteristics'][0]['tractpctminority'][inputs['minority percent']]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def by_tract_income(self, container, inputs):
		if inputs['tract income index'] > 3:
			pass
		else:
			container['censuscharacteristics'][1]['incomelevel'][inputs['tract income index']]['purchasers'][inputs['purchaser']]['count'] +=1
			container['censuscharacteristics'][1]['incomelevel'][inputs['tract income index']]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def totals(self, container, inputs):
		container['total']['purchasers'][inputs['purchaser']]['count'] +=1
		container['total']['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def by_pricing_status(self, container, inputs):
		if inputs['rate spread index'] == 8 and inputs['lien status'] == '1':
			container['pricinginformation'][0]['purchasers'][inputs['purchaser']]['first lien count'] +=1
			container['pricinginformation'][0]['purchasers'][inputs['purchaser']]['first lien value'] += int(inputs['loan value'])
		elif inputs['rate spread index'] == 8 and inputs['lien status'] == '2':
			container['pricinginformation'][0]['purchasers'][inputs['purchaser']]['junior lien count'] +=1
			container['pricinginformation'][0]['purchasers'][inputs['purchaser']]['junior lien value'] += int(inputs['loan value'])
		else:
			if inputs['lien status'] == '1' and inputs['rate spread index'] < 8:
				container['pricinginformation'][1]['purchasers'][inputs['purchaser']]['first lien count'] +=1
				container['pricinginformation'][1]['purchasers'][inputs['purchaser']]['first lien value'] += int(inputs['loan value'])
			elif inputs['lien status'] == '2' and inputs['rate spread index'] < 8:
				container['pricinginformation'][1]['purchasers'][inputs['purchaser']]['junior lien count'] += 1
				container['pricinginformation'][1]['purchasers'][inputs['purchaser']]['junior lien value'] += int(inputs['loan value'])

	def by_rate_spread(self, container, inputs):
		if inputs['lien status'] == '1' and inputs['rate spread index'] < 8:
			container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['first lien count'] +=1
			container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['first lien value'] += int(inputs['loan value'])

		elif inputs['lien status'] == '2' and inputs['rate spread index'] <8:
			container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['junior lien count'] +=1
			container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['junior lien value'] += int(inputs['loan value'])

	def by_hoepa_status(self, container, inputs):
		if inputs['hoepa flag'] == 1:
			if inputs['lien status'] == '1':
				container['hoepa']['purchasers'][inputs['purchaser']]['first lien count'] +=1
				container['hoepa']['purchasers'][inputs['purchaser']]['first lien value'] +=int(inputs['loan value'])
			elif inputs['lien status'] == '2':
				container['hoepa']['purchasers'][inputs['purchaser']]['junior lien count'] +=1
				container['hoepa']['purchasers'][inputs['purchaser']]['junior lien value'] +=int(inputs['loan value'])
			else:
				print "invalid hoepa flag, oops"
		elif inputs['hoepa flag'] == 2:
			pass
		else:
			print "HOEPA flag not present or outside parameters"

	def rate_sum(self, container, inputs):
		if inputs['rate spread'] != 'NA   ' and inputs['rate spread'] != '     ':
			#lien status 1 - first liens
			if inputs['purchaser'] == 0 and inputs['lien status'] == '1':
				inputs['Fannie Mae first rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 1 and  inputs['lien status'] == '1':
				inputs['Ginnie Mae first rates'] +=float(inputs['rate spread'])
			elif inputs['purchaser'] == 2 and  inputs['lien status'] == '1':
				inputs['Freddie Mac first rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 3 and  inputs['lien status'] == '1':
				inputs['Farmer Mac first rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 4 and  inputs['lien status'] == '1':
				inputs['Private Securitization first rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 5 and  inputs['lien status'] == '1':
				inputs['Commercial bank, savings bank or association first rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 6 and  inputs['lien status'] == '1':
				inputs['Life insurance co., credit union, finance co. first rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 7 and  inputs['lien status'] == '1':
				inputs['Affiliate institution first rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 8 and  inputs['lien status'] == '1':
				inputs['Other first rates'] += float(inputs['rate spread'])
			#lien status 2 - junior liens
			elif inputs['purchaser'] == 0 and inputs['lien status'] == '2':
				inputs['Fannie Mae junior rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 1 and  inputs['lien status'] == '2':
				inputs['Ginnie Mae junior rates'] +=float(inputs['rate spread'])
			elif inputs['purchaser'] == 2 and  inputs['lien status'] == '2':
				inputs['Freddie Mac junior rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 3 and  inputs['lien status'] == '2':
				inputs['Farmer Mac junior rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 4 and  inputs['lien status'] == '2':
				inputs['Private Securitization junior rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 5 and  inputs['lien status'] == '2':
				inputs['Commercial bank, savings bank or association junior rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 6 and  inputs['lien status'] == '2':
				inputs['Life insurance co., credit union, finance co. junior rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 7 and  inputs['lien status'] == '2':
				inputs['Affiliate institution junior rates'] += float(inputs['rate spread'])
			elif inputs['purchaser'] == 8 and  inputs['lien status'] == '2':
				inputs['Other purchaser junior rates'] += float(inputs['rate spread'])

		else:
			pass

	def by_mean(self, container, inputs):
		first_lien_purchasers = ['Fannie Mae first rates', 'Ginnie Mae first rates', 'Freddie Mac first rates', 'Farmer Mac first rates', 'Private Securitization first rates', 'Commercial bank, savings bank or association first rates', 'Life insurance co., credit union, finance co. first rates', 'Affiliate institution first rates', 'Other first rates']
		junior_lien_purchasers = ['Fannie Mae junior rates', 'Ginnie Mae junior rates', 'Freddie Mac junior rates', 'Farmer Mac junior rates', 'Private Securitization junior rates', 'Commercial bank, savings bank or association junior rates', 'Life insurance co., credit union, finance co. junior rates', 'Affiliate institution junior rates', 'Other junior rates']
		for n in range(0,9):
			if float(container['pricinginformation'][1]['purchasers'][n]['first lien count']) > 0 and inputs[first_lien_purchasers[n]] > 0: #bug fix for divide by 0 errors
				container['points'][8]['purchasers'][n]['first lien'] = round(inputs[first_lien_purchasers[n]]/float(container['pricinginformation'][1]['purchasers'][n]['first lien count']),2)

			if float(container['pricinginformation'][1]['purchasers'][n]['junior lien count']) > 0 and inputs[junior_lien_purchasers[n]] > 0: #bug fix for divide by 0 errors
				container['points'][8]['purchasers'][n]['junior lien'] = round(inputs[junior_lien_purchasers[n]]/float(container['pricinginformation'][1]['purchasers'][n]['junior lien count']),2)

	def fill_median_lists(self, inputs):
		purchaser_first_lien_rates = ['Fannie Mae first lien list', 'Ginnie Mae first lien list', 'Freddie Mac first lien list', 'Farmer Mac first lien list', 'Private Securitization first lien list', 'Commercial bank, savings bank or association first lien list', 'Life insurance co., credit union, finance co. first lien list', 'Affiliate institution first lien list', 'Other first lien list']
		purchaser_junior_lien_rates = ['Fannie Mae junior lien list', 'Ginnie Mae junior lien list', 'Freddie Mac junior lien list', 'Farmer Mac junior lien list', 'Private Securitization junior lien list', 'Commercial bank, savings bank or association junior lien list', 'Life insurance co., credit union, finance co. junior lien list', 'Affiliate institution junior lien list', 'Other junior lien list']
		if inputs['rate spread'] == 'NA   ' or inputs['rate spread'] == '     ':
			pass
		elif inputs['lien status'] == '1':
			inputs[purchaser_first_lien_rates[inputs['purchaser']]].append(float(inputs['rate spread']))
		elif inputs['lien status'] == '2':
			inputs[purchaser_junior_lien_rates[inputs['purchaser']]].append(float(inputs['rate spread']))

	def by_median(self, container, inputs):
		purchaser_first_lien_rates = ['Fannie Mae first lien list', 'Ginnie Mae first lien list', 'Freddie Mac first lien list', 'Farmer Mac first lien list', 'Private Securitization first lien list', 'Commercial bank, savings bank or association first lien list', 'Life insurance co., credit union, finance co. first lien list', 'Affiliate institution first lien list', 'Other first lien list']
		purchaser_junior_lien_rates = ['Fannie Mae junior lien list', 'Ginnie Mae junior lien list', 'Freddie Mac junior lien list', 'Farmer Mac junior lien list', 'Private Securitization junior lien list', 'Commercial bank, savings bank or association junior lien list', 'Life insurance co., credit union, finance co. junior lien list', 'Affiliate institution junior lien list', 'Other junior lien list']
		for n in range(0,9):
			#first lien median block
			if len(inputs[purchaser_first_lien_rates[n]]) > 0:
				container['points'][9]['purchasers'][n]['first lien'] = round(numpy.median(numpy.array(inputs[purchaser_first_lien_rates[n]])),2)

			#junior lien median block
			if len(inputs[purchaser_junior_lien_rates[n]]) > 0:
				container['points'][9]['purchasers'][n]['junior lien'] = round(numpy.median(numpy.array(inputs[purchaser_junior_lien_rates[n]])),2)

	def build_report_31(self, table31, inputs):  #calls aggregation functions to fill JSON object for table 3-1
		self.by_race(table31, inputs) #aggregate loan by race
		self.by_ethnicity(table31, inputs) #aggregate loan by ethnicity
		self.by_minority_status(table31, inputs) #aggregate loan by minority status (binary determined by race and ethnicity)
		self.by_applicant_income(table31, inputs) #aggregates by ratio of appicant income to tract median income (census)
		self.by_minority_composition(table31, inputs) #aggregates loans by percent of minority residents (census)
		self.by_tract_income(table31, inputs) #aggregates loans by census tract income rating - low/moderate/middle/upper
		self.totals(table31, inputs) #aggregate totals for each purchaser
		return table31

	def build_report_32(self, table32, inputs): #calls aggregation functions to fill JSON object for table 3-2
		self.by_pricing_status(table32, inputs) #aggregate count by lien status
		self.by_rate_spread(table32, inputs) #aggregate loans by percentage points above APOR as ##.##%
		self.by_hoepa_status(table32, inputs) #aggregates loans by presence of HOEPA flag
		self.rate_sum(table32, inputs) #sums spreads above APOR for each loan purchaser, used to determine medians
		self.fill_median_lists(inputs) #fills the median rate spread for each purchaser
		#mean and median functions are not called here
		#mean and median function must be called outside the control loop
		return table32




