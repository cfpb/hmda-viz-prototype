
class demographics(object):
	#holds all the functions for setting race, minority status, and ethnicity for FFIEC A&D reports
	#this class is called when the parse_txx function is called by the controller
	def __init__(self):
		self.result = 0

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
			return None

	def rate_spread_index_3_2(self, rate):
		#sets the rate spread variable to an index number for aggregation in the JSON object
		#indexes match the position on the report
		if rate == 'NA   ' or rate == '     ':
			return 8
		elif float(rate) >= 1.5 and float(rate) <= 1.99:
			return 0
		elif float(rate) >= 1.5 and float(rate) <= 2.49:
			return 1
		elif float(rate) >= 1.5 and  float(rate) <= 2.99:
			return 2
		elif float(rate) >= 1.5 and float(rate) <= 3.49:
			return 3
		elif float(rate) >= 1.5 and  float(rate) <= 4.49:
			return 4
		elif float(rate) >= 1.5 and  float(rate) <= 5.49:
			return 5
		elif float(rate) >= 1.5 and  float(rate) <= 6.49:
			return 6
		elif float(rate) >= 1.5 and  float(rate) >= 6.50:
			return 7
		else:
			return None

	def rate_spread_index_11_x(self, rate):
		#indexes the rate spreads for use in table 11.x
		if rate == 'NA   ' or rate == '     ':
			return 0
		#index 1 is reserved for 'reported pricing data' and will be handled during aggregation
		elif float(rate) >= 1.5 and float(rate) <= 1.99:
			return 2
		elif float(rate) >= 1.5 and float(rate) <= 2.49:
			return 3
		elif float(rate) >= 1.5 and float(rate) <= 2.99:
			return 4
		elif float(rate) >= 1.5 and float(rate) <= 3.99:
			return 5
		elif float(rate) >= 1.5 and float(rate) <= 4.99:
			return 6
		elif float(rate) >= 1.5 and float(rate) <= 5.99:
			return 7
		elif float(rate) > 5.99:
			return 8
		else:
			return None

	def minority_count(self, a_race):
		#the minority count is the count of minority races listed for the primary applicant
		#if minority count is > 2, then the race is set to 2 minority
		minority_count = 0
		for race in a_race:
			if race < 5 and race > 0: #if a race was entered (not blank not a non-race category code, increment the minority count by 1 if the race was non-white)
				minority_count += 1
		return minority_count

	def set_non_white(self, race_list): #pass in a list of length 5, return a boolean
		for i in range(1, 5):
			if i in race_list:
				return True
		if 5 in race_list:
			return False
		else:
			return None

	def set_joint(self, inputs): #takes a dictionary 'inputs' which is held in the controller(?) object and used to process each loan row
		#set default return to true or false and then only run 1 check
		#joint status exists if one borrower is white and one is non-white
		#check to see if joint status exists
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
		#   return 1
		else:
			return None

	def set_ethnicity(self, inputs):
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
		#   return  0
		#elif (inputs['a ethn'] == ' ' or inputs['a ethn'] == '3' or inputs['a ethn'] == '4' or inputs['a ethn'] == '5') and inputs['co ethn'] == '1': #co applicant hispanic, applicant blank, not available
		#   return  0
		#determine if loan is not hispanic or latino
		elif inputs['a ethn'] == '2' and inputs['co ethn'] != '1': #applicant not hispanic (positive entry), co applicant not hispanic (all other codes)
			return  1
		#elif inputs['a ethn'] != '1' and inputs['co ethn'] == '2': #co applicant not hispanic (positive entry), applicant not hispanic (all other codes)
		#   return  1
		elif (inputs['a ethn'] == '3' or inputs['a ethn'] == '4') and (inputs['co ethn'] != '1' and inputs['co ethn'] != '2'): #no applicant ethnicity information, co applicant did not mark ethnicity positively
			return  3
		else:
			return 3
			print "error setting ethnicity"

	def make_race_list(self, a_race):
		#a_race = [row['applicantrace1'], row['applicantrace2'], row['applicantrace3'],row['applicantrace4'],row['applicantrace5']]
		for i in range(0, 5): #convert ' ' entries to 0 for easier comparisons and loan aggregation
			if a_race[i] == ' ':
				a_race[i] = 0
			else:
				a_race[i] = int(a_race[i])
		return [int(race) for race in a_race] #convert string entries to int for easier comparison and loan aggregation

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

