from msa_indexing import MSA_info
from median_age_api import median_age_API as age_API
from demographics_indexing import demographics
from connector import connect_DB as connect

class parse_inputs(object):
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

		#median age of housing by tract
		self.tract_median_ages = {}

	def parse_3_1(self, row): #takes a row of tuples from a table 3-1 query and parses it to the inputs dictionary
		#parsing inputs for report 3.1
		#self.inputs will be used in the aggregation functions
		#note: sequence number did not exist prior to 2012 and HUD median income became FFIEC median income in 2012
		#instantiate classes to set loan variables
		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics

		app_races = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		co_app_races = [row['coapplicantrace1'], row['coapplicantrace2'], row['coapplicantrace3'],row['coapplicantrace4'],row['coapplicantrace5']]

		a_race = demo.make_race_list(app_races) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.make_race_list(co_app_races) #put co-applicant race codes in a list 0-5, 0 is blank field
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
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs) #sets the tract to MSA median income ratio to an index number for aggregation
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs) #sets the applicant income as an index by an applicant's income as a percent of MSA median
		self.inputs['minority percent index'] = MSA_index.minority_percent(self.inputs) #sets the minority population percent to an index for aggregation

		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['race'] = demo.set_race(self.inputs, a_race) #requires joint status be set prior to running set_race
		self.inputs['ethnicity'] = demo.set_ethnicity(self.inputs) #requires  ethnicity be parsed prior to running set_ethnicity
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status


	def parse_3_2(self, row): #takes a row of tuples from a table 3-1 query and parses it to the inputs dictionary
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
		self.inputs['rate spread index'] = demo.rate_spread_index_3_2(self.inputs['rate spread']) #index of the rate spread for use in the JSON structure

	def parse_4_x(self, row):
		#parsing inputs for report 4-x
		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics
		a_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		co_race = [] #race lists will hold 5 integers with 0 replacing a blank entry

		#fill race lists from the demographics class
		app_races = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		co_app_races = [row['coapplicantrace1'], row['coapplicantrace2'], row['coapplicantrace3'],row['coapplicantrace4'],row['coapplicantrace5']]
		a_race = demo.make_race_list(app_races) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.make_race_list(co_app_races) #put co-applicant race codes in a list 0-5, 0 is blank field

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
		self.inputs['ethnicity'] = demo.set_ethnicity(self.inputs) #requires  ethnicity be parsed prior to running set_ethnicity
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['gender'] = demo.set_gender(self.inputs)

	def parse_5_x(self, row):

		#self.inputs will be used in the aggregation functions
		#note: sequence number did not exist prior to 2012 and HUD median income became FFIEC median income in 2012
		#instantiate classes to set loan variables
		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics

		app_races = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		co_app_races = [row['coapplicantrace1'], row['coapplicantrace2'], row['coapplicantrace3'],row['coapplicantrace4'],row['coapplicantrace5']]
		a_race = demo.make_race_list(app_races) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.make_race_list(co_app_races) #put co-applicant race codes in a list 0-5, 0 is blank field
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
		self.inputs['ethnicity'] = demo.set_ethnicity(self.inputs) #requires  ethnicity be parsed prior to running set_ethnicity
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status

	def parse_7_x(self, row):
		MSA_index = MSA_info() #contains functions for census tract characteristics
		#connection = connect() #connects to the DB
		#cur = connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres

		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['county code'] = row['countycode']
		self.inputs['census tract number'] = row['censustractnumber']
		self.inputs['MSA'] = row['msaofproperty']
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['action taken'] = int(row['actiontype']) #disposition of the loan application
		self.inputs['minority percent'] = row['minoritypopulationpct'] #%of population that is minority
		self.inputs['minority percent index'] = MSA_index.minority_percent(self.inputs) #sets the minority population percent to an index for aggregation
		self.inputs['tract to MSA income'] = row['tract_to_msa_md_income'] #ratio of tract to msa/md income
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs) #sets the tract to msa income ratio to an index for aggregation (low, middle, moderate,  high
		#self.inputs['small county flag'] = MSA_index.get_small_county_flag(cur, self.inputs['MSA'], self.inputs['state code'], self.inputs['county code'], self.inputs['census tract number'].replace('.',''))

	def parse_8_x(self, row):
		#note: sequence number did not exist prior to 2012 and HUD median income became FFIEC median income in 2012

		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics
		a_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		co_race = [] #race lists will hold 5 integers with 0 replacing a blank entry

		#fill race lists from the demographics class
		app_races = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		co_app_races = [row['coapplicantrace1'], row['coapplicantrace2'], row['coapplicantrace3'],row['coapplicantrace4'],row['coapplicantrace5']]
		a_race = demo.make_race_list(app_races) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.make_race_list(co_app_races) #put co-applicant race codes in a list 0-5, 0 is blank field

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
		self.inputs['ethnicity'] = demo.set_ethnicity(self.inputs) #requires  ethnicity be parsed prior to running set_ethnicity
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

	def parse_9_x(self, row):
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['census tract'] = row['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
		self.inputs['action taken'] = int(row['actiontype']) #disposition of the loan application
		self.inputs['property type'] = row['propertytype']
		self.inputs['loan purpose'] = row['loanpurpose']
		self.inputs['loan value'] = row['loanamount']
		self.inputs['occupancy'] = row['occupancy']
		self.inputs['tract number'] = row['censustractnumber']
		if self.inputs['census tract'] != 'NA     ':
			self.inputs['median age'] = self.tract_median_ages[row['statecode']+row['countycode']+row['censustractnumber']] #passes state/county/tract to a dict to get age
		self.inputs['loan type index'] = self.set_loan_index(int(row['loantype']), row['loanpurpose'], row['propertytype'])
		self.inputs['median age index'] = self.median_age_index(self.inputs['median age'])

	def set_loan_index(self, loan_type, loan_purpose, property_type):
		if loan_purpose == '1' and property_type != '3':
			if loan_type == 1:
				return 1
			elif loan_type == 2:
				return 0
			elif loan_type == 3:
				return 0
			elif loan_type == 4:
				return 0
		elif loan_purpose == '3' and property_type != '3':
			return 2
		elif loan_purpose == '2' and property_type != '3':
			return 3
		elif property_type == '3':
			return 4


	def median_tract_age(self, cur, MSA): #, state, county, tract
		#calls the HMDA database and returns a distinct list of tracts for an MSA
		#queries Census API to get median housing age for each tract
		#adds the tract and age to self.
		self.age_API = age_API() #initialize API call object, this object returns the median age of when passed state, county, and tract numbers.

		state_string = '''SELECT DISTINCT(statecode) FROM hmdapub2013 WHERE msaofproperty = '{MSA}' ;'''
		tract_string = '''SELECT DISTINCT(censustractnumber) FROM hmdapub2013 WHERE countycode = '{county}' and msaofproperty = '{MSA}' ;'''
		county_string = '''SELECT DISTINCT(countycode) FROM hmdapub2013 WHERE statecode = '{statecode}' and msaofproperty = '{MSA}' ;'''
		state_SQL = state_string.format(MSA = MSA)

		cur.execute(state_SQL,)
		state_list = cur.fetchall()
		if len(state_list) > 0:
		#try
			for j in range(0, len(state_list)):
				state = state_list[j][0]
				county_SQL = county_string.format(MSA = MSA, statecode = state)
				cur.execute(county_SQL, MSA)

				county_list= cur.fetchall() #counties is a list
				#print 'county list\n', county_list
				for k in range(0, len(county_list)):
					county = county_list[k][0]
					tract_SQL = tract_string.format(county = county, MSA = MSA)
					cur.execute(tract_SQL,)

					tract_list= cur.fetchall()
					#print tract_list
					for i in range(0, len(tract_list)):
						#print tract_list[i][0][:-3] + tract_list[i][0][5:]
						tract = tract_list[i][0].replace('.', '')
						if tract == 'NA     ':
							pass
						else:
							tract_age = self.age_API.get_age(state, county, tract)
							#print int(tract_age.strip('"'))
						  #  print state+county+tract_list[i][0], tract_age
							if tract_age != 'null':
								self.tract_median_ages[state+county+tract_list[i][0]] = int(tract_age.strip('"'))
							else:
								self.tract_median_ages[state+county+tract_list[i][0]] = tract_age.strip('"')
		else:
			print "no states in '{MSA}' for selected HMDA year".format(MSA = MSA)
		#except IndexError:
		#   print cur.fetchall(), "index error problem with '{MSA}' ".format(MSA = MSA)
		#print self.tract_median_ages
					#print state + county+tract_list[i][0]

	def median_age_index(self, year):
		#are new buckets added every 10 years?
		#what will the unavailable index require?
		if year <= 1969:
			return 4
		elif year <= 1979:
			return 3
		elif year <= 1989:
			return 2
		elif year <= 1999:
			return 1
		elif year <= 2010:
			return 0
		else:
			print "no median age found for tract"
			return 5 #this is actually a report section, not an ignored index

	def parse_11_x(self, row):
		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics
		a_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		co_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		#fill race lists from the demographics class
		app_races = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		co_app_races = [row['coapplicantrace1'], row['coapplicantrace2'], row['coapplicantrace3'],row['coapplicantrace4'],row['coapplicantrace5']]
		a_race = demo.make_race_list(app_races) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.make_race_list(co_app_races) #put co-applicant race codes in a list 0-5, 0 is blank field
		#add data elements to dictionary
		self.inputs['a_race'] = a_race
		self.inputs['co_race'] = co_race
		self.inputs['a ethn'] = row['applicantethnicity'] #ethnicity of the applicant
		self.inputs['co ethn'] = row['coapplicantethnicity'] #ethnicity of the co-applicant
		self.inputs['income'] = row['applicantincome'] #relied upon income rounded to the nearest thousand
		self.inputs['rate spread'] = row['ratespread'] # interest rate spread over APOR if spread is greater than 1.5%
		self.inputs['loan value'] = (row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['app sex'] = row['applicantsex']
		self.inputs['co app sex'] = row['coapplicantsex']
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['minority percent'] = row['minoritypopulationpct'] #%of population that is minority
		self.inputs['tract to MSA income'] = row['tract_to_msa_md_income'] #ratio of tract to msa/md income
		self.inputs['sequence'] = row['sequencenumber'] #the sequence number of the loan, used for checking errors
		self.inputs['lien status'] = row['lienstatus']
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs) #sets the tract to MSA median income ratio to an index number for aggregation
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs) #sets the applicant income as an index by an applicant's income as a percent of MSA median
		self.inputs['rate spread index'] = demo.rate_spread_index_11_x(self.inputs['rate spread']) #index of the rate spread for use in the JSON structure
		self.inputs['minority percent index'] = MSA_index.minority_percent(self.inputs) #sets the minority population percent to an index for aggregation
		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['race'] = demo.set_race(self.inputs, a_race) #requires joint status be set prior to running set_race
		self.inputs['ethnicity'] = demo.set_ethnicity(self.inputs) #requires  ethnicity be parsed prior to running set_ethnicity
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['gender'] = demo.set_gender(self.inputs)

	def parse_12_x(self, row):
		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics
		a_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		co_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		#fill race lists from the demographics class
		app_races = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		co_app_races = [row['coapplicantrace1'], row['coapplicantrace2'], row['coapplicantrace3'],row['coapplicantrace4'],row['coapplicantrace5']]
		a_race = demo.make_race_list(app_races) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.make_race_list(co_app_races) #put co-applicant race codes in a list 0-5, 0 is blank field
		#add data elements to dictionary
		self.inputs['a_race'] = a_race
		self.inputs['co_race'] = co_race
		self.inputs['a ethn'] = row['applicantethnicity'] #ethnicity of the applicant
		self.inputs['co ethn'] = row['coapplicantethnicity'] #ethnicity of the co-applicant
		self.inputs['income'] = row['applicantincome'] #relied upon income rounded to the nearest thousand
		self.inputs['rate spread'] = row['ratespread'] # interest rate spread over APOR if spread is greater than 1.5%
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['app sex'] = row['applicantsex']
		self.inputs['co app sex'] = row['coapplicantsex']
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['minority percent'] = row['minoritypopulationpct'] #%of population that is minority
		self.inputs['tract to MSA income'] = row['tract_to_msa_md_income'] #ratio of tract to msa/md income
		self.inputs['sequence'] = row['sequencenumber'] #the sequence number of the loan, used for checking errors
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs) #sets the tract to MSA median income ratio to an index number for aggregation
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs) #sets the applicant income as an index by an applicant's income as a percent of MSA median
		self.inputs['action taken'] = int(row['actiontype'])
		self.inputs['rate spread index'] = demo.rate_spread_index_11_x(self.inputs['rate spread']) #index of the rate spread for use in the JSON structure
		self.inputs['minority percent index'] = MSA_index.minority_percent(self.inputs) #sets the minority population percent to an index for aggregation
		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['race'] = demo.set_race(self.inputs, a_race) #requires joint status be set prior to running set_race
		self.inputs['ethnicity'] = demo.set_ethnicity(self.inputs) #requires  ethnicity be parsed prior to running set_ethnicity
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['gender'] = demo.set_gender(self.inputs)

	def parse_A_x(self, row):
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['sequence'] = row['sequencenumber'] #the sequence number of the loan, used for checking errors
		self.inputs['lien status'] = row['lienstatus']
		self.inputs['action taken index'] = self.action_taken_index(int(row['actiontype']), row['preapproval']) #disposition of the loan application
		self.inputs['purchaser'] = int(row['purchasertype'])
		self.inputs['preapproval'] = row['preapproval']
		self.inputs['loan purpose'] = self.purpose_index(row['loanpurpose']) #adjust loan purpose down one to match index in JSON structure
		self.inputs['loan type'] = int(row['loantype']) -1 #adjust loan purpose down one to match index in JSON structure

	def action_taken_index(self, action_taken, preapproval):
		if action_taken < 6:
			return action_taken
		elif action_taken == 6:
			return 7
		else:
			return 8

	def purpose_index(self, loantype):
		if loantype == '1':
			return 0 #purchase loans
		elif loantype == '2':
			return 2 #home improvement loans
		elif loantype == '3':
			return 1 #refinance loans

	def parse_A_4(self, row):
		MSA_index = MSA_info() #contains functions for census tract characteristics
		demo=demographics() #contains functions for borrower characteristics
		a_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		co_race = [] #race lists will hold 5 integers with 0 replacing a blank entry
		#fill race lists from the demographics class
		app_races = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		co_app_races = [row['coapplicantrace1'], row['coapplicantrace2'], row['coapplicantrace3'],row['coapplicantrace4'],row['coapplicantrace5']]
		a_race = demo.make_race_list(app_races) #put applicant race codes in a list 0-5, 0 is blank field
		co_race = demo.make_race_list(co_app_races) #put co-applicant race codes in a list 0-5, 0 is blank field
		#add data elements to dictionary
		self.inputs['a_race'] = a_race
		self.inputs['co_race'] = co_race
		self.inputs['a ethn'] = row['applicantethnicity'] #ethnicity of the applicant
		self.inputs['co ethn'] = row['coapplicantethnicity'] #ethnicity of the co-applicant
		self.inputs['income'] = row['applicantincome'] #relied upon income rounded to the nearest thousand
		self.inputs['rate spread'] = row['ratespread'] # interest rate spread over APOR if spread is greater than 1.5%
		self.inputs['loan value'] = float(row['loanamount']) #loan value rounded to the nearest thousand
		self.inputs['year'] = row['asofdate'] #year or application or origination
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['app sex'] = row['applicantsex']
		self.inputs['co app sex'] = row['coapplicantsex']
		self.inputs['MSA median income'] = row['ffiec_median_family_income'] #median income for the tract/msa
		self.inputs['minority percent'] = row['minoritypopulationpct'] #%of population that is minority
		self.inputs['tract to MSA income'] = row['tract_to_msa_md_income'] #ratio of tract to msa/md income
		self.inputs['sequence'] = row['sequencenumber'] #the sequence number of the loan, used for checking errors
		self.inputs['preapproval'] = row['preapproval']
		self.inputs['action taken'] = row['actiontype']
		#self.inputs['lien status'] = row['lienstatus']
		self.inputs['tract income index'] = MSA_index.tract_to_MSA_income(self.inputs) #sets the tract to MSA median income ratio to an index number for aggregation
		self.inputs['income bracket'] = MSA_index.app_income_to_MSA(self.inputs) #sets the applicant income as an index by an applicant's income as a percent of MSA median
		self.inputs['rate spread index'] = demo.rate_spread_index_11_x(self.inputs['rate spread']) #index of the rate spread for use in the JSON structure
		self.inputs['minority percent index'] = MSA_index.minority_percent(self.inputs) #sets the minority population percent to an index for aggregation
		self.inputs['app non white flag'] = demo.set_non_white(a_race) #flags the applicant as non-white if true, used in setting minority status and race
		self.inputs['co non white flag'] = demo.set_non_white(co_race) #flags the co applicant as non-white if true, used in setting minority status and race
		self.inputs['minority count'] = demo.minority_count(a_race) #determines if the number of minority races claimed by the applicant is 2 or greater
		self.inputs['joint status'] = demo.set_joint(self.inputs) #requires non white status flags be set prior to running set_joint
		self.inputs['race'] = demo.set_race(self.inputs, a_race) #requires joint status be set prior to running set_race
		self.inputs['ethnicity'] = demo.set_ethnicity(self.inputs) #requires  ethnicity be parsed prior to running set_ethnicity
		self.inputs['minority status'] = demo.set_minority_status(self.inputs) #requires non white flags be set prior to running set_minority_status
		self.inputs['gender'] = demo.set_gender(self.inputs)

	def parse_B_x(self, row):
		demo=demographics() #contains functions for borrower characteristics
		self.inputs['year'] = row['asofdate'] #year or application or origination
		#self.inputs['rate spread'] = row['ratespread'] # interest rate spread over APOR if spread is greater than 1.5%
		self.inputs['rate spread'] = row['ratespread']
		self.inputs['state code'] = row['statecode'] #two digit state code
		self.inputs['state name'] = row['statename'] #two character state abbreviation
		self.inputs['sequence'] = row['sequencenumber'] #the sequence number of the loan, used for checking errors
		self.inputs['loan purpose'] = self.purpose_index(row['loanpurpose'])
		self.inputs['lien status'] = int(row['lienstatus'])
		self.inputs['hoepa flag'] = int(row['hoepastatus']) #if the loan is subject to Home Ownership Equity Protection Act
		self.inputs['property type'] = int(row['propertytype'])
		self.inputs['rate spread index'] = demo.rate_spread_index_11_x(row['ratespread']) #index of the rate spread for use in the JSON structure