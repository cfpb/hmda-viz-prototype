#this file pulls the data required to build the MSA aggregate reports 3-1 and 3-2 covering loan sales by purchaser, ethnicity, income, and pricing
#rows race, ethnicity, income, pricing
#columns are purchaser, lien status. Sub columns are counts and values of the main columns

#the report_3_ object will be instantiated by the controller object (in another file).
# report_3_ initializes with a list 'inputs' that holds all the information on a loan (both information pulled from the SQL server and information created by functions in this file)
# report_3_ has a single JSON structure named 'table_3'. This table holds the aggregations of loans by race, purchaser, ethnicity, minority status, and lien status.
# functions in report_3_ are: parse_inputs, set_joint_status, set_minority_status, set_race, table_3_aggregator, print_report_3, write_report_3, report_3_main
#parse_inputs takes one row of the LAR file as a parameter and stores the values in the 'inputs' dictioanry
#set_joint_status determines if the loan has joint status (if one borrower's race is white and the other non-white)
#set_minority_status flags if any applicant on the loan is of a minority race or ethnicity
#set_race changes the race code from the LAR file to match the output options for the report
#table_3_aggregator writes data into the JSON structure
#print_report_3 prints the JSON structure to the terminal
#write_report_3 write sthe JSON object to a file
#report_3_main pings the SQL server to get data and uses the other functions to aggregate and write it to the JSON structure
class report_3_(object):


	def __init__(self):
		self.inputs = {} #will hold one row's values for all inputs into the other functions to determine how to aggregate the loan
		 #JSON object to hold data for tables 3-1, 3-2
		self.table_3 = {
		"table": "",
		"type": "aggregate",
		"desc": "Loans sold, by characteristics of borrower and of census tract in which property is located and by type of purchaser (includes originations and purchased loans",
		"year": "",
		"msa-md": {
			"id": "",
			"name": "",
			"state": ""
		},
		"borrower-characteristics": [
			{
				"name": "Race",
				"types": [
					{
						"name": "American Indian/Alaska Native",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Asian",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Black",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Pacific Islander",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "White",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Not Provided",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Not Applicable",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "2 minority",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "joint",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "not reported",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					}
				]
			},
			{
				"name": "Ethnicity",
				"types": [
					{
						"name": "Hispanic or Latino",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Not Hispanic or Latino",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Joint",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Ethnicity not available",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Farmer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					}
				]
			},
			{
				"name": "Minority Status",
				"types": [
					{
						"name": "White non-hispanic",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Faermer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					},
					{
						"name": "Others, including Hispanic",
						"purchasers": [
							{
								"name": "Loan was not originated or purchased in calendar year",
								"count": 0,
								"value": 0
							},
							{
								"name": "Fannie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Ginnie Mae",
								"count": 0,
								"value": 0
							},
							{
								"name": "Freddie Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Faermer Mac",
								"count": 0,
								"value": 0
							},
							{
								"name": "Private securitization",
								"count": 0,
								"value": 0
							},
							{
								"name": "Commercial bank",
								"count": 0,
								"value": 0
							},
							{
								"name": "Insurance co., Credit Union, Mortgage Bank or Finance co.",
								"count": 0,
								"value": 0
							},
							{
								"name": "Affiliate Institution",
								"count": 0,
								"value": 0
							},
							{
								"name": "Other purchaser",
								"count": 0,
								"value": 0
							}
						]
					}
				]
			}
		]
	}

	def set_ethnicity(self):
		#this function outputs a number code for ethnicity: 0 - hispanic or latino, 1 - not hispanic/latino
		#2 - joint (1 applicant hispanic/latino 1 not), 3 - ethnicity not available
		#if both ethnicity fields are blank report not available(3)
		if self.inputs['a ethn'] == ' ' and self.inputs['co ethn']:
			self.inputs['ethnicity'] = 3 #set to not available

		#determine if the loan is joint hispanic/latino and non hispanic/latino(2)
		elif self.inputs['a ethn'] == '1' and self.inputs['co ethn'] != '1':
			self.inputs['ethnicity'] = 2 #set to joint
		elif self.inputs['a ethn'] != '1' and self.inputs['co ethn'] == '1':
			self.inputs['ethnicity'] = 2 #set to joint
		#determine if loan is of hispanic ethnicity (appplicant is hispanic/latino, no co applicant info or co applicant also hispanic/latino)
		elif self.inputs['a ethn'] == '1' and self.inputs['co ethn'] == '1':
			self.inputs['ethnicity'] = 0
		elif self.inputs['a ethn'] == '1' and (self.inputs['co ethn'] == ' ' or self.inputs['co ethn'] == '3' or self.inputs['co ethn'] == '4' or self.inputs['co ethn']) == '5':
			self.inputs['ethnicity'] = 0

		#determine if loan is not hispanic or latino
		elif self.inputs['a ethn'] == '2' and self.inputs['co ethn'] != '1':
			self.inputs['ethnicity'] = 1

		elif (self.inputs['a ethn'] == '3' or self.inputs['a ethn'] == '4') and (self.inputs['co ethn'] != '1' and self.inputs['co ethn'] != '2'):
			self.inputs['ethnicity'] = 3
		else:
			print "error loan not aggregated"

		#print self.inputs['a ethn'], 'applicant ethnicity'
		#print self.inputs['co ethn'], 'co applicant ethnicity'
		#print self.inputs['ethnicity'], 'ethnicity result'

	def parse_inputs(self, rows):
		#parsing inputs for report 3.1
		#self.inputs will be returned to for use in the aggregation function
		#filling the applicant and co-applicant race code lists (5 codes per applicant)
		a_race = [race for race in rows[1:6]]
		co_race = [race for race in rows[6:11]]
		#convert ' ' entries to 0 for easier comparisons and loan aggregation
		for i in range(0, 5):
			if a_race[i] == ' ':
				a_race[i] = 0
		for i in range(0,5):
			if co_race[i] == ' ':
				co_race[i] = 0

		#convert string entries to int for easier comparison and loan aggregation
		a_race = [int(race) for race in a_race]
		co_race = [int(race) for race in co_race]

		#add data elements to dictionary
		self.inputs['a ethn'] = rows[11]
		self.inputs['co ethn'] = rows[12]
		self.inputs['income'] = rows[13]
		self.inputs['rate spread'] = rows[14]
		self.inputs['lien status'] = rows[15]
		self.inputs['hoepa flag'] = rows[16]
		self.inputs['purchaser'] = int(rows[17])
		self.inputs['loan value'] = rows[18]
		self.inputs['a race'] = a_race
		self.inputs['co race']= co_race
		self.inputs['joint status'] = ''
		self.inputs['race'] = ''
		self.inputs['app non white flag'] = ''
		self.inputs['co non white flag'] = ''
		self.inputs['sequence'] = rows[19] # the sequence number to track loans in error checking
		self.inputs['year'] = rows[20]
		self.inputs['state code'] = rows[21]
		self.inputs['census tract'] = rows[22]
		self.inputs['county code'] = rows[23]

		#the minority count is the count of minority races listed for the primary applicant
		minority_count = 0
		for race in self.inputs['a race']:
			if race < 5 and race > 0:
				minority_count += 1
		self.inputs['minority count'] = minority_count



	def set_joint_status(self):
		#loop over all elements in both race lists to flag presence of minority race
		#assigning non-white boolean flags for use in joint race status and minority status checks
		#set boolean flag for white/non-white status for applicant
		#need to check App A ID2 for race 6
		for i in range(0,4):
			if self.inputs['a race'][i] < 5 and self.inputs['a race'][i] != 0:
				self.inputs['app non white flag'] = True #flag true if applicant listed a minority race
				break
			elif self.inputs['a race'][i] == 5:
				self.inputs['app non white flag'] = False

		for i in range(0,4):
			if self.inputs['co race'][i] < 5 and self.inputs['co race'][i] != 0:
				self.inputs['co non white flag'] = True #flag true if co-applicant exists and has a non-white race listed
				break
			elif self.inputs['co race'][i] == 5:
				self.inputs['co non white flag'] = False

		#joint status exists if one borrower is white and one is non-white
		#check to see if joint status exists
		if self.inputs['app non white flag'] == False and self.inputs['co non white flag'] == False:
			self.inputs['joint status'] = False #flag false if both applicant and co-applicant are white
		elif self.inputs['app non white flag'] == True and self.inputs['co non white flag'] == True:
			self.inputs['joint status'] = False #flag false if both applicant and co-applicant are minority
		elif self.inputs['app non white flag'] == True and self.inputs['co non white flag'] ==  False:
			self.inputs['joint status'] = True #flag true if one applicant is minority and one is white
		elif self.inputs['app non white flag'] == False and self.inputs['co non white flag'] == True:
			self.inputs['joint status'] = True #flag true if one applicant is minority and one is white


	def set_minority_status(self): #inputs is a dictionary, app non white flag and co non white flag are booleans
		#determine minority status
		#minority_status = False
		#if either applicant reported a non-white race or an ethinicity of hispanic or latino then minority status is true
		if self.inputs['app non white flag'] == True or self.inputs['co non white flag'] == True or self.inputs['a ethn'] == '1' or self.inputs['co ethn'] == '1':
			self.inputs['minority status'] = 1

		#if both applicants reported white race and non-hispanic/latino ethnicity then minority status is false
		elif self.inputs['app non white flag'] == False and self.inputs['co non white flag'] == False and self.inputs['a ethn']  == '2' and self.inputs['co ethn'] == '2':
			self.inputs['minority status'] = 0

	def set_race(self): #joint_status is a boolean, inputs is a list
		#if one white and one minority race are listed, use the minority race
		#race options are: joint, 1 through 5, 2 minority, not reported
		#if the entry is 'joint' then the loan is aggregated as 'joint'
		#create a single race item instead of a list to use in comparisons to build aggregates

		if self.inputs['joint status'] == True:
			self.inputs['race'] = 'joint'
		#determine if the loan will be filed as 'two or more minority races'
		#if two minority races are listed, the loan is 'two or more minority races'
		#if any combination of two or more race fields are minority then 'two or more minority races'
		elif self.inputs['minority count'] > 1:
			self.inputs['race'] = '2 minority'

		#if only the first race field is used, use the first filed
		elif self.inputs['a race'][0] != 0 and self.inputs['a race'][1] == 0 and self.inputs['a race'][2] == 0 and self.inputs['a race'][3] == 0 and self.inputs['a race'][4] == 0:
			self.inputs['race'] = self.inputs['a race'][0] #if only one race is reported, and joint status and minority status are false, set race to first race

		elif self.inputs['a race'][0] == 0 and self.inputs['a race'][1] == 0 and self.inputs['a race'][2] == 0 and self.inputs['a race'][3] == 0 and self.inputs['a race'][4] == 0:
			self.inputs['race'] = 'not reported' #if all race fields are blank, set race to 'not reported'

		else:
			for i in range(1,4):
				if i in self.inputs['a race']: #check if a minority race is present in the race array
					self.inputs['race'] = self.inputs['a race'][0]
					if self.inputs['a race'][0] == 5:
						for code in self.inputs['a race']:
							if code < 5 and code != 0: #if first race is white, but a minority race is reported, set race to the first minority reported
								self.inputs['race'] = code
								break #exit on first minority race

	def table_3_aggregator(self):
		#convert the race to a text to access the JSON structure to aggregate and store data
		#may be able to combine this with the integer setting step below
		if self.inputs['race'] == 1:
			race = 'American Indian/Alaska Native'
		elif self.inputs['race'] == 2:
			race = 'Asian'
		elif self.inputs['race'] == 3:
			race = 'Black'
		elif self.inputs['race'] == 4:
			race = 'Pacific Islander'
		elif self.inputs['race'] == 5:
			race = 'White'
		elif self.inputs['race'] == 6:
			race = 'Not Provided'
		elif self.inputs['race']== 7:
			race = 'Not Applicable'
		elif self.inputs['race'] == '2 minority':
			race = self.inputs['race']
		elif self.inputs['race'] == 'joint':
			race = self.inputs['race']
		elif self.inputs['race'] == 'not reported':
			race = self.inputs['race']
		else:
			print race, 'ERROR'

		#set race_code to integers for use in JSON structure lists
		if self.inputs['race'] == 1:
			race_code = 0
		elif self.inputs['race'] == 2:
			race_code = 1
		elif self.inputs['race'] == 3:
			race_code = 2
		elif self.inputs['race'] == 4:
			race_code = 3
		elif self.inputs['race'] == 5:
			race_code = 4
		elif self.inputs['race'] == 6:
			race_code = 5
		elif self.inputs['race'] == 7:
			race_code = 6
		elif self.inputs['race'] == '2 minority':
			race_code = 7
		elif self.inputs['race'] == 'joint':
			race_code = 8
		elif self.inputs['race'] == 'not reported':
			race_code = 9

		#set purchaser code to purchaser name to access JSON structre to aggregate and store data
		if self.inputs['purchaser'] == 0:
			purchaser = 'Loan was not originated or purchased in calendar year'
		elif self.inputs['purchaser'] == 1:
			purchaser = 'Fannie Mae'
		elif self.inputs['purchaser'] == 2:
			purchaser = 'Ginnie Mae'
		elif self.inputs['purchaser'] == 3:
			purchaser = 'Freddie Mac'
		elif self.inputs['purchaser'] == 4:
			purchaser = 'Farmer Mac'
		elif self.inputs['purchaser'] == 5:
			purchaser = 'Private securitization'
		elif self.inputs['purchaser'] == 6:
			purchaser = 'Commercial bank'
		elif self.inputs['purchaser'] == 7:
			purchaser = 'Insurance co., Credit Union, Mortgage Bank or Finance co.'
		elif self.inputs['purchaser'] == 8:
			purchaser = 'Affiliate Institution'
		elif self.inputs['purchaser']== 9:
			purchaser = 'Other purchaser'
		else:
			purchaser = 'not purchased'

		#set ethnicity code to a name for accessing the JSON structure
		if self.inputs['ethnicity'] == 0:
			ethnicity = 'Hispanic or Latino'
		elif self.inputs['ethnicity'] == 1:
			ethnicity = 'Not Hispanic or Latino'
		elif self.inputs['ethnicity'] == 2:
			ethnicity = 'Joint'
		elif self.inputs['ethnicity'] == 3:
			ethnicity = 'Ethnicity not available'
		#test prints for data validation
		#print "\n\n", race_code, "race code"
		#print self.inputs['purchaser'], "purchaser"
		#print self.inputs['loan value'], "amount "
		#print self.table_3['borrower-characteristics'][0]['types'][race_code]['purchasers'][self.inputs['purchaser']]

		#aggregate loans by race and purchaser
		#check if the race and the purchaser listed for the loan exists in the data structure, if so, add them to the values in the JSON structure
		#if not, print 'loan not added'
		if race in self.table_3['borrower-characteristics'][0]['types'][race_code]['name'] and purchaser in self.table_3['borrower-characteristics'][0]['types'][race_code]['purchasers'][self.inputs['purchaser']]['name']:
			self.table_3['borrower-characteristics'][0]['types'][race_code]['purchasers'][self.inputs['purchaser']]['count'] += 1
			self.table_3['borrower-characteristics'][0]['types'][race_code]['purchasers'][self.inputs['purchaser']]['value'] += int(self.inputs['loan value'])

		else:
			print "loan not added, code not present - race"

		#aggregate loans by ethnicity and purchaser
		#print ethnicity
		if ethnicity in self.table_3['borrower-characteristics'][1]['types'][self.inputs['ethnicity']]['name'] and purchaser in self.table_3['borrower-characteristics'][1]['types'][self.inputs['ethnicity']]['purchasers'][self.inputs['purchaser']]['name']:
			self.table_3['borrower-characteristics'][1]['types'][self.inputs['ethnicity']]['purchasers'][self.inputs['purchaser']]['count'] += 1
			self.table_3['borrower-characteristics'][1]['types'][self.inputs['ethnicity']]['purchasers'][self.inputs['purchaser']]['value'] += int(self.inputs['loan value'])
		else:
			print "loan not added, code not present - ethnicity"

		#aggregate loans by minority status and purchaser
		if ethnicity in self.table_3['borrower-characteristics'][1]['types'][self.inputs['ethnicity']]['name'] and purchaser in self.table_3['borrower-characteristics'][1]['types'][self.inputs['ethnicity']]['purchasers'][self.inputs['purchaser']]['name']:
			self.table_3['borrower-characteristics'][2]['types'][self.inputs['minority status']]['purchasers'][self.inputs['purchaser']]['count'] += 1
			self.table_3['borrower-characteristics'][2]['types'][self.inputs['minority status']]['purchasers'][self.inputs['purchaser']]['value'] += int(self.inputs['loan value'])


	#Race: American Indian or Alaska NAtive(1), Asian(2), Black(3), Native Hawaiian or Pacific Islander(4), White(5), Not provided(6), Not applicable(7), no co-applicant(8)
	#joint definition: one minority race and one white
	#2 minority definition: both applicants of minority race
	#Ethnicity: Hispanic or Latino(1), not Hispanic or Latino(2), not provided(3), not applicable(4), no co-applicant(5)
	#joint Hispanic or Latino / not Hispanic or Latino definition
	#Income is relied upon income rounded?
	#Lien status: first lien(1), subordinate lien(2), not secured(3), not applicable purchased loans(4)
	#purchaser codes: Fannie(1), Ginnie(2), Freddie(3), Farmer(4), Private(5), Commercial(6), Insurance(7), Affiliate(8), Other(9)
	#hoepa status: hoepa loan(1), non-hoepa loan(2)
	def report_3_main(self, location, credentials):
		import psycopg2 #to access a SQL database
		dbname = credentials[0]
		user = credentials[1]
		host = credentials[2]
		password = credentials[3]
		cred = (dbname, user, host, password)
		connect_string = "dbname=%s user=%s host=%s password=%s" % (dbname, user, host, password)

		#attempte a connection to the SQL database hosting the LAR information
		try: #this login information must be set appropriately, it is currently set to localhost with a specified user
			conn = psycopg2.connect(connect_string)
		#if database connection results in an error print the following
		except:
			print "I am unable to connect to the database"
		#create a cursor object to use with the SQL database
		cur = conn.cursor()

		#count the number of rows to be selected for the geography
		SQL = "SELECT COUNT(geocode) FROM LAR_TEST WHERE statecode = %s and countycode = %s and censustractnumber = %s;"
		cur.execute(SQL, location) #location is a list passed in from the controller object. The list order must match the variable order in the SQL string
		#produces a tuple that is a count of the number of records in the selected geography
		rows_selected = cur.fetchone()
		#determine how many rows were selected, this will be used to set the loop range when aggregating all loans
		count = rows_selected[0]

		#set the SQL statement to select the needed fields to aggregate loans for the table_3 JSON structure
		SQL = '''SELECT
			geocode, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4,	coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, ratespeed, lienstatus, hoepastatus,
			purchasertype, loanamount,sequencenumber, asofdate, statecode, censustractnumber, countycode
		FROM LAR_TEST WHERE statecode = %s and countycode = %s and censustractnumber = %s; '''

		cur.execute(SQL, location)


		for i in range(0, count):
			#pull one record from the database query
			rows = cur.fetchone()
			#parse the selected row and rename for readability
			#all data is stored in the inputs dictionary
			self.parse_inputs(rows)
			self.table_3['year'] = self.inputs['year'] #set the year of the report
			self.table_3['msa-md']['id'] = self.inputs['census tract'] #set MSA-MD ID to tract number
			self.table_3['msa-md']['name'] = self.inputs['county code'] #set count name. This will need a dictionary of county names and codes
			self.table_3['msa-md']['state'] = self.inputs['state code'] #set the state code. This will need a dictionary of state names and codes

			#joint status indicates that one borrower is white and the other is non-white
			self.set_joint_status()

			#set the race for use in the table_3_aggregator function
			#race options are: joint, 1 through 5, 2 minority, not reported
			#if one white and one minority race are listed, use the minority race
			self.set_race()

			#set the ethnicity of the loan
			self.set_ethnicity()

			#determine minority status: if either applicant is non-white or has hispanic or latino ethinicity
			#then the loan is a minority loan
			self.set_minority_status()

			#table 3-1 logic filters
			#counts loans and aggregates values by race and purchaser
			self.table_3_aggregator()


	def print_report_3(self): #prints the JSON structure to the terminal
		for i in range(0, 10):
			print "\n"
			print self.table_3['borrower-characteristics'][0]['types'][i]['name'], "\n", "*" * 10
			for j in range(0,10):
				print "name", self.table_3['borrower-characteristics'][0]['types'][i]['purchasers'][j]['name']
				print "count", self.table_3['borrower-characteristics'][0]['types'][i]['purchasers'][j]['count']
				print "value", self.table_3['borrower-characteristics'][0]['types'][i]['purchasers'][j]['value']

	def write_report_3(self, name): #writes the JSON structure to a file
		import json
		with open(name, 'w') as outfile:
			 json.dump(self.table_3, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

