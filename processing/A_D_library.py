#this file holds the classes used to create the A&D reports using the HMDA LAR files combined with Census demographic information
from decimal import Decimal
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
		self.inputs['a_race'] = a_race
		self.inputs['co_race'] = co_race
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
		self.inputs['minority percent index'] = MSA_index.minority_percent(self.inputs) #sets the minority population percent to an index for aggregation

		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['race'] = demo.set_race(self.inputs, a_race) #requires joint status be set prior to running set_race
		self.inputs['ethnicity'] = demo.set_loan_ethn(self.inputs) #requires  ethnicity be parsed prior to running set_loan_ethn
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status


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
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['race'] = demo.set_race(self.inputs, a_race) #requires joint status be set prior to running set_race
		self.inputs['ethnicity'] = demo.set_loan_ethn(self.inputs) #requires  ethnicity be parsed prior to running set_loan_ethn
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['gender'] = demo.set_gender(self.inputs)
		if self.inputs['race'] == 1:
			print a_race, co_race, self.inputs['race'], self.inputs['ethnicity'], self.inputs['gender'], self.inputs['sequence'], self.inputs['loan value'], self.inputs['app non white flag'], self.inputs['co non white flag']
	def parse_t5x(self, row):

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
		self.inputs['a_race'] = a_race
		self.inputs['co_race'] = co_race
		self.inputs['a ethn'] = row['applicantethnicity'] #ethnicity of the applicant
		self.inputs['co ethn'] = row['coapplicantethnicity'] #ethnicity of the co-applicant
		self.inputs['income'] = row['applicantincome'] #relied upon income rounded to the nearest thousand
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['action taken'] = int(row['actiontype']) #disposition of the loan application
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['sequence'] = row['sequencenumber'] #the sequence number of the loan, used for checking errors
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs) #sets the applicant income as an index by an applicant's income as a percent of MSA median
		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['race'] = demo.set_race(self.inputs, a_race) #requires joint status be set prior to running set_race
		if self.inputs['race'] == 7:
			#print 'using co race', self.inputs['race']
			demo.set_race(self.inputs, co_race)
			#print self.inputs['race']
		self.inputs['ethnicity'] = demo.set_loan_ethn(self.inputs) #requires  ethnicity be parsed prior to running set_loan_ethn
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status

	def parse_t7x(self, row):
		MSA_index = MSA_info() #contains functions for census tract characteristics

		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['action taken'] = int(row['actiontype']) #disposition of the loan application
		self.inputs['minority percent'] = row['minoritypopulationpct'] #%of population that is minority
		self.inputs['minority percent index'] = MSA_index.minority_percent(self.inputs) #sets the minority population percent to an index for aggregation
		self.inputs['tract to MSA income'] = row['tract_to_msa_md_income'] #ratio of tract to msa/md income
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs) #sets the tract to msa income ratio to an index for aggregation (low, middle, moderate,  high

	def parse_t8x(self, row): #takes a row of tuples from a table 3-1 query and parses it to the inputs dictionary

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
		self.inputs['a_race'] = a_race
		self.inputs['co_race'] = co_race
		self.inputs['a ethn'] = row['applicantethnicity'] #ethnicity of the applicant
		self.inputs['co ethn'] = row['coapplicantethnicity'] #ethnicity of the co-applicant
		self.inputs['app sex'] = row['applicantsex']
		self.inputs['co app sex'] = row['coapplicantsex']
		self.inputs['income'] = row['applicantincome'] #relied upon income rounded to the nearest thousand
		self.inputs['denial reason1'] = self.adjust_denial_index(row['denialreason1'])
		self.inputs['denial reason2'] = self.adjust_denial_index(row['denialreason2'])
		self.inputs['denial reason3'] = self.adjust_denial_index(row['denialreason3'])
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['census tract'] = row['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
		self.inputs['county code'] = row['countycode'] #3 digit county code
		self.inputs['county name'] = row['countyname'] #full text county name
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs) #sets the applicant income as an index by an applicant's income as a percent of MSA median
		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['race'] = demo.set_race(self.inputs, a_race) #requires joint status be set prior to running set_race
		self.inputs['ethnicity'] = demo.set_loan_ethn(self.inputs) #requires  ethnicity be parsed prior to running set_loan_ethn
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['gender'] = demo.set_gender(self.inputs)
		self.inputs['denial_list'] = self.denial_reasons_list(self.inputs['denial reason1'], self.inputs['denial reason2'], self.inputs['denial reason3'])

	def adjust_denial_index(self, reason):
		if reason != ' ':
			return int(reason) - 1

	def denial_reasons_list(self, reason1, reason2, reason3):
		denial_list = []
		denial_list.append(reason1)
		denial_list.append(reason2)
		denial_list.append(reason3)
		return denial_list

	def parse_t9x(self, row):
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['census tract'] = row['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
		self.inputs['action taken'] = int(row['actiontype']) #disposition of the loan application
		self.inputs['property type'] = row['propertytype']
		self.inputs['loan purpose'] = row['loan purpose']
		self.inputs['loan type'] = row['loantype']



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
		if inputs['minority percent'] == '      ':#if no information is available use an out of bounds index
			return  5
		elif inputs['minority percent'] == 'NA    ': #if tract minority percent is NA then it is aggregated as <10%
			return 0
		elif float(inputs['minority percent']) < 10.0: #less than 10%
			return  0
		elif float(inputs['minority percent']) <20.0: # 10-19%
			return 1
		elif float(inputs['minority percent'])  < 50.0: # 20-49%
			return  2
		elif float(inputs['minority percent'])  < 80.0: # 50-79
			return  3
		elif float(inputs['minority percent'])  <= 100.0: # 80-100
			return  4
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

class demographics(AD_report):
	#holds all the functions for setting race, minority status, and ethnicity for FFIEC A&D reports
	#this class is called when the parse_txx function is called by the controller
	def __init__(self):
		pass
	def set_gender(self, inputs):
		male_flag = False
		female_flag = False

		if int(inputs['app sex']) >= 3:# int(inputs['co app sex']) >= 3: #if sex of neither applicant is reported
			return 3 #gender not available (used in report 8-x)

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
		#non_white = False
		'''
		for i in range(0,5):
			if race_list[i] < 5 and race_list[i] != 0:
				return True #flag true if applicant listed a minority race
		#needs a section that sets to false if all race codes are 0 or 5
		for i in range(0, 5):
			if race_list[i] == 5
		'''
		for i in range(1, 5):
			#print race_list, i in race_list
			if i in race_list:
				return True
		if 5 in race_list:
			return False

	def set_joint(self, inputs): #takes a dictionary 'inputs' which is held in the controller(?) object and used to process each loan row
		#set default return to true or false and then only run 1 check
		#joint status exists if one borrower is white and one is non-white
		#check to see if joint status exists
		#inputs['joint status'] = False
		#if inputs['app non white flag'] == False and inputs['co non white flag'] == False:
		#	return False #flag false if both applicant and co-applicant are white
		#elif inputs['app non white flag'] == True and inputs['co non white flag'] == True:
		#	return False #flag false if both applicant and co-applicant are minority
		if inputs['app non white flag'] == True and inputs['co non white flag'] ==  False:
			return True #flag true if one applicant is minority and one is white
		elif inputs['app non white flag'] == False and inputs['co non white flag'] == True:
			return True #flag true if one applicant is minority and one is
		else:
			return False


	def set_minority_status(self, inputs):
		#determine minority status, this is a binary category
		#not shown: non-hispanics with no race available, whites with no ethnicity available, and loans with no race/ethn available

		if inputs['race'] == 7 and inputs['ethnicity'] !=0 and inputs['ethnicity'] != 2: #non-hispanics with no race info
			return 3
		elif inputs['race'] == 4 and inputs['ethnicity'] == 3: #whites with no ethnicity info
			return 3
		elif inputs['race'] == 7 and inputs['ethnicity'] == 3: #loans with no race and no ethn info
			return 3

		elif inputs['race'] == 4 and inputs['ethnicity'] != 0 and inputs['ethnicity'] != 2:
			return 0 #white non-hispanic
		elif inputs['race'] <=7 or inputs['ethnicity'] ==0 or inputs['ethnicity'] == 2:
			return 1 #Others including hispanic
		#elif inputs['race'] == 6 or inputs['race'] == 5: #joint status race
		#	return 1
		else:
			print inputs['race'], inputs['ethnicity']
			print 'minority status not set'

 	def set_loan_ethn(self, inputs):
		#this function outputs a number code for ethnicity: 0 - hispanic or latino, 1 - not hispanic/latino
		#2 - joint (1 applicant hispanic/latino 1 not), 3 - ethnicity not available
		#if both ethnicity fields are blank report not available(3)
		if inputs['a ethn'] == ' ':# and inputs['co ethn'] == ' ':
			return  3 #set to not available
		#determine if the loan is joint hispanic/latino and non hispanic/latino(2)
		elif inputs['a ethn'] == '1' and inputs['co ethn'] == '2':
			return  2 #set to joint
		elif inputs['a ethn'] == '2' and inputs['co ethn'] == '1':
			return  2 #set to joint
		#determine if loan is of hispanic ethnicity (appplicant is hispanic/latino, no co applicant info or co applicant also hispanic/latino)
		elif inputs['a ethn'] == '1':# and inputs['co ethn'] == '1': #both applicants hispanic
			return  0
		#elif inputs['a ethn'] == '1' and (inputs['co ethn'] == ' ' or inputs['co ethn'] == '3' or inputs['co ethn'] == '4' or inputs['co ethn']== '5'): #applicant hispanic, co-applicant blank, not available or no co applicant
		#	return  0
		#elif (inputs['a ethn'] == ' ' or inputs['a ethn'] == '3' or inputs['a ethn'] == '4' or inputs['a ethn'] == '5') and inputs['co ethn'] == '1': #co applicant hispanic, applicant blank, not available
		#	return  0
		#determine if loan is not hispanic or latino
		elif inputs['a ethn'] == '2' and inputs['co ethn'] != '1': #applicant not hispanic (positive entry), co applicant not hispanic (all other codes)
			return  1
		#elif inputs['a ethn'] != '1' and inputs['co ethn'] == '2': #co applicant not hispanic (positive entry), applicant not hispanic (all other codes)
		#	return  1
		elif (inputs['a ethn'] == '3' or inputs['a ethn'] == '4') and (inputs['co ethn'] != '1' and inputs['co ethn'] != '2'): #no applicant ethnicity information, co applicant did not mark ethnicity positively
			return  3
		else:
			return 3
			print "error setting ethnicity"

	def a_race_list(self, row):
		a_race = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		for i in range(0, 5): #convert ' ' entries to 0 for easier comparisons and loan aggregation
			if a_race[i] == ' ':
				a_race[i] = 0
			else:
				a_race[i] = int(a_race[i])
		return [int(race) for race in a_race] #convert string entries to int for easier comparison and loan aggregation

	def co_race_list(self, row):
		co_race = [row['coapplicantrace1'], row['coapplicantrace2'], row['coapplicantrace3'],row['coapplicantrace4'],row['coapplicantrace5']]
		for i in range(0,5):
			if co_race[i] == ' ':
				co_race[i] = 0
			else:
				co_race[i] = int(co_race[i])

		return [int(race) for race in co_race] #convert string entries to int for easier comparison and loan aggregation

	def set_race(self, inputs, race_list): #sets the race to an integer index for loan aggregation
		#if one white and one minority race are listed, use the minority race
		#race options are: joint, 1 through 5, 2 minority, not reported
		if race_list[0] > 5 and race_list[1] == 0 and race_list[2] == 0 and race_list[3] == 0 and race_list[4] == 0:
			return 7 #race information not available
		elif inputs['joint status'] == True:
			return  6
		#if two minority races are listed, the loan is 'two or more minority races'
		#if any combination of two or more race fields are minority then 'two or more minority races'
		elif self.minority_count(race_list) > 1: #determine if the loan will be filed as 'two or more minority races'
			return  5

		elif race_list[0] != 0 and race_list[1] == 0 and race_list[2] == 0 and race_list[3] == 0 and race_list[4] == 0: #if only the first race field is used, use the first field unless it is blank
			return  race_list[0]-1 #if only one race is reported, and joint status and minority status are false, set race to first race
		elif race_list[0] == 0 and race_list[1] == 0 and race_list[2] == 0 and race_list[3] == 0 and race_list[4] == 0:
			return  7 #if all race fields are blank, set to 7 'not available'
		else:
			for i in range(1,5):
				for r in range(0,5):
					if race_list[r] == i:
						return race_list[r] -1 #return first instance of minority race (-1 adjusts race code to race index in the JSON)
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

	def table_8x_builder(self):
		holding = OrderedDict({})
		self.container['applicantcharacteristics'] = []
		holding = self.table_8_helper('Race', 'race', self.race_names)
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

	def table_helper(self, characteristic_key, characteristic, row_list, key, key_singular, end_key, end_key_singular, end_point_list, end_bool1, end_bool2):
		temp = OrderedDict({})
		temp[characteristic_key] = characteristic
		temp[key] = self.set_list(self.end_points, row_list, key_singular, end_bool1)
		for i in range(0, len(temp[key])):
			temp[key][i][end_key] = self.set_list(self.end_points, end_point_list, end_key_singular, end_bool2)
		return temp
	def table_7x_builder(self):
		self.container['censuscharacteristics'] = []

		holding = OrderedDict({})
		'''
		holding['characteristic'] = 'Racial/Ethnic Composition'
		holding['compositions'] = self.set_list(self.end_points, self.tract_pct_minority, 'composition', False)


		for i in range(0, len(holding['compositions'])):
			holding['compositions'][i]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
		'''
		holding = self.table_helper('characteristic', 'Racial/Ethnic Composition', self.tract_pct_minority, 'compositions','compositions', 'dispositions', 'disposition', self.dispositions_list, False, True)
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
		#note to self: you have to re-instantiate all the ordered dicts or else they will be linked to each other during aggregation
		self.container['applicantincomes'] = self.set_list(self.end_points, self.applicant_income_bracket[:-1], 'applicantincome', False)

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
				minoritystatus_holding['minoritystatus'][j]['dispositions'] = self.set_list(self.end_points, self.dispositions_list, 'disposition', True)
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


class queries(AD_report):
	#can I decompose these query parts into lists and concatenate them prior to passing to the cursor?
	#need to standardize field names in order to use the same query across eyars
		#ffiec_median_family_income vs HUD_median_family_income
		#no sequencenumber prior to 2012
	def __init__(self):

		self.SQL_Count = '''SELECT COUNT(msaofproperty) FROM hmdapub{year} WHERE msaofproperty = '{MSA}' '''
		self.SQL_Query = '''SELECT {columns} FROM hmdapub{year} WHERE msaofproperty = '{MSA}' '''

	def table_A_3_1_conditions(self):
		return ''' and purchasertype != '0'; '''

	def table_A_3_2_conditions(self):
		return ''' and actiontype = '1' and purchasertype != '0';'''

	def table_A_4_1_conditions(self):
		return '''and (loantype = '2' or loantype = '3' or loantype = '4') and propertytype !='3' and loanpurpose = '1' ;'''

	def table_A_4_2_conditions(self):
		return '''and loantype = '1' and propertytype !='3' and loanpurpose = '1' ;'''

	def table_A_4_3_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '3';'''

	def table_A_4_4_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '2';'''

	def table_A_4_5_conditions(self):
		return '''and propertytype ='3';'''

	def table_A_4_6_conditions(self):
		return '''and propertytype !='3' and occupancy = '2';'''

	def table_A_4_7_conditions(self):
		return '''and propertytype ='2';'''

	def table_A_5_1_conditions(self):
		return '''and propertytype !='3' and loantype !='1' and loanpurpose = '1';'''

	def table_A_5_2_conditions(self):
		return '''and propertytype !='3' and loantype ='1' and loanpurpose = '1';'''

	def table_A_5_3_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '3';'''

	def table_A_5_4_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '2';'''

	def table_A_5_5_conditions(self):
		return '''and propertytype ='3';'''

	def table_A_5_6_conditions(self):
		return '''and occupancy ='1' and propertytype !='3' ;'''

	def table_A_5_7_conditions(self):
		return '''and propertytype ='2' ;'''

	def table_A_7_1_conditions(self):
		return '''and loantype != '1' and propertytype !='3' and loanpurpose = '1';'''


	def table_A_7_2_conditions(self):
		return '''and loantype = '1' and propertytype !='3' and loanpurpose = '1';'''

	def table_A_7_3_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '3';'''

	def table_A_7_4_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '2';'''

	def table_A_7_5_conditions(self):
		return '''and propertytype ='3';'''

	def table_A_7_6_conditions(self):
		return '''and propertytype !='3' and occupancy = '2';'''

	def table_A_7_7_conditions(self):
		return '''and propertytype ='3';'''

	def table_A_8_1_conditions(self):
		return '''and loantype != '1' and propertytype != '3' and loanpurpose = '1';'''

	def table_A_8_2_conditions(self):
		return '''and loantype ='1' and propertytype !='3' and loanpurpose = '1';'''

	def table_A_8_3_conditions(self):
		return '''and propertytype != '3' and loanpurpose = '3';'''

	def table_A_8_4_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '2';'''

	def table_A_8_5_conditions(self):
		return '''and propertytype = '3';'''

	def table_A_8_6_conditions(self):
		return '''and occupancy = '2' and propertytype != '3';'''

	def table_A_8_7_conditions(self):
		return '''and propertytype = '2';'''

	def table_A_9_conditions(self):
		return '''and actiontaken != '6' and actiontaken != '7' and actiontaken != '8' and actiontaken != '9';'''

	def table_3_1_columns(self):
		return '''censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, hoepastatus,
			purchasertype, loanamount, asofdate, statecode, statename, countycode, countyname,
			ffiec_median_family_income, minoritypopulationpct, tract_to_msa_md_income, sequencenumber'''

	def table_3_2_columns(self):
		return '''censustractnumber,  ratespread, lienstatus, loanamount, hoepastatus, purchasertype, asofdate, statecode, statename, countycode, countyname'''

	def table_4_x_columns(self):
		return '''censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy'''

	def table_5_x_columns(self):
		return '''applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate,
			actiontype, ffiec_median_family_income, statecode, statename, sequencenumber '''

	def table_7_x_columns(self):
		return '''minoritypopulationpct, actiontype, loanamount, ffiec_median_family_income, tract_to_msa_md_income, asofdate, statecode, statename '''

	def table_8_x_columns(self):
		return '''applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, asofdate, applicantsex,
			coapplicantsex, denialreason1, denialreason2, denialreason3, ffiec_median_family_income,
			statecode, statename, censustractnumber, countycode, countyname '''

	def table_9_x_columns(self):
		return '''loantype, loanpurpose, propertytype, actiontype, asofdate, censustractnumber, statecode, statename
			msaofproperty '''


class aggregate(AD_report): #aggregates LAR rows by appropriate characteristics to fill the JSON files

	def __init__(self):
		self.purchaser_first_lien_rates = ['Fannie Mae first rates', 'Ginnie Mae first rates', 'Freddie Mac first rates', 'Farmer Mac first rates', 'Private Securitization first rates', 'Commercial bank, savings bank or association first rates', 'Life insurance co., credit union, finance co. first rates', 'Affiliate institution first rates', 'Other first rates']
		self.purchaser_junior_lien_rates = ['Fannie Mae junior rates', 'Ginnie Mae junior rates', 'Freddie Mac junior rates', 'Farmer Mac junior rates', 'Private Securitization junior rates', 'Commercial bank, savings bank or association junior rates', 'Life insurance co., credit union, finance co. junior rates', 'Affiliate institution junior rates', 'Other junior rates']
		self.purchaser_first_lien_weight = ['Fannie Mae first weight', 'Ginnie Mae first weight', 'Freddie Mac first weight', 'Farmer Mac first weight', 'Private Securitization first weight', 'Commercial bank, savings bank or association first weight', 'Life insurance co., credit union, finance co. first weight', 'Affiliate institution first weight', 'Other first weight']
		self.purchaser_junior_lien_weight = ['Fannie Mae junior weight', 'Ginnie Mae junior weight', 'Freddie Mac junior weight', 'Farmer Mac junior weight', 'Private Securitization junior weight', 'Commercial bank, savings bank or association junior weight', 'Life insurance co., credit union, finance co. junior weight', 'Affiliate institution junior weight', 'Other junior weight']

	def by_demographics_3x(self, container, inputs, section, section_index, key, key_index):
		container[section][section_index][key][key_index]['purchasers'][inputs['purchaser']]['count'] += 1
		container[section][section_index][key][key_index]['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

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
		for n in range(0,9):
			if float(container['pricinginformation'][1]['purchasers'][n]['firstliencount']) > 0 and inputs[self.purchaser_first_lien_rates[n]] > 0: #bug fix for divide by 0 errors
				container['points'][8]['purchasers'][n]['firstliencount'] = round(numpy.mean(numpy.array(inputs[self.purchaser_first_lien_rates[n]])),2)

			if float(container['pricinginformation'][1]['purchasers'][n]['juniorliencount']) > 0 and inputs[self.purchaser_junior_lien_rates[n]] > 0: #bug fix for divide by 0 errors
				container['points'][8]['purchasers'][n]['juniorliencount'] = round(numpy.mean(numpy.array(inputs[self.purchaser_junior_lien_rates[n]]), dtype=numpy.float64),2)

	def by_weighted_mean(self, container, inputs): #aggregate loans by weighted mean of rate spread
		for n in range(0,9):
			if float(container['pricinginformation'][1]['purchasers'][n]['firstliencount']) > 0 and inputs[self.purchaser_first_lien_weight[n]] > 0: #bug fix for divide by 0 errors
				'''
				s = [['123.123','23'],['2323.212','123123.21312']]
				decimal_s = [[decimal.Decimal(x) for x in y] for y in s]
				ss = numpy.array(decimal_s)
				'''
				nd_first_rates = numpy.array(inputs[self.purchaser_first_lien_rates[n]])
				#nd_first_rates = [[Decimal(x) for x in inputs[self.purchaser_first_lien_rates[n]]]]
				#nd_first_rates_np = numpy.array(nd_first_rates)
				nd_first_weights = numpy.array(inputs[self.purchaser_first_lien_weight[n]])
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

			#junior lien median block
			if len(inputs[self.purchaser_junior_lien_rates[n]]) > 0: #check to see if the array is populated
				container['points'][9]['purchasers'][n]['juniorliencount'] = round(numpy.median(numpy.array(inputs[self.purchaser_junior_lien_rates[n]])),2) #for normal median

	def by_weighted_median(self, container, inputs):
		for n in range(0,9):
			#first lien weighted median block
			#print inputs[self.purchaser_first_lien_rates[n]], inputs[self.purchaser_first_lien_weight[n]]
			if len(inputs[self.purchaser_first_lien_rates[n]]) >0 and len(inputs[self.purchaser_first_lien_weight[n]]) >0: #check to see if the array is populated
				nd_first_rates = inputs[self.purchaser_first_lien_rates[n]]
				nd_first_values = inputs[self.purchaser_first_lien_weight[n]]
				nd_first_rates, nd_first_values = zip(*sorted(zip(nd_first_rates, nd_first_values)))

				step_size = round(float(sum(nd_first_values)) / len(nd_first_values),3)
				steps_needed = (len(nd_first_values) / float(2))
				nd_steps = [round(x/step_size,3) for x in nd_first_values]

				count = 0
				for i in range(0, len(nd_first_values)):
					step_taken = nd_first_values[i] / float(step_size)
					steps_needed -=step_taken
					count +=1

					if steps_needed <= 0:
						#print nd_first_rates, "*"*10,nd_first_rates[count-1], count-1

						container['points'][9]['purchasers'][n]['firstlienvalue'] = sorted(nd_first_rates)[count-1] #for weighted median
						break

			#junior lien weighted median block
			if len(inputs[self.purchaser_junior_lien_rates[n]]) > 0 and len(inputs[self.purchaser_junior_lien_weight[n]]) >0: #check to see if the array is populated
				nd_junior_rates = inputs[self.purchaser_junior_lien_rates[n]]
				nd_junior_values = inputs[self.purchaser_junior_lien_weight[n]]
				nd_junior_rates, nd_junior_values = zip(*sorted(zip(nd_junior_rates, nd_junior_values)))

				step_size = round(float(sum(nd_junior_values)) / len(nd_junior_values),3)
				steps_needed = (len(nd_junior_values) / float(2))
				nd_steps = [round(x/step_size,3) for x in nd_junior_values]

				count = 0
				for i in range(0, len(nd_junior_values)):
					step_taken = nd_junior_values[i] / float(step_size)
					steps_needed -=step_taken
					count +=1

					if steps_needed <= 0:
						#print nd_junior_rates, "*"*10,nd_junior_rates[count-1], count-1

						container['points'][9]['purchasers'][n]['juniorlienvalue'] = sorted(nd_junior_rates)[count-1] #for weighted median
						break

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

	def by_4x_demographics(self, container, inputs, key, key_index):

		if inputs['action taken'] < 6:
			if key == 'minoritystatuses' and key_index > 1:
				pass
			else:
				self.aggregate_4x(container, inputs, key, key_index, 0, False)
				self.aggregate_4x(container, inputs, key, key_index, inputs['action taken'], False)

				if inputs['gender'] < 3:
					self.aggregate_4x(container, inputs, key, key_index, 0, True)
					self.aggregate_4x(container, inputs, key, key_index, inputs['action taken'], True)

	def aggregate_4x(self, container, inputs, key, key_index, action_index, gender_bool):
		if gender_bool == False:
			container[key][key_index]['dispositions'][action_index]['count'] +=1
			container[key][key_index]['dispositions'][action_index]['value'] +=int(inputs['loan value'])
		elif gender_bool == True:
			container[key][key_index]['genders'][inputs['gender']]['dispositions'][action_index]['count'] +=1
			container[key][key_index]['genders'][inputs['gender']]['dispositions'][action_index]['value'] +=int(inputs['loan value'])

	def totals_4x(self, container, inputs):
		if inputs['action taken'] < 6 and inputs['action taken'] != ' ':
			container['total'][0]['count'] += 1
			container['total'][0]['value'] += int(inputs['loan value'])
			container['total'][inputs['action taken']]['count'] +=1
			container['total'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def by_5x_totals(self, container, inputs):
		if inputs['action taken'] > 5:
			pass
		else:
			container['total'][0]['count'] +=1
			container['total'][0]['value'] += int(inputs['loan value'])

			container['total'][inputs['action taken']]['count'] +=1
			container['total'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def by_5x_demographics(self, container, inputs, index_num, index_name, index_code):
		#index_num: the index of the primary list in the dictionary
		#index_name: the key corresponding to the index number
		#index_code: the code from the inputs dictionary for the row being aggregated
		if inputs['income bracket'] < 5 and inputs['action taken'] < 6:
			container['applicantincomes'][inputs['income bracket']]['borrowercharacteristics'][index_num][index_name][index_code]['dispositions'][0]['count'] += 1 #increment count of applications received by minority status
			container['applicantincomes'][inputs['income bracket']]['borrowercharacteristics'][index_num][index_name][index_code]['dispositions'][0]['value'] += int(inputs['loan value'])
			container['applicantincomes'][inputs['income bracket']]['borrowercharacteristics'][index_num][index_name][index_code]['dispositions'][inputs['action taken']]['count'] += 1 #increment count by action taken and minority status
			container['applicantincomes'][inputs['income bracket']]['borrowercharacteristics'][index_num][index_name][index_code]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def build_report5x(self, table5x, inputs):
		self.by_5x_demographics(table5x, inputs, 0, 'races', inputs['race'])
		self.by_5x_demographics(table5x, inputs, 1, 'ethnicities', inputs['ethnicity'])
		if inputs['minority status'] < 2:
			self.by_5x_demographics(table5x, inputs, 2, 'minoritystatus', inputs['minority status'])
		self.by_5x_totals(table5x, inputs)

	def by_tract_characteristics(self, container, inputs, json_index, key, key_index, action_index):
		if action_index < 6 and key_index <4:
			container['censuscharacteristics'][json_index][key][key_index]['dispositions'][0]['count'] +=1
			container['censuscharacteristics'][json_index][key][key_index]['dispositions'][0]['value'] +=int(inputs['loan value'])
			container['censuscharacteristics'][json_index][key][key_index]['dispositions'][action_index]['count'] +=1
			container['censuscharacteristics'][json_index][key][key_index]['dispositions'][action_index]['value'] +=int(inputs['loan value'])

	def by_income_ethnic_combo(self, container, inputs):
		if inputs['action taken'] > 5 or inputs['tract income index'] > 3:
			pass
		else:
			container['incomeRaces'][0]['incomes'][inputs['tract income index']]['compositions'][inputs['minority percent index']]['dispositions'][0]['count'] +=1
			container['incomeRaces'][0]['incomes'][inputs['tract income index']]['compositions'][inputs['minority percent index']]['dispositions'][0]['value'] += int(inputs['loan value'])
			container['incomeRaces'][0]['incomes'][inputs['tract income index']]['compositions'][inputs['minority percent index']]['dispositions'][inputs['action taken']]['count'] +=1
			container['incomeRaces'][0]['incomes'][inputs['tract income index']]['compositions'][inputs['minority percent index']]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def get_small_county_flag(self, cur, MSA):
		#msa can be either an MSA or the last 5 of a geoid?
		SQL = '''SELECT small_county FROM tract_to_cbsa_2010 WHERE geoid_msa = %s;'''
		cur.execute(SQL, MSA)
		small_county_flag = cur.fetchall()[0]

	def by_geo_type(self, container, inputs, index_num, action_index):
		container['types'][index_num]['dispositions'][action_index]['count'] +=1
		container['types'][index_num]['dispositions'][action_index]['value'] +=int(inputs['loan value'])

	def totals_7x(self, container, inputs):
		if inputs['action taken'] > 5:
			pass
		else:
			container['total'][0]['count'] += 1
			container['total'][0]['value'] += int(inputs['loan value'])
			container['total'][inputs['action taken']]['count'] += 1
			container['total'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def by_denial_percent(self, container, inputs, index_num, key):
		for j in range(0, len(container['applicantcharacteristics'][index_num][key])):
			for i in range(0, len(container['applicantcharacteristics'][index_num][key][j]['denialreasons'])):
				if float(container['applicantcharacteristics'][index_num][key][j]['denialreasons'][9]['count']) >0:
					container['applicantcharacteristics'][index_num][key][j]['denialreasons'][i]['value'] = int(round((container['applicantcharacteristics'][index_num][key][j]['denialreasons'][i]['count'] / float(container['applicantcharacteristics'][index_num][key][j]['denialreasons'][9]['count'])) *100,0))

	def by_denial_reason(self, container, inputs, index_num, key, key_singular):
		for reason in inputs['denial_list']:
			if reason is None:
				pass
			else:
				container['applicantcharacteristics'][index_num][key][inputs[key_singular]]['denialreasons'][9]['count'] +=1 #add to totals
				container['applicantcharacteristics'][index_num][key][inputs[key_singular]]['denialreasons'][reason]['count'] +=1 #adds to race/reason cell

	def build_report8x(self, table8x, inputs):
		self.by_denial_reason(table8x, inputs, 0, 'races', 'race')
		self.by_denial_reason(table8x, inputs, 1, 'ethnicities', 'ethnicity')
		if inputs['minority status'] <2: #pass on loans with no minority status information
			self.by_denial_reason(table8x, inputs, 2, 'minoritystatuses', 'minority status')
		self.by_denial_reason(table8x, inputs, 3, 'genders', 'gender')
		if inputs['income bracket'] <6:
			self.by_denial_reason(table8x, inputs, 4, 'incomes', 'income bracket')

	def build_report7x(self, table7x, inputs):
		self.by_tract_characteristics(table7x, inputs, 0, 'compositions', inputs['minority percent index'], inputs['action taken'])
		self.by_tract_characteristics(table7x, inputs, 1, 'incomes', inputs['tract income index'], inputs['action taken'])
		self.by_income_ethnic_combo(table7x, inputs)
		if inputs['small county flag'] == '1':
			self.by_geo_type(table7x, inputs, 0, 0)
			self.by_geo_type(table7x, inputs, 0, inputs['action taken'])
		if inputs['tract to MSA income'] == 4 and inputs['action taken'] < 6:
			self.by_geo_type(table7x, inputs, 1, 0)
			self.by_geo_type(table7x, inputs, 1, inputs['action taken'])
		self.totals_7x(table7x, inputs)

	def build_report4x(self, table4x, inputs): #call functions to fill JSON object for table 4-1 (FHA, FSA, RHS, and VA home purchase loans)
		self.by_4x_demographics(table4x, inputs, 'races', inputs['race'])
		self.by_4x_demographics(table4x, inputs, 'ethnicities', inputs['ethnicity'])
		self.by_4x_demographics(table4x, inputs, 'minoritystatuses', inputs['minority status'])

		self.by_applicant_income_4x(table4x, inputs) #aggregate loans by applicant income to MSA income ratio
		self.totals_4x(table4x, inputs) #totals of applications by application disposition

	def build_report_31(self, table31, inputs):  #calls aggregation functions to fill JSON object for table 3-1
		self.by_demographics_3x(table31, inputs, 'borrowercharacteristics', 0, 'races', inputs['race'])#aggregate loan by race
		self.by_demographics_3x(table31, inputs, 'borrowercharacteristics', 1, 'ethnicities', inputs['ethnicity'])#aggregate loan by ethnicity
		if inputs['minority status'] < 2:
			self.by_demographics_3x(table31, inputs, 'borrowercharacteristics', 2, 'minoritystatuses', inputs['minority status'])#aggregate loan by minority status (binary determined by race and ethnicity)
		if inputs['income bracket'] < 6: #income index outside bounds of report 3-1
			self.by_demographics_3x(table31, inputs, 'borrowercharacteristics', 3, 'applicantincomes', inputs['income bracket'])#aggregates by ratio of appicant income to tract median income (census)
		if inputs['minority percent index'] < 5: #minority percent not available
			self.by_demographics_3x(table31, inputs, 'censuscharacteristics', 0, 'tractpctminorities', inputs['minority percent index'])#aggregates loans by percent of minority residents (census)
		if inputs['tract income index'] < 4: #income ratio not available or outside report 3-1 bounds
			self.by_demographics_3x(table31, inputs, 'censuscharacteristics', 1, 'incomelevels', inputs['tract income index']) #aggregates loans by census tract income rating - low/moderate/middle/upper
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




