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

class report_selector(AD_report):
	def __init__(self):
		self.report_list = {} #fill this dictionary with the headers in the CSV as dict keys

	def initalize_lists(self, infile):
		with open(infile, 'rU') as csvfile:
			msareader = csv.DictReader(csvfile, delimiter = ',', quotechar='"')
			for row in msareader:
				for key in row:
					self.report_list[key] = [] #initialize a value list for each column header in the input file

	def get_report_lists(self, infile):
		#file will have MSA list (entire population)
		#list of FIs in MSA to generate reports for?
		#open the controller file that tells which reports to generate
		self.initalize_lists(infile) #initialize all reports lists
		with open(infile, 'rU') as csvfile:
			msareader = csv.DictReader(csvfile, delimiter = ',', quotechar='"')
			for row in msareader:
				for key in row: # scan through keys to check all report flags in a row
					if row[key] == '1':
						self.report_list[key].append(row['MSA number']) #if an MSA has a report flagged as '1' add it to the generation list
					if key == 'year': #create a year variable for each row, filepath and query should key off this year
						self.report_list[key].append(row['year'])

		#need to find a work around to add lists for disclosure reports that will return lists of FIs and not flags

class parse_inputs(AD_report):
	inputs = {}
	def __init__(self):
		#initialize rate spread sum variables for first lien means
		self.inputs['Fannie Mae first rates'] =[]
		self.inputs['Ginnie Mae first rates'] =[]
		self.inputs['Freddie Mac first rates'] =[]
		self.inputs['Farmer Mac first rates'] =[]
		self.inputs['Private Securitization first rates'] =[]
		self.inputs['Commercial bank, savings bank or association first rates'] =[]
		self.inputs['Life insurance co., credit union, finance co. first rates'] =[]
		self.inputs['Affiliate institution first rates'] = []
		self.inputs['Other first rates'] =[]
		#initialize rate spread sum variables for junior lien means
		self.inputs['Fannie Mae junior rates'] =[]
		self.inputs['Ginnie Mae junior rates'] =[]
		self.inputs['Freddie Mac junior rates'] =[]
		self.inputs['Farmer Mac junior rates'] =[]
		self.inputs['Private Securitization junior rates'] =[]
		self.inputs['Commercial bank, savings bank or association junior rates'] =[]
		self.inputs['Life insurance co., credit union, finance co. junior rates'] =[]
		self.inputs['Affiliate institution junior rates'] = []
		self.inputs['Other junior rates'] =[]

		#initialize rate spread sum variables for first lien weighted means
		self.inputs['Fannie Mae first weight'] =[]
		self.inputs['Ginnie Mae first weight'] =[]
		self.inputs['Freddie Mac first weight'] =[]
		self.inputs['Farmer Mac first weight'] =[]
		self.inputs['Private Securitization first weight'] =[]
		self.inputs['Commercial bank, savings bank or association first weight'] =[]
		self.inputs['Life insurance co., credit union, finance co. first weight'] =[]
		self.inputs['Affiliate institution first weight'] = []
		self.inputs['Other first weight'] =[]

		#initialize rate spread sum variables for junior lien weighted means
		self.inputs['Fannie Mae junior weight'] =[]
		self.inputs['Ginnie Mae junior weight'] =[]
		self.inputs['Freddie Mac junior weight'] =[]
		self.inputs['Farmer Mac junior weight'] =[]
		self.inputs['Private Securitization junior weight'] =[]
		self.inputs['Commercial bank, savings bank or association junior weight'] =[]
		self.inputs['Life insurance co., credit union, finance co. junior weight'] =[]
		self.inputs['Affiliate institution junior weight'] = []
		self.inputs['Other junior weight'] =[]

	def parse_t31(self, row): #takes a row of tuples from a table 3-1 query and parses it to the inputs dictionary
		#parsing inputs for report 3.1
		#self.inputs will be used in the aggregation functions
		#note: sequence number did not exist prior to 2012 and HUD median income became FFIEC median income in 2012
		#instantiate classes to set loan variables
		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics

		a_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		co_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		#fill race lists from the demographics class
		a_race = demo.a_race_list(row) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.co_race_list(row) #put co-applicant race codes in a list 0-5, 0 is blank field
		#add data elements to dictionary
		self.inputs['a ethn'] = row['applicantethnicity'] #ethnicity of the applicant
		self.inputs['co ethn'] = row['coapplicantethnicity'] #ethnicity of the co-applicant
		self.inputs['income'] = row['applicantincome'] #relied upon income rounded to the nearest thousand
		self.inputs['purchaser'] = int(row['purchasertype']) -1 #adjust purchaser index down 1 to match JSON structure
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['census tract'] = row['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
		self.inputs['county code'] = row['countycode'] #3 digit county code
		self.inputs['county name'] = row['countyname'] #full text county name
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['minority percent'] = row['minoritypopulationpct'] #%of population that is minority
		self.inputs['tract to MSA income'] = row['tract_to_msa_md_income'] #ratio of tract to msa/md income
		self.inputs['sequence'] = row['sequencenumber'] #the sequence number of the loan, used for checking errors
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs) #sets the applicant income to an index number for aggregation
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs) #sets the applicant income as an index by an applicant's income as a percent of MSA median
		self.inputs['minority percent'] = MSA_index.minority_percent(self.inputs) #sets the minority population percent to an index for aggregation
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs) #sets the tract to msa income ratio to an index for aggregation (low, moderate, middle, upper)
		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['ethnicity'] = demo.set_loan_ethn(self.inputs) #requires  ethnicity be parsed prior to running set_loan_ethn
		self.inputs['race'] = demo.set_race(self.inputs, a_race, co_race) #requires joint status be set prior to running set_race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater

	def parse_t32(self, row): #takes a row of tuples from a table 3-1 query and parses it to the inputs dictionary
		#parsing inputs for report 3-1
		#self.inputs will be returned to for use in the aggregation function

		demo=demographics() #instantiate class to set loan variables

		#add data elements to dictionary
		self.inputs['rate spread'] = row['ratespread'] # interest rate spread over APOR if spread is greater than 1.5%
		self.inputs['lien status'] = row['lienstatus'] #first, junior, or not applicable
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['hoepa flag'] = int(row['hoepastatus']) #if the loan is subject to Home Ownership Equity Protection Act
		self.inputs['purchaser'] = int(row['purchasertype']) -1 #adjust purchaser index down 1 to match JSON
		self.inputs['year'] = row['asofdate'] #year of the loan
		self.inputs['state code'] = row['statecode'] #state abbreviation, 2 digits
		self.inputs['state name'] = row['statename'] #name of the state
		self.inputs['census tract'] = row['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
		self.inputs['county code'] = row['countycode'] #3 digit county code
		self.inputs['county name'] = row['countyname'] #full county name
		self.inputs['rate spread index'] = demo.rate_spread_index(self.inputs['rate spread']) #index of the rate spread for use in the JSON structure

	def parse_t4x(self, row):
		#parsing inputs for report 4-1
		#for key, value in row.iteritems():
		#	print key, value
		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics

		a_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		co_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		#fill race lists from the demographics class
		a_race = demo.a_race_list(row) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.co_race_list(row) #put co-applicant race codes in a list 0-5, 0 is blank field
		#add data elements to dictionary

		self.inputs['a ethn'] = row['applicantethnicity'] #ethnicity of the applicant
		self.inputs['co ethn'] = row['coapplicantethnicity'] #ethnicity of the co-applicant
		self.inputs['app sex'] = row['applicantsex']
		self.inputs['co app sex'] = row['coapplicantsex']
		self.inputs['income'] = row['applicantincome'] #relied upon income rounded to the nearest thousand
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['occupancy'] = row['occupancy']
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['census tract'] = row['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
		self.inputs['county code'] = row['countycode'] #3 digit county code
		self.inputs['county name'] = row['countyname'] #full text county name
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['action taken'] = int(row['actiontype']) #disposition of the loan application
		self.inputs['sequence'] = row['sequencenumber'] #the sequence number of the loan, used for checking errors
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs) #sets the applicant income as an index by an applicant's income as a percent of MSA median
		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['ethnicity'] = demo.set_loan_ethn(self.inputs) #requires  ethnicity be parsed prior to running set_loan_ethn
		self.inputs['race'] = demo.set_race(self.inputs, a_race, co_race) #requires joint status be set prior to running set_race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['gender'] = demo.set_gender(self.inputs)

class demographics(AD_report):
	#holds all the functions for setting race, minority status, and ethnicity for FFIEC A&D reports
	#this class is called when the parse_txx function is called by the controller
	def set_gender(self, inputs):
		male_flag = False
		female_flag = False

		if int(inputs['app sex']) > 2 and int(inputs['co app sex']) > 2: #if sex of neither applicant is reported
			return 3 #return out of bounds index

		if inputs['app sex'] == '1' or inputs['co app sex'] == '1':
			male_flag = True

		if inputs['app sex'] == '2' or inputs['co app sex'] == '2':
			female_flag = True

		if male_flag == True and female_flag == True:
			return 2 #joint male/female application/loan
		elif male_flag == True and female_flag == False:
			return 0 #male loan
		elif male_flag == False and female_flag == True:
			return 1 #female loan
		else:
			print "gender not set", inputs['app sex'], inputs['co app sex']
			print male_flag, female_flag

	def rate_spread_index(self, rate):
		#sets the rate spread variable to an index number for aggregation in the JSON object
		#indexes match the position on the report
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
		#if minority count is > 2, then the race is set to 2 minority
		minority_count = 0
		for race in a_race:
			if race < 5 and race > 0: #if a race was entered (not blank not a non-race category code, increment the minority count by 1 if the race was non-white)
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
		#determine minority status, this is a binary category
		#if either applicant reported a non-white race or an ethinicity of hispanic or latino then minority status is true
		if inputs['app non white flag'] == True or inputs['co non white flag'] == True or inputs['a ethn'] == '1' or inputs['co ethn'] == '1':
			return  1
		#if both applicants reported white race and non-hispanic/latino ethnicity then minority status is false
		elif inputs['app non white flag'] != True and inputs['co non white flag'] != True and inputs['a ethn']  != '1' and inputs['co ethn'] != '1':
			return 0
		else:
			print 'minority status not set'

	def set_loan_ethn(self, inputs):
		#this function outputs a number code for ethnicity: 0 - hispanic or latino, 1 - not hispanic/latino
		#2 - joint (1 applicant hispanic/latino 1 not), 3 - ethnicity not available
		#if both ethnicity fields are blank report not available(3)
		if inputs['a ethn'] == ' ' and inputs['co ethn'] == ' ':
			return  3 #set to not available
		#determine if the loan is joint hispanic/latino and non hispanic/latino(2)
		elif inputs['a ethn'] == '1' and inputs['co ethn'] == '2':
			return  2 #set to joint
		elif inputs['a ethn'] == '2' and inputs['co ethn'] == '1':
			return  2 #set to joint
		#determine if loan is of hispanic ethnicity (appplicant is hispanic/latino, no co applicant info or co applicant also hispanic/latino)
		elif inputs['a ethn'] == '1' and inputs['co ethn'] == '1': #both applicants hispanic
			return  0
		elif inputs['a ethn'] == '1' and (inputs['co ethn'] == ' ' or inputs['co ethn'] == '3' or inputs['co ethn'] == '4' or inputs['co ethn']== '5'): #applicant hispanic, co-applicant blank, not available or no co applicant
			return  0
		elif (inputs['a ethn'] == ' ' or inputs['a ethn'] == '3' or inputs['a ethn'] == '4' or inputs['a ethn'] == '5') and inputs['co ethn'] == '1': #co applicant hispanic, applicant blank, not available
			return  0
		#determine if loan is not hispanic or latino
		elif inputs['a ethn'] == '2' and inputs['co ethn'] != '1': #applicant not hispanic (positive entry), co applicant not hispanic (all other codes)
			return  1
		elif inputs['a ethn'] != '1' and inputs['co ethn'] == '2': #co applicant not hispanic (positive entry), applicant not hispanic (all other codes)
			return  1
		elif (inputs['a ethn'] == '3' or inputs['a ethn'] == '4') and (inputs['co ethn'] != '1' and inputs['co ethn'] != '2'): #no applicant ethnicity information, co applicant did not mark ethnicity positively
			return  3
		else:
			print "error setting ethnicity"

	def a_race_list(self, row):
		a_race = [race for race in row[1:6]] #filling the loan applicant race code lists (5 codes per applicant)
		for i in range(0, 5): #convert ' ' entries to 0 for easier comparisons and loan aggregation
			if a_race[i] == ' ':
				a_race[i] = 0
		return [int(race) for race in a_race] #convert string entries to int for easier comparison and loan aggregation

	def co_race_list(self, row):
		co_race = [race for race in row[6:11]] #filling the loan co-applicant race code lists (5 codes per applicant)
		for i in range(0,5):
			if co_race[i] == ' ':
				co_race[i] = 0
		return [int(race) for race in co_race] #convert string entries to int for easier comparison and loan aggregation

	def set_race(self, inputs, a_race, co_race): #sets the race to an integer index for loan aggregation
		#if one white and one minority race are listed, use the minority race
		#race options are: joint, 1 through 5, 2 minority, not reported
		if a_race[0] > 5 and a_race[1] == 0 and a_race[2] == 0 and a_race[3] == 0 and a_race[4] == 0:
			return 7 #race information not available
		elif inputs['joint status'] == True:
			return  6
		#if two minority races are listed, the loan is 'two or more minority races'
		#if any combination of two or more race fields are minority then 'two or more minority races'
		elif self.minority_count(a_race) > 1: #determine if the loan will be filed as 'two or more minority races'
			return  5

		elif a_race[0] != 0 and a_race[1] == 0 and a_race[2] == 0 and a_race[3] == 0 and a_race[4] == 0: #if only the first race field is used, use the first field unless it is blank
			return  a_race[0] #if only one race is reported, and joint status and minority status are false, set race to first race
		elif a_race[0] == 0 and a_race[1] == 0 and a_race[2] == 0 and a_race[3] == 0 and a_race[4] == 0:
			return  7 #if all race fields are blank, set to 7 'not available'
		else:
			for i in range(0,5):
				for r in range(0,5):
					if a_race[r] == i:
						return a_race[r] #return first instance of minority race
						break

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
		self.dispositions_list = ['Applications Received', 'Loans Originated', 'Apps. Approved But Not Accepted', 'Aplications Denied', 'Applications Withdrawn', 'Files Closed For Incompleteness']
		self.gender_list = ['Male', 'Female', 'Joint (Male/Female)']

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
			#aggregate needs to be variablalized


			path = 'json'+"/"+report_type+"/"+selector.report_list['year'][1]+"/"+self.state_names[state].replace(' ', '-').lower()
			print path #change this to a log file write
			if not os.path.exists(path): #check if path exists
				os.makedirs(path) #if path not present, create it
			#self.write_JSON(name, state_msas, path)
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
			return 'Disposition of applications to refinnace loans on 1- to 4- family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-4':
			return 'Disposition of applications for home improvement loans, 1- to 4- family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-5':
			return 'Disposition of applications for loans on dwellings for 5 or more families, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-6':
			return 'Disposition of applications from nonoccupants for home-purchase, home improvement, or refinancing loans, 1- to 4- family and manufactured home dwellings, by race, ethnicity, gender and income of applicant'
		elif table_num == '4-7':
			return 'Disposition of applications for home-purchase, home improvement, or refinancing loans, manufactured home dwellings by race, ethnicity, gender and income of applicant'

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
		self.container['report-date'] = "{:0>2d}".format(d)+'/'+"{:0>2d}".format(m)+'/'+"{:0>4d}".format(y)
		self.msa['id'] = MSA
		self.msa['name'] = self.msa_names[MSA]
		self.msa['state'] = inputs['state name'] #this is the two digit abbreviation
		self.msa['state_name'] = self.state_names[self.msa['state']]
		self.container['msa'] = self.msa
		return self.container

	def set_4x_dispositions(self, end_points): #builds the dispositions of applications section of report 4-1 JSON
		dispositions = []
		for item in self.dispositions_list:
			dispositionsholding = OrderedDict({})
			dispositionsholding['disposition'] = "{}".format(item)
			dispositions.append(dispositionsholding)
			for point in end_points:
				dispositionsholding[point] = 0
		return dispositions

	def set_4x_gender(self): #creates the gender portion of table 4-1 JSON
		genders = []
		for gender in self.gender_list:
			holding = OrderedDict({})
			holding['gender'] = "{}".format(gender)
			genders.append(holding)
		return genders

	def set_gender_disps(self):
		for i in range(0, len(self.race_names)):
			for g in range(0, len(self.gender_list)):
				self.container['races'][i]['genders'][g]['dispositions'] = self.set_4x_dispositions(['count', 'value'])
		for i in range(0, len(self.ethnicity_names)):
			for g in range(0, len(self.gender_list)):
				self.container['ethnicities'][i]['genders'][g]['dispositions'] = self.set_4x_dispositions(['count', 'value'])
		for i in range(0, len(self.minority_statuses)):
			for g in range(0, len(self.gender_list)):
				self.container['minoritystatuses'][i]['genders'][g]['dispositions'] = self.set_4x_dispositions(['count', 'value'])
	def set_4x_races(self):
		races = []
		for race in self.race_names:
			holding = OrderedDict({})
			holding['race'] = "{}".format(race)
			races.append(holding)
		self.container['races'] = races
		for i in range(0,len(self.container['races'])):
			self.container['races'][i]['dispositions'] = self.set_4x_dispositions(['count', 'value'])
			self.container['races'][i]['genders'] = self.set_4x_gender()

	def set_4x_ethnicity(self):
		ethnicities = []
		for ethnicity in self.ethnicity_names:
			holding = OrderedDict({})
			holding['ethnicity'] = "{}".format(ethnicity)
			ethnicities.append(holding)
		self.container['ethnicities'] = ethnicities
		for i in range(0, len(self.container['ethnicities'])):
			self.container['ethnicities'][i]['dispositions'] = self.set_4x_dispositions(['count', 'value'])
			self.container['ethnicities'][i]['genders'] = self.set_4x_gender()

	def set_4x_minority(self):
		minoritystatuses = []
		for status in self.minority_statuses:
			holding = OrderedDict({})
			holding['minoritystatus'] = "{}".format(status)
			minoritystatuses.append(holding)
		self.container['minoritystatuses'] = minoritystatuses
		for i in range(0, len(self.container['minoritystatuses'])):
			self.container['minoritystatuses'][i]['dispositions'] = self.set_4x_dispositions(['count', 'value'])
			self.container['minoritystatuses'][i]['genders'] = self.set_4x_gender()

	def set_4x_incomes(self):
		applicantincomes = []
		for income in self.applicant_income_bracket:
			holding = OrderedDict({})
			holding['income'] = "{}".format(income)
			applicantincomes.append(holding)
		self.container['incomes'] = applicantincomes
		for i in range(0, len(self.container['incomes'])):
			self.container['incomes'][i]['dispositions'] = self.set_4x_dispositions(['count', 'value'])
		self.container['total'] = self.set_4x_dispositions(['count', 'value'])

	def table_4x_builder(self): #builds the table 4-1 JSON object: disposition of application by race and gender
		self.set_4x_races()
		self.set_4x_ethnicity()
		self.set_4x_minority()
		self.set_4x_incomes()
		self.set_gender_disps()
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
				holding['purchasers'] = self.set_purchasers(['firstliencount', 'firstlienvalue', 'juniorliencount', 'juniorlienvalue'])
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
			holding['purchasers']  = self.set_purchasers(['firstliencount', 'firstlienvalue', 'juniorliencount', 'juniorlienvalue']) #purchasers is overwritten each pass in the holding dictionary
			pricinginformation.append(holding)
		self.container['pricinginformation'] = pricinginformation
		holding = OrderedDict({})
		points = self.build_rate_spreads()
		self.container['points'] = points
		hoepa = OrderedDict({})
		hoepa['pricing'] = 'hoepa loans'
		hoepa['purchasers'] = self.set_purchasers(['firstliencount', 'firstlienvalue', 'juniorliencount', 'juniorlienvalue'])
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



class connect_DB(AD_report): #connects to the SQL database
	#this is currently hosted locally
	def connect(self):
		with open('/Users/roellk/Desktop/python/credentials.txt', 'r') as f: #read in credentials file
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
		except: #if database connection results in an error print the following
			print "I am unable to connect to the database"
		return conn.cursor(cursor_factory=psycopg2.extras.DictCursor) #return a dictionary cursor object

class MSA_info(AD_report): #contains functions for setting aggregate information for the MSA

	def app_income_to_MSA(self, inputs): #set income bracket index
		if inputs['income'] == 'NA  ' or inputs['income'] == '    ':
			return 5 #applicant income unavailable, feeds to 'income not available'
		elif inputs['MSA median income'] == 'NA      ' or inputs['MSA median income'] == '        ' :
			return 6 #placeholder for MSA median income unavailable, feeds to 'income not available'
		else:
			inputs['percent MSA income'] = (float(inputs['income']) / (float(inputs['MSA median income'] )/1000)) *100 #common size median income and create ##.##% format ratio
			#determine income bracket for use as an index in the JSON object
			if inputs['percent MSA income'] < 50:
				return 0
			elif inputs['percent MSA income'] <= 80:
				return 1
			elif inputs['percent MSA income'] <= 100:
				return 2
			elif inputs['percent MSA income'] <= 120:
				return 3
			elif inputs['percent MSA income'] >= 120:
				return 4
			else:
				print 'error setting percent MSA income bracket for index'

	def minority_percent(self, inputs): #set index codes for minority population percent
		if inputs['minority percent'] == '      ' or inputs['minority percent'] == 'NA    ': #if no information is available use an out of bounds index
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

	def tract_to_MSA_income(self, inputs): #set census MSA income level: low, moderate, middle, upper
		if inputs['tract to MSA income'] == '      ' or inputs['tract to MSA income'] == 'NA    ': #if no information is available use an out of bounds index
			return 4 #not stored in report 3-1
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

class queries(AD_report):
	#can I decompose these query parts into lists and concatenate them prior to passing to the cursor?
	#need to standardize field names in order to use the same query across eyars
		#ffiec_median_family_income vs HUD_median_family_income
		#no sequencenumber prior to 2012
	def count_rows_2012(self): #get the count of rows in the LAR for an MSA, used to run the parsing/aggregation loop
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s;'''
		return SQL

	def count_rows_2013(self): #get the count of rows in the LAR for an MSA, used to run the parsing/aggregation loop
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s;'''
		return SQL

	def count_rows_41_2012(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s and (loantype = '2' or loantype = '3' or loantype = '4')
			and propertytype !='3' and loanpurpose = '1' ;'''
		return SQL

	def count_rows_41_2013(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s and (loantype = '2' or loantype = '3' or loantype = '4')
			and propertytype !='3' and loanpurpose = '1' ;'''
		return SQL

	def count_rows_42_2012(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s and loantype = '1'
			and propertytype !='3' and loanpurpose = '1' ;'''
		return SQL

	def count_rows_42_2013(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s and loantype = '1'
			and propertytype !='3' and loanpurpose = '1' ;'''
		return SQL

	def count_rows_43_2012(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s
			and propertytype !='3' and loanpurpose = '3' ;'''
		return SQL

	def count_rows_43_2013(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s
			and propertytype !='3' and loanpurpose = '3' ;'''
		return SQL

	def count_rows_44_2012(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s
			and propertytype !='3' and loanpurpose = '2' ;'''
		return SQL

	def count_rows_44_2013(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s
			and propertytype !='3' and loanpurpose = '2' ;'''
		return SQL

	def count_rows_45_2012(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s
			and propertytype ='3';'''
		return SQL

	def count_rows_45_2013(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s
			and propertytype ='3';'''
		return SQL

	def count_rows_46_2012(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s
			and propertytype !='3' and occupancy = '2';'''
		return SQL

	def count_rows_46_2013(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s
			and propertytype !='3' and occupancy = '2';'''
		return SQL

	def count_rows_47_2012(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s
			and propertytype ='2';'''
		return SQL

	def count_rows_47_2013(self):
		SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s
			and propertytype ='2' ;'''
		return SQL

	def table_3_1_2013(self): #set the SQL statement to select the needed fields to aggregate loans for the table_3 JSON structure
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, hoepastatus,
			purchasertype, loanamount, asofdate, statecode, statename, countycode, countyname,
			ffiec_median_family_income, minoritypopulationpct, tract_to_msa_md_income, sequencenumber
			FROM hmdapub2013 WHERE msaofproperty = %s;'''
		return SQL

	def table_3_1_2012(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, hoepastatus,
			purchasertype, loanamount, asofdate, statecode, statename, countycode, countyname,
			ffiec_median_family_income, minoritypopulationpct, tract_to_msa_md_income, sequencenumber
			FROM hmdapub2012 WHERE msaofproperty = %s;'''
		return SQL

	def table_3_2_2012(self):
		SQL = '''SELECT
			censustractnumber,  ratespread, lienstatus, loanamount, hoepastatus,
			purchasertype, asofdate, statecode, statename, countycode, countyname
			FROM hmdapub2012 WHERE msaofproperty = %s;'''
		return SQL

	def table_3_2_2013(self): #set the SQL statement to select the needed fields to aggregate loans for the table_3 JSON structure
		SQL = '''SELECT
			censustractnumber,  ratespread, lienstatus, loanamount, hoepastatus,
			purchasertype, asofdate, statecode, statename, countycode, countyname
			FROM hmdapub2013 WHERE msaofproperty = %s;'''
		return SQL

	def table_4_1_2012(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2012 WHERE msaofproperty = %s and (loantype = '2' or loantype = '3' or loantype = '4')
			and propertytype !='3' and loanpurpose = '1' ;'''
		return SQL

	def table_4_1_2013(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2013 WHERE msaofproperty = %s and (loantype = '2' or loantype = '3' or loantype = '4')
			and propertytype !='3' and loanpurpose = '1' ;'''
		return SQL

	def table_4_2_2012(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2012 WHERE msaofproperty = %s and loantype = '1' and propertytype !='3' and loanpurpose = '1' ;'''
		return SQL

	def table_4_2_2013(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2013 WHERE msaofproperty = %s and loantype = '1' and propertytype !='3' and loanpurpose = '1' ;'''
		return SQL

	def table_4_3_2012(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2012 WHERE msaofproperty = %s and propertytype !='3' and loanpurpose = '3' ;'''
		return SQL

	def table_4_3_2013(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2013 WHERE msaofproperty = %s and propertytype !='3' and loanpurpose = '3' ;'''
		return SQL

	def table_4_4_2012(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2012 WHERE msaofproperty = %s and propertytype !='3' and loanpurpose = '2' ;'''
		return SQL

	def table_4_4_2013(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2013 WHERE msaofproperty = %s and propertytype !='3' and loanpurpose = '2' ;'''
		return SQL

	def table_4_5_2012(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2012 WHERE msaofproperty = %s and propertytype ='3';'''
		return SQL

	def table_4_5_2013(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2013 WHERE msaofproperty = %s and propertytype ='3';'''
		return SQL

	def table_4_6_2012(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2012 WHERE msaofproperty = %s and occupancy = '2' and propertytype !='3';'''
		return SQL

	def table_4_6_2013(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2013 WHERE msaofproperty = %s and occupancy = '2' and propertytype !='3';'''
		return SQL

	def table_4_7_2012(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2012 WHERE msaofproperty = %s and propertytype ='2';'''
		return SQL

	def table_4_7_2013(self):
		SQL = '''SELECT
			censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy
			FROM hmdapub2013 WHERE msaofproperty = %s and propertytype ='2';'''
		return SQL


class aggregate(AD_report): #aggregates LAR rows by appropriate characteristics to fill the JSON files

	def __init__(self):
		self.purchaser_first_lien_rates = ['Fannie Mae first rates', 'Ginnie Mae first rates', 'Freddie Mac first rates', 'Farmer Mac first rates', 'Private Securitization first rates', 'Commercial bank, savings bank or association first rates', 'Life insurance co., credit union, finance co. first rates', 'Affiliate institution first rates', 'Other first rates']
		self.purchaser_junior_lien_rates = ['Fannie Mae junior rates', 'Ginnie Mae junior rates', 'Freddie Mac junior rates', 'Farmer Mac junior rates', 'Private Securitization junior rates', 'Commercial bank, savings bank or association junior rates', 'Life insurance co., credit union, finance co. junior rates', 'Affiliate institution junior rates', 'Other junior rates']
		self.purchaser_first_lien_weight = ['Fannie Mae first weight', 'Ginnie Mae first weight', 'Freddie Mac first weight', 'Farmer Mac first weight', 'Private Securitization first weight', 'Commercial bank, savings bank or association first weight', 'Life insurance co., credit union, finance co. first weight', 'Affiliate institution first weight', 'Other first weight']
		self.purchaser_junior_lien_weight = ['Fannie Mae junior weight', 'Ginnie Mae junior weight', 'Freddie Mac junior weight', 'Farmer Mac junior weight', 'Private Securitization junior weight', 'Commercial bank, savings bank or association junior weight', 'Life insurance co., credit union, finance co. junior weight', 'Affiliate institution junior weight', 'Other junior weight']

	def by_race(self, container, inputs): #aggregates loans by race category
		#if inputs['race'] == 5 and inputs['purchaser'] == 0:
		#	print inputs['sequence'], inputs['loan value'], "fannie mae 2 minority"
		#if inputs['race'] == 6 and inputs['purchaser'] == 0:
		#	print inputs['sequence'], inputs['loan value'], "fannie mae joint"
		container['borrowercharacteristics'][0]['races'][inputs['race']]['purchasers'][inputs['purchaser']]['count'] += 1
		container['borrowercharacteristics'][0]['races'][inputs['race']]['purchasers'][inputs['purchaser']]['value'] += inputs['loan value']

	def by_ethnicity(self, container, inputs): #aggregate loans by enthicity status
		container['borrowercharacteristics'][1]['ethnicities'][inputs['ethnicity']]['purchasers'][inputs['purchaser']]['count'] += 1
		container['borrowercharacteristics'][1]['ethnicities'][inputs['ethnicity']]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def by_minority_status(self, container, inputs): #aggregate loans by minority status
		container['borrowercharacteristics'][2]['minoritystatuses'][inputs['minority status']]['purchasers'][inputs['purchaser']]['count'] += 1
		container['borrowercharacteristics'][2]['minoritystatuses'][inputs['minority status']]['purchasers'][inputs['purchaser']]['value']+= int(inputs['loan value'])

	def by_applicant_income(self, container, inputs): #aggregate loans by applicant income index
		if inputs['income bracket'] > 5: #income index outside bounds of report 3-1
			pass
		else:
			container['borrowercharacteristics'][3]['applicantincomes'][inputs['income bracket']]['purchasers'][inputs['purchaser']]['count'] += 1
			container['borrowercharacteristics'][3]['applicantincomes'][inputs['income bracket']]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def by_minority_composition(self, container, inputs): #aggregate loans by MSA minority population percent
		if inputs['minority percent'] == 4: #minority percent not available
			pass
		else:
			container['censuscharacteristics'][0]['tractpctminorities'][inputs['minority percent']]['purchasers'][inputs['purchaser']]['count'] += 1
			container['censuscharacteristics'][0]['tractpctminorities'][inputs['minority percent']]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def by_tract_income(self, container, inputs): #aggregate loans by tract to MSA income ratio
		if inputs['tract income index'] > 3: #income ratio not available or outside report 3-1 bounds
			pass
		else:
			container['censuscharacteristics'][1]['incomelevels'][inputs['tract income index']]['purchasers'][inputs['purchaser']]['count'] +=1
			container['censuscharacteristics'][1]['incomelevels'][inputs['tract income index']]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def totals(self, container, inputs): #aggregate total of purchased loans
		container['total']['purchasers'][inputs['purchaser']]['count'] +=1
		container['total']['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def by_pricing_status(self, container, inputs): #aggregate loans by lien status
		#index 8 is for loans with no reported pricing information
		if inputs['rate spread index'] == 8 and inputs['lien status'] == '1':
			container['pricinginformation'][0]['purchasers'][inputs['purchaser']]['firstliencount'] +=1
			container['pricinginformation'][0]['purchasers'][inputs['purchaser']]['firstlienvalue'] += int(inputs['loan value'])
		elif inputs['rate spread index'] == 8 and inputs['lien status'] == '2':
			container['pricinginformation'][0]['purchasers'][inputs['purchaser']]['juniorliencount'] +=1
			container['pricinginformation'][0]['purchasers'][inputs['purchaser']]['juniorlienvalue'] += int(inputs['loan value'])
		else: #if loan has pricing information aggregate by index
			if inputs['rate spread index'] < 8 and inputs['lien status'] == '1' :
				container['pricinginformation'][1]['purchasers'][inputs['purchaser']]['firstliencount'] +=1
				container['pricinginformation'][1]['purchasers'][inputs['purchaser']]['firstlienvalue'] += int(inputs['loan value'])
			elif  inputs['rate spread index'] < 8 and inputs['lien status'] == '2':
				container['pricinginformation'][1]['purchasers'][inputs['purchaser']]['juniorliencount'] += 1
				container['pricinginformation'][1]['purchasers'][inputs['purchaser']]['juniorlienvalue'] += int(inputs['loan value'])

	def by_rate_spread(self, container, inputs): #aggregate loans by rate spread index
		if inputs['lien status'] == '1' and inputs['rate spread index'] < 8: #aggregate first lien status loans
			if container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['firstliencount'] == 'NA':
				container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['firstliencount'] =0
				container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['firstlienvalue'] =0
			container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['firstliencount'] +=1
			container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['firstlienvalue'] += int(inputs['loan value'])

		elif inputs['lien status'] == '2' and inputs['rate spread index'] <8: #aggregate subordinate lien status loans
			if container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['juniorliencount'] == 'NA':
				container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['juniorliencount'] =0
				container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['juniorlienvalue'] =0
			container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['juniorliencount'] +=1
			container['points'][inputs['rate spread index']]['purchasers'][inputs['purchaser']]['juniorlienvalue'] += int(inputs['loan value'])

	def by_hoepa_status(self, container, inputs): #aggregate loans subject to HOEPA
		if inputs['hoepa flag'] == 1:
			if inputs['lien status'] == '1': #first lien HOEPA
				container['hoepa']['purchasers'][inputs['purchaser']]['firstliencount'] +=1
				container['hoepa']['purchasers'][inputs['purchaser']]['firstlienvalue'] +=int(inputs['loan value'])
			elif inputs['lien status'] == '2': #junior lien HOEPA
				container['hoepa']['purchasers'][inputs['purchaser']]['juniorliencount'] +=1
				container['hoepa']['purchasers'][inputs['purchaser']]['juniorlienvalue'] +=int(inputs['loan value'])
			elif inputs['lien status'] == '3':
				pass #this space reserved for loans not secured by liens
			elif inputs['lien status'] == '4':
				pass #this space reserved for purchased loans 'not applicable'
			else:
				print "invalid hoepa flag, oops"

		elif inputs['hoepa flag'] == 2:
			pass #the reports do not aggregate non-HOEPA loans in this section
		else:
			print "HOEPA flag not present or outside parameters" #error message to be displayed if a loan falls outside logic parameters

	def by_mean(self, container, inputs): #aggregate loans by mean of rate spread
		#first_lien_purchasers = ['Fannie Mae first rates', 'Ginnie Mae first rates', 'Freddie Mac first rates', 'Farmer Mac first rates', 'Private Securitization first rates', 'Commercial bank, savings bank or association first rates', 'Life insurance co., credit union, finance co. first rates', 'Affiliate institution first rates', 'Other first rates']
		#junior_lien_purchasers = ['Fannie Mae junior rates', 'Ginnie Mae junior rates', 'Freddie Mac junior rates', 'Farmer Mac junior rates', 'Private Securitization junior rates', 'Commercial bank, savings bank or association junior rates', 'Life insurance co., credit union, finance co. junior rates', 'Affiliate institution junior rates', 'Other junior rates']
		for n in range(0,9):
			if float(container['pricinginformation'][1]['purchasers'][n]['firstliencount']) > 0 and inputs[self.purchaser_first_lien_rates[n]] > 0: #bug fix for divide by 0 errors
				#container['points'][8]['purchasers'][n]['first lien'] = 0
				container['points'][8]['purchasers'][n]['firstliencount'] = round(numpy.mean(numpy.array(inputs[self.purchaser_first_lien_rates[n]])),2)#round(self.inputs[first_lien_rates[n]]/float(container['pricinginformation'][1]['purchasers'][n]['firstliencount']),2)

			if float(container['pricinginformation'][1]['purchasers'][n]['juniorliencount']) > 0 and inputs[self.purchaser_junior_lien_rates[n]] > 0: #bug fix for divide by 0 errors
				#container['points'][8]['purchasers'][n]['junior lien'] = 0
				#print inputs[self.purchaser_junior_lien_rates[n]], "junior lien rates"
				container['points'][8]['purchasers'][n]['juniorliencount'] = round(numpy.mean(numpy.array(inputs[self.purchaser_junior_lien_rates[n]])),2)#round(inputs[self.junior_lien_rates[n]]/float(container['pricinginformation'][1]['purchasers'][n]['juniorliencount']),2)

	def by_weighted_mean(self, container, inputs): #aggregate loans by weighted mean of rate spread
		#first_lien_purchasers = ['Fannie Mae first weight', 'Ginnie Mae first weight', 'Freddie Mac first weight', 'Farmer Mac first weight', 'Private Securitization first weight', 'Commercial bank, savings bank or association first weight', 'Life insurance co., credit union, finance co. first weight', 'Affiliate institution first weight', 'Other first weight']
		#junior_lien_purchasers = ['Fannie Mae junior weight', 'Ginnie Mae junior weight', 'Freddie Mac junior weight', 'Farmer Mac junior weight', 'Private Securitization junior weight', 'Commercial bank, savings bank or association junior weight', 'Life insurance co., credit union, finance co. junior weight', 'Affiliate institution junior weight', 'Other junior weight']
		for n in range(0,9):
			if float(container['pricinginformation'][1]['purchasers'][n]['firstliencount']) > 0 and inputs[self.purchaser_first_lien_weight[n]] > 0: #bug fix for divide by 0 errors
				nd_first_rates = numpy.array(inputs[self.purchaser_first_lien_rates[n]])
				nd_first_weights = numpy.array(inputs[self.purchaser_first_lien_weight[n]])
				#print nd_first_rates
				#print nd_first_weights
				container['points'][8]['purchasers'][n]['firstlienvalue'] = round(numpy.average(nd_first_rates, weights=nd_first_weights),2)#round(inputs[self.purchaser_first_lien_weight[n]]/float(container['pricinginformation'][1]['purchasers'][n]['firstlienvalue']),2)

			if float(container['pricinginformation'][1]['purchasers'][n]['juniorliencount']) > 0 and inputs[self.purchaser_junior_lien_weight[n]] > 0: #bug fix for divide by 0 errors
				nd_junior_rates = numpy.array(inputs[self.purchaser_junior_lien_rates[n]])
				nd_junior_weights = numpy.array(inputs[self.purchaser_junior_lien_rates[n]])
				container['points'][8]['purchasers'][n]['juniorlienvalue'] = round(numpy.average(nd_junior_rates, weights=nd_junior_weights),2)#round(inputs[self.purchaser_junior_lien_weight[n]]/float(container['pricinginformation'][1]['purchasers'][n]['juniorlienvalue']),2)

	def fill_weight_lists(self, inputs): #add all loan values to a list to find means and medians
		if inputs['rate spread'] != 'NA   ' and inputs['rate spread'] != '     ':

			if inputs['lien status'] =='1':
				inputs[self.purchaser_first_lien_weight[inputs['purchaser']]].append(int(inputs['loan value']))
			elif inputs['lien status'] == '2':
				inputs[self.purchaser_junior_lien_weight[inputs['purchaser']]].append(int(inputs['loan value']))

	def fill_rate_lists(self, inputs): #add all rate spreads to a list to find the mean and median rate spreads
		#purchaser_first_lien_rates = ['Fannie Mae first lien list', 'Ginnie Mae first lien list', 'Freddie Mac first lien list', 'Farmer Mac first lien list', 'Private Securitization first lien list', 'Commercial bank, savings bank or association first lien list', 'Life insurance co., credit union, finance co. first lien list', 'Affiliate institution first lien list', 'Other first lien list']
		#purchaser_junior_lien_rates = ['Fannie Mae junior lien list', 'Ginnie Mae junior lien list', 'Freddie Mac junior lien list', 'Farmer Mac junior lien list', 'Private Securitization junior lien list', 'Commercial bank, savings bank or association junior lien list', 'Life insurance co., credit union, finance co. junior lien list', 'Affiliate institution junior lien list', 'Other junior lien list']
		if inputs['rate spread'] == 'NA   ' or inputs['rate spread'] == '     ':
			pass
		elif inputs['lien status'] == '1': #add to first lien rate spread list
			inputs[self.purchaser_first_lien_rates[inputs['purchaser']]].append(float(inputs['rate spread']))
		elif inputs['lien status'] == '2': #add to junior lien rate spread list
			inputs[self.purchaser_junior_lien_rates[inputs['purchaser']]].append(float(inputs['rate spread']))

	def by_median(self, container, inputs): #puts the median rate spread in the JSON object
		#purchaser_first_lien_rates = ['Fannie Mae first lien list', 'Ginnie Mae first lien list', 'Freddie Mac first lien list', 'Farmer Mac first lien list', 'Private Securitization first lien list', 'Commercial bank, savings bank or association first lien list', 'Life insurance co., credit union, finance co. first lien list', 'Affiliate institution first lien list', 'Other first lien list']
		#purchaser_junior_lien_rates = ['Fannie Mae junior lien list', 'Ginnie Mae junior lien list', 'Freddie Mac junior lien list', 'Farmer Mac junior lien list', 'Private Securitization junior lien list', 'Commercial bank, savings bank or association junior lien list', 'Life insurance co., credit union, finance co. junior lien list', 'Affiliate institution junior lien list', 'Other junior lien list']
		for n in range(0,9):
			#first lien median block
			if len(inputs[self.purchaser_first_lien_rates[n]]) > 0: #check to see if the array is populated
				container['points'][9]['purchasers'][n]['firstliencount'] = round(numpy.median(numpy.array(inputs[self.purchaser_first_lien_rates[n]])),2) #for normal median
				#container['points'][9]['purchasers'][n]['firstlienvalue'] = round(numpy.median(numpy.array(inputs[purchaser_first_lien_rates[n]])),2) #for weighted median
			#junior lien median block
			if len(inputs[self.purchaser_junior_lien_rates[n]]) > 0: #check to see if the array is populated
				container['points'][9]['purchasers'][n]['juniorliencount'] = round(numpy.median(numpy.array(inputs[self.purchaser_junior_lien_rates[n]])),2) #for normal median
				#container['points'][9]['purchasers'][n]['juniorlienvalue'] = round(numpy.median(numpy.array(inputs[purchaser_junior_lien_rates[n]])),2) #for weighted median
	def by_weighted_median(self, container, inputs):
		for n in range(0,9):
			#first lien weighted median block
			#print inputs[self.purchaser_first_lien_rates[n]], inputs[self.purchaser_first_lien_weight[n]]
			if len(inputs[self.purchaser_first_lien_rates[n]]) >0 and len(inputs[self.purchaser_first_lien_weight[n]]) >0: #check to see if the array is populated
				nd_first_rates = numpy.array(inputs[self.purchaser_first_lien_rates[n]]) #set arrays to nparrays
				nd_first_values = numpy.array(inputs[self.purchaser_first_lien_weight[n]])
				container['points'][9]['purchasers'][n]['firstlienvalue'] = round(weighted.median(nd_first_rates, nd_first_values),2) #for weighted median
			#junior lien weighted median block
			#print self.purchaser_junior_lien_rates[n], inputs[self.purchaser_junior_lien_rates[n]]
			#print self.purchaser_junior_lien_weight[n], inputs[self.purchaser_junior_lien_weight[n]]
			if len(inputs[self.purchaser_junior_lien_rates[n]]) > 0 and len(inputs[self.purchaser_junior_lien_weight[n]]) >0: #check to see if the array is populated
				nd_junior_rates = numpy.array(inputs[self.purchaser_junior_lien_rates[n]]) #set array to numpy array
				nd_junior_values = numpy.array(inputs[self.purchaser_junior_lien_weight[n]]) #set arry to numpy array
				container['points'][9]['purchasers'][n]['juniorlienvalue'] = round(weighted.median(nd_junior_rates, nd_junior_values),2)
	def by_applicant_income_4x(self, container, inputs): #aggregate loans by applicant income index
		if inputs['income bracket'] > 5 or inputs['action taken'] == ' ' or inputs['action taken'] > 5: #filter out of bounds indexes before calling aggregations
			pass

		elif inputs['income bracket'] <6 and inputs['action taken'] < 6:
			container['incomes'][inputs['income bracket']]['dispositions'][0]['count'] += 1 #add to 'applications received'
			container['incomes'][inputs['income bracket']]['dispositions'][0]['value'] += int(inputs['loan value']) #add to 'applications received'

			container['incomes'][inputs['income bracket']]['dispositions'][inputs['action taken']]['count'] += 1 #loans by action taken code
			container['incomes'][inputs['income bracket']]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])
		else:
			print "error aggregating income for report 4-1"

	def by_race_4x(self, container, inputs):
		if inputs['action taken'] >5:
			pass
		else:

			container['races'][inputs['race']]['dispositions'][0]['count'] += 1 #count of total applications received
			container['races'][inputs['race']]['dispositions'][0]['value'] += int(inputs['loan value'])

			container['races'][inputs['race']]['dispositions'][inputs['action taken']]['count'] += 1
			container['races'][inputs['race']]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])

			if inputs['gender'] < 3:
				container['races'][inputs['race']]['genders'][inputs['gender']]['dispositions'][0]['count'] += 1 #count of total applications received for each gender
				container['races'][inputs['race']]['genders'][inputs['gender']]['dispositions'][0]['value'] += int(inputs['loan value'])

				container['races'][inputs['race']]['genders'][inputs['gender']]['dispositions'][inputs['action taken']]['count'] += 1
				container['races'][inputs['race']]['genders'][inputs['gender']]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def by_ethnicity_4x(self, container, inputs):
		if inputs['action taken'] >5:
			pass
		else:
			container['ethnicities'][inputs['ethnicity']]['dispositions'][0]['count'] += 1 #count of total applications received
			container['ethnicities'][inputs['ethnicity']]['dispositions'][0]['value'] += int(inputs['loan value'])

			container['ethnicities'][inputs['ethnicity']]['dispositions'][inputs['action taken']]['count'] += 1
			container['ethnicities'][inputs['ethnicity']]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])

			if inputs['gender'] < 3:
				container['ethnicities'][inputs['ethnicity']]['genders'][inputs['gender']]['dispositions'][0]['count'] +=1 #count of all applications (all dispositions)
				container['ethnicities'][inputs['ethnicity']]['genders'][inputs['gender']]['dispositions'][0]['value'] +=1
				container['ethnicities'][inputs['ethnicity']]['genders'][inputs['gender']]['dispositions'][inputs['action taken']]['count'] += 1
				container['ethnicities'][inputs['ethnicity']]['genders'][inputs['gender']]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def by_minority_status_4x(self, container, inputs):

		if inputs['minority status'] > 2 or inputs['action taken'] > 5:
			pass
		else:
			container['minoritystatuses'][inputs['minority status']]['dispositions'][0]['count'] +=1 #count of total applications received by minority status
			container['minoritystatuses'][inputs['minority status']]['dispositions'][0]['value'] +=int(inputs['loan value']) #value of total applications received by minority status

			container['minoritystatuses'][inputs['minority status']]['dispositions'][inputs['action taken']]['count'] +=1 #totals of each minority status by disposition of application
			container['minoritystatuses'][inputs['minority status']]['dispositions'][inputs['action taken']]['value'] +=int(inputs['loan value']) #totals of each gender for each minority status

			if inputs['gender'] < 3:
				container['minoritystatuses'][inputs['minority status']]['genders'][inputs['gender']]['dispositions'][0]['count'] +=1 #total for all application dispositions by minority status and gender
				container['minoritystatuses'][inputs['minority status']]['genders'][inputs['gender']]['dispositions'][0]['count'] +=int(inputs['loan value'])
				container['minoritystatuses'][inputs['minority status']]['genders'][inputs['gender']]['dispositions'][inputs['action taken']]['count'] +=1 #totals of each gender for each minority status
				container['minoritystatuses'][inputs['minority status']]['genders'][inputs['gender']]['dispositions'][inputs['action taken']]['value'] +=int(inputs['loan value']) #totals of each gender for each minority status

	def totals_4x(self, container, inputs):
		if inputs['action taken'] < 6 and inputs['action taken'] != ' ':
			container['total'][0]['count'] += 1
			container['total'][0]['value'] += int(inputs['loan value'])
			container['total'][inputs['action taken']]['count'] +=1
			container['total'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def build_report4x(self, table4x, inputs): #call functions to fill JSON object for table 4-1 (FHA, FSA, RHS, and VA home purchase loans)
		self.by_race_4x(table4x, inputs) #aggregate loans by race, gender, and applicaiton disposition
		self.by_ethnicity_4x(table4x, inputs)#aggregate loans by ethnicity, gender, and applicaiton disposition
		self.by_minority_status_4x(table4x, inputs)#aggregate loans by minority status, gender, and applicaiton disposition
		self.by_applicant_income_4x(table4x, inputs) #aggregate loans by applicant income to MSA income ratio
		self.totals_4x(table4x, inputs) #totals of applications by application disposition

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
		self.fill_rate_lists(inputs)
		self.fill_weight_lists(inputs) #fills the median rate spread for each purchaser
		#mean and median functions are not called here
		#mean and median function must be called outside the control loop
		return table32




