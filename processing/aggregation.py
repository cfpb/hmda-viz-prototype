import numpy
from decimal import Decimal
import decimal

class aggregate(object): #aggregates LAR rows by appropriate characteristics to fill the JSON files

	def __init__(self):
		self.small_tract_flags = {} #to hold 11 digit tract number as key and small county flag as value
		self.purchaser_first_lien_rates = ['Fannie Mae first rates', 'Ginnie Mae first rates', 'Freddie Mac first rates', 'Farmer Mac first rates', 'Private Securitization first rates', 'Commercial bank, savings bank or association first rates', 'Life insurance co., credit union, finance co. first rates', 'Affiliate institution first rates', 'Other first rates']
		self.purchaser_junior_lien_rates = ['Fannie Mae junior rates', 'Ginnie Mae junior rates', 'Freddie Mac junior rates', 'Farmer Mac junior rates', 'Private Securitization junior rates', 'Commercial bank, savings bank or association junior rates', 'Life insurance co., credit union, finance co. junior rates', 'Affiliate institution junior rates', 'Other junior rates']
		self.purchaser_first_lien_weight = ['Fannie Mae first weight', 'Ginnie Mae first weight', 'Freddie Mac first weight', 'Farmer Mac first weight', 'Private Securitization first weight', 'Commercial bank, savings bank or association first weight', 'Life insurance co., credit union, finance co. first weight', 'Affiliate institution first weight', 'Other first weight']
		self.purchaser_junior_lien_weight = ['Fannie Mae junior weight', 'Ginnie Mae junior weight', 'Freddie Mac junior weight', 'Farmer Mac junior weight', 'Private Securitization junior weight', 'Commercial bank, savings bank or association junior weight', 'Life insurance co., credit union, finance co. junior weight', 'Affiliate institution junior weight', 'Other junior weight']
		self.race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Other Pacific Islander', 'White', '2 or more minority races', 'Joint (White/Minority Race)', 'Race Not Available']
		self.rate_spreads = ['No Reported Pricing Data', 'Reported Pricing Data', '1.50 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.99', '4.00 - 4.99', '5.00 - 5.99', '6 or more', 'Mean', 'Median']
		self.race_rate_list = self.create_rate_lists(len(self.race_names))
		#rate lists for tables 11 and 12
		self.ethnicity_rate_list = self.create_rate_lists(4)
		self.minority_rate_list = self.create_rate_lists(2)
		self.income_rate_list = self.create_rate_lists(6)
		self.gender_rate_list = self.create_rate_lists(4)
		self.composition_rate_list = self.create_rate_lists(5)
		self.tract_income_rate_list = self.create_rate_lists(4)
		#weight lists for tables 11 and 12
		self.race_weight_list = self.create_rate_lists(len(self.race_names))
		self.ethnicity_weight_list = self.create_rate_lists(4)
		self.minority_weight_list = self.create_rate_lists(2)
		self.income_weight_list = self.create_rate_lists(6)
		self.gender_weight_list = self.create_rate_lists(4)
		self.composition_weight_list = self.create_rate_lists(5)
		self.tract_income_weight_list = self.create_rate_lists(4)
		#rate lists for table B
		self.table_B_rates = self.create_rate_lists(2) #lists by property type. 0 = single family, 1 = manufactured
		for i in range(0, len(self.table_B_rates)):
			self.table_B_rates[i] = self.create_rate_lists(3) #lien status lists 0=first lien, 1=junior lien, 2=no lien
			for j in range(0, len(self.table_B_rates[i])):
				self.table_B_rates[i][j] = self.create_rate_lists(3) #loan purpose lists. 0=home purchase, 1=refinance, 2=home improvement

		#weight lists for table B
		self.table_B_weights = self.create_rate_lists(2) #lists by property type. 0 = single family, 1 = manufactured
		for i in range(0, len(self.table_B_weights)):
			self.table_B_weights[i] = self.create_rate_lists(3) #lien status lists 0=first lien, 1=junior lien, 2=no lien
			for j in range(0, len(self.table_B_weights[i])):
				self.table_B_weights[i][j] = self.create_rate_lists(3) #loan purpose lists. 0=home purchase, 1=refinance, 2=home improvement

	def create_rate_lists(self, length):
		new_list = []
		for x in range(0, length):
			new_list.append([])
		return new_list

	def fill_by_characteristics(self, container, inputs, section, section_index, key, key_index, section2, section2_index):
		container[section][section_index][key][key_index][section2][section2_index]['count'] += 1
		container[section][section_index][key][key_index][section2][section2_index]['value'] += int(inputs['loan value'])

	def fill_by_characteristics_NA(self, container, inputs, section, section_index, key, key_index, section2, section2_index):
		container[section][section_index][key][key_index][section2][section2_index]['count'] = 'NA'
		container[section][section_index][key][key_index][section2][section2_index]['value'] = 'NA'

	def calc_weighted_median(self, rate_list, weight_list):
		#to find the weighted median, step throught the rates using a step size that is the average loan amount
		#when number of loans divided by 2 steps have been taken, return the associated rate spread
		if len(rate_list) > 0 and len(weight_list) > 0:#check for divide by 0 errors
			rate_list, weight_list = zip(*sorted(zip(rate_list, weight_list))) #sort both lists by rate- this converts the lists to tuples
			step_size = round(Decimal(sum(weight_list)) / len(weight_list),2) #get a managable decimal length
			steps_needed = Decimal(round(len(weight_list) / Decimal(2),1))
			count = 0 #count is used to choose find the index of the rate for the median weight, can this be simplified?
			for i in range(0, len(weight_list)):
				step_taken = Decimal(weight_list[i] / Decimal(step_size))
				steps_needed -= step_taken
				if round(steps_needed,2) <= 0:
					return rate_list[count]
				count +=1

	def fill_weighted_medians_11_12(self, container, inputs):
		#strings need to be converted to floats for external data requests
		for i in range(0, len(self.race_rate_list)):
			container['borrowercharacteristics'][0]['races'][i]['pricinginformation'][9]['value'] = str(self.calc_weighted_median(self.race_rate_list[i], self.race_weight_list[i]))
		for i in range(0, len(self.ethnicity_rate_list)):
			container['borrowercharacteristics'][1]['ethnicities'][i]['pricinginformation'][9]['value'] = str(self.calc_weighted_median(self.ethnicity_rate_list[i], self.ethnicity_weight_list[i]))
		for i in range(0, len(self.minority_rate_list)):
			container['borrowercharacteristics'][2]['minoritystatuses'][i]['pricinginformation'][9]['value'] = str(self.calc_weighted_median(self.minority_rate_list[i], self.minority_weight_list[i]))
		for i in range(0, len(self.income_rate_list)):
			container['borrowercharacteristics'][3]['incomes'][i]['pricinginformation'][9]['value'] = str(self.calc_weighted_median(self.income_rate_list[i], self.income_weight_list[i]))
		for i in range(0, len(self.gender_rate_list)):
			container['borrowercharacteristics'][4]['genders'][i]['pricinginformation'][9]['value'] = str(self.calc_weighted_median(self.gender_rate_list[i], self.gender_weight_list[i]))
		for i in range(0, len(self.composition_rate_list)):
			container['censuscharacteristics'][0]['compositions'][i]['pricinginformation'][9]['value'] = str(self.calc_weighted_median(self.composition_rate_list[i], self.composition_weight_list[i]))
		for i in range(0, len(self.tract_income_rate_list)):
			container['censuscharacteristics'][1]['incomes'][i]['pricinginformation'][9]['value'] = str(self.calc_weighted_median(self.tract_income_rate_list[i], self.tract_income_weight_list[i]))

	def calc_weighted_mean_11_12(self, rate_list, weight_list):
		weighted_rates = []
		percent_weights = [x / sum(weight_list) for x in weight_list]
		if len(rate_list) > 0 and len(weight_list) > 0:
			for i in range(0, len(rate_list)):
				weighted_rates.append(rate_list[i] * percent_weights[i])
			return round(sum(weighted_rates),2)# / sum(percent_weights[i]),2)
		else:
			return None

	def fill_weighted_means_11_12(self, container, inputs):
		for i in range(0, len(self.race_rate_list)):
			container['borrowercharacteristics'][0]['races'][i]['pricinginformation'][8]['value'] = str(self.calc_weighted_mean_11_12(self.race_rate_list[i], self.race_weight_list[i]))#self.calc_weighted_mean_11_12(self.race_rate_list[i], self.race_weight_list[i]) #numpy.average(numpy.array(self.race_weight_list[i],dtype=numpy.dtype(decimal.Decimal)), weights=numpy.array(self.race_weight_list[i],dtype=numpy.dtype(decimal.Decimal)))
		for i in range(0, len(self.ethnicity_rate_list)):
			container['borrowercharacteristics'][1]['ethnicities'][i]['pricinginformation'][8]['value'] = str(self.calc_weighted_mean_11_12(self.ethnicity_rate_list[i], self.ethnicity_weight_list[i]))
		for i in range(0, len(self.minority_rate_list)):
			container['borrowercharacteristics'][2]['minoritystatuses'][i]['pricinginformation'][8]['value'] = str(self.calc_weighted_mean_11_12(self.minority_rate_list[i], self.minority_weight_list[i]))
		for i in range(0, len(self.income_rate_list)):
			container['borrowercharacteristics'][3]['incomes'][i]['pricinginformation'][8]['value'] = str(self.calc_weighted_mean_11_12(self.income_rate_list[i], self.income_weight_list[i]))
		for i in range(0, len(self.gender_rate_list)):
			container['borrowercharacteristics'][4]['genders'][i]['pricinginformation'][8]['value'] = str(self.calc_weighted_mean_11_12(self.gender_rate_list[i], self.gender_weight_list[i]))
		for i in range(0, len(self.composition_rate_list)):
			container['censuscharacteristics'][0]['compositions'][i]['pricinginformation'][8]['value'] = str(self.calc_weighted_mean_11_12(self.composition_rate_list[i], self.composition_weight_list[i]))
		for i in range(0, len(self.tract_income_rate_list)):
			container['censuscharacteristics'][1]['incomes'][i]['pricinginformation'][8]['value'] = str(self.calc_weighted_mean_11_12(self.tract_income_rate_list[i], self.tract_income_weight_list[i]))

	def fill_totals_3_1(self, container, inputs): #aggregate total of purchased loans for table 3-1
		container['total']['purchasers'][inputs['purchaser']]['count'] +=1
		container['total']['purchasers'][inputs['purchaser']]['value'] += int(inputs['loan value'])

	def compile_report_3_1(self, table31, inputs):  #calls aggregation functions to fill JSON object for table 3-1
		self.fill_by_characteristics(table31, inputs, 'borrowercharacteristics', 0, 'races', inputs['race'], 'purchasers', inputs['purchaser'])#aggregate loan by race
		self.fill_by_characteristics(table31, inputs, 'borrowercharacteristics', 1, 'ethnicities', inputs['ethnicity'], 'purchasers', inputs['purchaser'])#aggregate loan by ethnicity
		if inputs['minority status'] < 2:
			self.fill_by_characteristics(table31, inputs, 'borrowercharacteristics', 2, 'minoritystatuses', inputs['minority status'], 'purchasers', inputs['purchaser'])#aggregate loan by minority status (binary determined by race and ethnicity)
		if inputs['income bracket'] < 6: #income index outside bounds of report 3-1
			self.fill_by_characteristics(table31, inputs, 'borrowercharacteristics', 3, 'applicantincomes', inputs['income bracket'], 'purchasers', inputs['purchaser'])#aggregates by ratio of appicant income to tract median income (census)
		if inputs['minority percent index'] < 5: #minority percent not available
			self.fill_by_characteristics(table31, inputs, 'censuscharacteristics', 0, 'tractpctminorities', inputs['minority percent index'], 'purchasers', inputs['purchaser'])#aggregates loans by percent of minority residents (census)
		if inputs['tract income index'] < 4: #income ratio not available or outside report 3-1 bounds
			self.fill_by_characteristics(table31, inputs, 'censuscharacteristics', 1, 'incomelevels', inputs['tract income index'], 'purchasers', inputs['purchaser']) #aggregates loans by census tract income rating - low/moderate/middle/upper
		self.fill_totals_3_1(table31, inputs) #aggregate totals for each purchaser
		return table31

	def fill_by_pricing_status_3_2(self, container, inputs): #aggregate loans by lien status
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

	def fill_by_rate_spread_3_2(self, container, inputs): #aggregate loans by rate spread index
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

	def fill_by_hoepa_status_3_2(self, container, inputs): #aggregate loans subject to HOEPA
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

	def fill_by_mean_3_2(self, container, inputs): #aggregate loans by mean of rate spread
		for n in range(0,9):
			if float(container['pricinginformation'][1]['purchasers'][n]['firstliencount']) > 0 and inputs[self.purchaser_first_lien_rates[n]] > 0: #bug fix for divide by 0 errors
				container['points'][8]['purchasers'][n]['firstliencount'] = round(numpy.mean(numpy.array(inputs[self.purchaser_first_lien_rates[n]])),2)

			if float(container['pricinginformation'][1]['purchasers'][n]['juniorliencount']) > 0 and inputs[self.purchaser_junior_lien_rates[n]] > 0: #bug fix for divide by 0 errors
				container['points'][8]['purchasers'][n]['juniorliencount'] = round(numpy.mean(numpy.array(inputs[self.purchaser_junior_lien_rates[n]]), dtype=numpy.float64),2)

	def fill_by_weighted_mean_3_2(self, container, inputs): #aggregate loans by weighted mean of rate spread

		for n in range(0,9):
			if float(container['pricinginformation'][1]['purchasers'][n]['firstliencount']) > 0 and inputs[self.purchaser_first_lien_weight[n]] > 0: #bug fix for divide by 0 errors
				nd_first_rates = numpy.array(inputs[self.purchaser_first_lien_rates[n]])
				nd_first_weights = numpy.array(inputs[self.purchaser_first_lien_weight[n]])
				container['points'][8]['purchasers'][n]['firstlienvalue'] = round(numpy.average(nd_first_rates, weights=nd_first_weights),2)#round(inputs[self.purchaser_first_lien_weight[n]]/float(container['pricinginformation'][1]['purchasers'][n]['firstlienvalue']),2)

			if float(container['pricinginformation'][1]['purchasers'][n]['juniorliencount']) > 0 and inputs[self.purchaser_junior_lien_weight[n]] > 0: #bug fix for divide by 0 errors
				nd_junior_rates = numpy.array(inputs[self.purchaser_junior_lien_rates[n]])
				nd_junior_weights = numpy.array(inputs[self.purchaser_junior_lien_rates[n]])
				container['points'][8]['purchasers'][n]['juniorlienvalue'] = round(numpy.average(nd_junior_rates, weights=nd_junior_weights),2)#round(inputs[self.purchaser_junior_lien_weight[n]]/float(container['pricinginformation'][1]['purchasers'][n]['juniorlienvalue']),2)

	def fill_weight_lists_3_2(self, inputs): #add all loan values to a list to find means and medians for table 3-2
		if inputs['rate spread'] != 'NA   ' and inputs['rate spread'] != '     ':

			if inputs['lien status'] =='1':
				inputs[self.purchaser_first_lien_weight[inputs['purchaser']]].append(int(inputs['loan value']))
			elif inputs['lien status'] == '2':
				inputs[self.purchaser_junior_lien_weight[inputs['purchaser']]].append(int(inputs['loan value']))

	def fill_rate_lists_3_2(self, inputs): #add all rate spreads to a list to find the mean and median rate spreads for table 3-2
		if inputs['rate spread'] == 'NA   ' or inputs['rate spread'] == '     ':
			pass
		elif inputs['lien status'] == '1': #add to first lien rate spread list
			inputs[self.purchaser_first_lien_rates[inputs['purchaser']]].append(float(inputs['rate spread']))
		elif inputs['lien status'] == '2': #add to junior lien rate spread list
			inputs[self.purchaser_junior_lien_rates[inputs['purchaser']]].append(float(inputs['rate spread']))

	def fill_by_median_3_2(self, container, inputs): #puts the median rate spread in the JSON object
		for n in range(0,9):
			#first lien median column
			if len(inputs[self.purchaser_first_lien_rates[n]]) > 0: #check to see if the array is populated
				container['points'][9]['purchasers'][n]['firstliencount'] = round(numpy.median(numpy.array(inputs[self.purchaser_first_lien_rates[n]])),2) #for normal median
			#junior lien median column
			if len(inputs[self.purchaser_junior_lien_rates[n]]) > 0: #check to see if the array is populated
				container['points'][9]['purchasers'][n]['juniorliencount'] = round(numpy.median(numpy.array(inputs[self.purchaser_junior_lien_rates[n]])),2) #for normal median

	def fill_by_weighted_median_3_2(self, container, inputs): #weighted median function for table 3-2
		for n in range(0,9):
			#first lien weighted median column
			container['points'][9]['purchasers'][n]['firstlienvalue'] = self.calc_weighted_median(inputs[self.purchaser_first_lien_rates[n]], inputs[self.purchaser_first_lien_weight[n]])
			#junior lien weighted median column
			container['points'][9]['purchasers'][n]['juniorlienvalue'] = self.calc_weighted_median(inputs[self.purchaser_junior_lien_rates[n]], inputs[self.purchaser_junior_lien_weight[n]])

	def compile_report_3_2(self, table32, inputs): #calls aggregation functions to fill JSON object for table 3-2
		self.fill_by_pricing_status_3_2(table32, inputs) #aggregate count by lien status
		self.fill_by_rate_spread_3_2(table32, inputs) #aggregate loans by percentage points above APOR as ##.##%
		self.fill_by_hoepa_status_3_2(table32, inputs) #aggregates loans by presence of HOEPA flag
		self.fill_rate_lists_3_2(inputs)
		self.fill_weight_lists_3_2(inputs) #fills the median rate spread for each purchaser
		#mean and median functions are not called here
		#mean and median function must be called outside the control loop

	def compile_report_4_x(self, table4x, inputs): #call functions to fill JSON object for table 4-1 (FHA, FSA, RHS, and VA home purchase loans)
		self.fill_by_4_x_demographics(table4x, inputs, 'races', inputs['race'])
		self.fill_by_4_x_demographics(table4x, inputs, 'ethnicities', inputs['ethnicity'])
		self.fill_by_4_x_demographics(table4x, inputs, 'minoritystatuses', inputs['minority status'])
		self.fill_by_applicant_income_4_x(table4x, inputs) #aggregate loans by applicant income to MSA income ratio
		self.fill_totals_4_x(table4x, inputs) #totals of applications by application disposition

	def fill_by_applicant_income_4_x(self, container, inputs): #aggregate loans by applicant income index
		if inputs['income bracket'] > 5 or inputs['action taken'] == ' ' or inputs['action taken'] > 5: #filter out of bounds indexes before calling aggregations
			pass

		elif inputs['income bracket'] <6 and inputs['action taken'] < 6:
			#aggregate loans by total applications
			container['incomes'][inputs['income bracket']]['dispositions'][0]['count'] += 1 #add to 'applications received'
			container['incomes'][inputs['income bracket']]['dispositions'][0]['value'] += int(inputs['loan value']) #add to 'applications received'
			#aggregate loans by application disposition
			container['incomes'][inputs['income bracket']]['dispositions'][inputs['action taken']]['count'] += 1 #loans by action taken code
			container['incomes'][inputs['income bracket']]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])
		else:
			print "error aggregating income for report 4-1"

	def fill_by_4_x_demographics(self, container, inputs, key, key_index):
		if inputs['action taken'] < 6:
			if key == 'minoritystatuses' and key_index > 1:
				pass #minoritystatuses has 2 indexes 0,1
			else:
				self.fill_4_x(container, inputs, key, key_index, 0, False)
				self.fill_4_x(container, inputs, key, key_index, inputs['action taken'], False)

				if inputs['gender'] < 3:
					self.fill_4_x(container, inputs, key, key_index, 0, True)
					self.fill_4_x(container, inputs, key, key_index, inputs['action taken'], True)

	def fill_4_x(self, container, inputs, key, key_index, action_index, gender_bool):
		if gender_bool == False:
			#aggregate by application disposition
			container[key][key_index]['dispositions'][action_index]['count'] +=1
			container[key][key_index]['dispositions'][action_index]['value'] +=int(inputs['loan value'])
		elif gender_bool == True:
			#aggregate by gender and application disposition
			container[key][key_index]['genders'][inputs['gender']]['dispositions'][action_index]['count'] +=1
			container[key][key_index]['genders'][inputs['gender']]['dispositions'][action_index]['value'] +=int(inputs['loan value'])

	def fill_totals_4_x(self, container, inputs):
		if inputs['action taken'] < 6 and inputs['action taken'] != ' ':
			#aggregates loans for toal application column
			container['total'][0]['count'] += 1
			container['total'][0]['value'] += int(inputs['loan value'])
			#aggregates loans for application dispositions (action taken)
			container['total'][inputs['action taken']]['count'] +=1
			container['total'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def fill_by_5_x_totals(self, container, inputs):
		if inputs['action taken'] > 5:
			pass
		else:
			#aggregates total applications column
			container['total'][0]['count'] +=1
			container['total'][0]['value'] += int(inputs['loan value'])
			#aggregates loans by application disposition (action taken)
			container['total'][inputs['action taken']]['count'] +=1
			container['total'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def fill_by_5_x_demographics(self, container, inputs, index_num, index_name, index_code):
		#index_num: the index of the primary list in the dictionary
		#index_name: the key corresponding to the index number
		#index_code: the code from the inputs dictionary for the row being aggregated
		if inputs['income bracket'] < 5 and inputs['action taken'] < 6:
			container['applicantincomes'][inputs['income bracket']]['borrowercharacteristics'][index_num][index_name][index_code]['dispositions'][0]['count'] += 1 #increment count of applications received by minority status
			container['applicantincomes'][inputs['income bracket']]['borrowercharacteristics'][index_num][index_name][index_code]['dispositions'][0]['value'] += int(inputs['loan value'])
			container['applicantincomes'][inputs['income bracket']]['borrowercharacteristics'][index_num][index_name][index_code]['dispositions'][inputs['action taken']]['count'] += 1 #increment count by action taken and minority status
			container['applicantincomes'][inputs['income bracket']]['borrowercharacteristics'][index_num][index_name][index_code]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def compile_report_5_x(self, table5x, inputs):
		self.fill_by_5_x_demographics(table5x, inputs, 0, 'races', inputs['race'])
		self.fill_by_5_x_demographics(table5x, inputs, 1, 'ethnicities', inputs['ethnicity'])
		if inputs['minority status'] < 2:
			self.fill_by_5_x_demographics(table5x, inputs, 2, 'minoritystatus', inputs['minority status'])
		self.fill_by_5_x_totals(table5x, inputs)

	def fill_by_tract_characteristics(self, container, inputs, json_index, key, key_index, action_index):
		if action_index < 6 and key_index <4:
			container['censuscharacteristics'][json_index][key][key_index]['dispositions'][0]['count'] +=1
			container['censuscharacteristics'][json_index][key][key_index]['dispositions'][0]['value'] +=int(inputs['loan value'])
			container['censuscharacteristics'][json_index][key][key_index]['dispositions'][action_index]['count'] +=1
			container['censuscharacteristics'][json_index][key][key_index]['dispositions'][action_index]['value'] +=int(inputs['loan value'])

	def fill_by_income_ethnic_combo(self, container, inputs):
		if inputs['action taken'] > 5 or inputs['tract income index'] > 3:
			pass
		else:
			container['incomeRaces'][0]['incomes'][inputs['tract income index']]['compositions'][inputs['minority percent index']]['dispositions'][0]['count'] +=1
			container['incomeRaces'][0]['incomes'][inputs['tract income index']]['compositions'][inputs['minority percent index']]['dispositions'][0]['value'] += int(inputs['loan value'])
			container['incomeRaces'][0]['incomes'][inputs['tract income index']]['compositions'][inputs['minority percent index']]['dispositions'][inputs['action taken']]['count'] +=1
			container['incomeRaces'][0]['incomes'][inputs['tract income index']]['compositions'][inputs['minority percent index']]['dispositions'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def get_small_county_flag(self, cur, MSA): #marks tracts with small county flag for report 7
		#does this need to have a tract passed instead of an MSA?
		#msa can be either an MSA or the last 5 of a geoid?
		SQL = '''SELECT small_county, tract FROM tract_to_cbsa_2010
			WHERE geoid_msa = '{msa}';'''.format(msa=MSA)
		cur.execute(SQL,)
		#print cur.fetchall()
		#small_county_flag = cur.fetchall()[0]
		flags = cur.fetchall()
		for i in range(0, len(flags)):
			self.small_tract_flags[flags[i][1]] = str(flags[i][0])
		#print self.small_tract_flags

	def fill_by_geo_type(self, container, inputs, index_num, action_index):
		container['types'][index_num]['dispositions'][action_index]['count'] +=1
		container['types'][index_num]['dispositions'][action_index]['value'] +=int(inputs['loan value'])

	def fill_totals_7_x(self, container, inputs):
		if inputs['action taken'] > 5:
			pass
		else:
			container['total'][0]['count'] += 1
			container['total'][0]['value'] += int(inputs['loan value'])
			container['total'][inputs['action taken']]['count'] += 1
			container['total'][inputs['action taken']]['value'] += int(inputs['loan value'])

	def compile_report_7_x(self, table7x, inputs):
		self.fill_by_tract_characteristics(table7x, inputs, 0, 'compositions', inputs['minority percent index'], inputs['action taken'])
		self.fill_by_tract_characteristics(table7x, inputs, 1, 'incomes', inputs['tract income index'], inputs['action taken'])
		self.fill_by_income_ethnic_combo(table7x, inputs)
		if inputs['small county flag'] == '1':
			self.fill_by_geo_type(table7x, inputs, 0, 0)
			self.fill_by_geo_type(table7x, inputs, 0, inputs['action taken'])
		if inputs['tract to MSA income'] == 4 and inputs['action taken'] < 6:
			self.fill_by_geo_type(table7x, inputs, 1, 0)
			self.fill_by_geo_type(table7x, inputs, 1, inputs['action taken'])
		self.fill_totals_7_x(table7x, inputs)

	def fill_by_denial_percent(self, container, inputs, index_num, key):
		for j in range(0, len(container['applicantcharacteristics'][index_num][key])):
			for i in range(0, len(container['applicantcharacteristics'][index_num][key][j]['denialreasons'])):
				if float(container['applicantcharacteristics'][index_num][key][j]['denialreasons'][9]['count']) >0:
					container['applicantcharacteristics'][index_num][key][j]['denialreasons'][i]['value'] = int(round((container['applicantcharacteristics'][index_num][key][j]['denialreasons'][i]['count'] / float(container['applicantcharacteristics'][index_num][key][j]['denialreasons'][9]['count'])) *100,0))

	def fill_by_denial_reason(self, container, inputs, index_num, key, key_singular):
		for reason in inputs['denial_list']:
			if reason is None:
				pass
			else:
				container['applicantcharacteristics'][index_num][key][inputs[key_singular]]['denialreasons'][9]['count'] +=1 #add to totals
				container['applicantcharacteristics'][index_num][key][inputs[key_singular]]['denialreasons'][reason]['count'] +=1 #adds to race/reason cell

	def compile_report_8_x(self, table8x, inputs):
		self.fill_by_denial_reason(table8x, inputs, 0, 'races', 'race')
		self.fill_by_denial_reason(table8x, inputs, 1, 'ethnicities', 'ethnicity')
		if inputs['minority status'] <2: #pass on loans with no minority status information
			self.fill_by_denial_reason(table8x, inputs, 2, 'minoritystatuses', 'minority status')
		self.fill_by_denial_reason(table8x, inputs, 3, 'genders', 'gender')
		if inputs['income bracket'] <6:
			self.fill_by_denial_reason(table8x, inputs, 4, 'incomes', 'income bracket')

	def compile_report_9_x(self, container, inputs):
		container['medianages'][inputs['median age index']]['loancategories'][inputs['loan type index']]['dispositions'][inputs['action taken']-1]['count'] += 1
		container['medianages'][inputs['median age index']]['loancategories'][inputs['loan type index']]['dispositions'][inputs['action taken']-1]['value'] += int(inputs['loan value'])

		if inputs['occupancy'] == '2' and inputs['property type'] != '3':
			container['medianages'][inputs['median age index']]['loancategories'][5]['dispositions'][inputs['action taken']-1]['count'] += 1
			container['medianages'][inputs['median age index']]['loancategories'][5]['dispositions'][inputs['action taken']-1]['value'] += int(inputs['loan value'])
		if inputs['property type'] == '2':
			container['medianages'][inputs['median age index']]['loancategories'][6]['dispositions'][inputs['action taken']-1]['count'] += 1
			container['medianages'][inputs['median age index']]['loancategories'][6]['dispositions'][inputs['action taken']-1]['value'] += int(inputs['loan value'])

	def fill_11_12_weights(self, inputs):
		if inputs['rate spread'] != 'NA   ' and inputs['rate spread'] != '     ':
			self.race_weight_list[inputs['race']].append(Decimal(inputs['loan value']))
			self.ethnicity_weight_list[inputs['ethnicity']].append(Decimal(inputs['loan value']))
			if inputs['minority status'] < 2:
				self.minority_weight_list[inputs['minority status']].append(Decimal(inputs['loan value']))
			if inputs['income bracket'] < 6:
				self.income_weight_list[inputs['income bracket']].append(Decimal(inputs['loan value']))
			self.gender_weight_list[inputs['gender']].append(Decimal(inputs['loan value']))
			self.composition_weight_list[inputs['minority percent index']].append(Decimal(inputs['loan value']))
			if inputs['tract income index'] < 4:
				self.tract_income_weight_list[inputs['tract income index']].append(Decimal(inputs['loan value']))

	def fill_11_12_rates(self, inputs):
		#race section
		if inputs['rate spread'] != 'NA   ' and inputs['rate spread'] != '     ':
			self.race_rate_list[inputs['race']].append(Decimal(inputs['rate spread']))
			self.ethnicity_rate_list[inputs['ethnicity']].append(Decimal(inputs['rate spread']))
			if inputs['minority status'] < 2:
				self.minority_rate_list[inputs['minority status']].append(Decimal(inputs['rate spread']))

			if inputs['income bracket'] < 6:
				self.income_rate_list[inputs['income bracket']].append(Decimal(inputs['rate spread']))
			self.gender_rate_list[inputs['gender']].append(Decimal(inputs['rate spread']))
			self.composition_rate_list[inputs['minority percent index']].append(Decimal(inputs['rate spread']))
			if inputs['tract income index'] < 4:
				self.tract_income_rate_list[inputs['tract income index']].append(Decimal(inputs['rate spread']))

	def calc_mean_11_12(self, container, list_name, section, section_index, key_plural, ratespread_list):
		for x in range(0, len(list_name)):
			if len(ratespread_list[x]) > 0: #check for divide by 0 errors
				container[section][section_index][key_plural][x]['pricinginformation'][8]['count'] = round(numpy.array(ratespread_list[x]).sum() / len(ratespread_list[x]),2)
				#this access path needs to abstract to match the by_characteristics function
	def fill_means_11_12(self, table_X, build_X):
		self.calc_mean_11_12(table_X, build_X.race_names, 'borrowercharacteristics', 0, 'races', self.race_rate_list)
		self.calc_mean_11_12(table_X, build_X.ethnicity_names, 'borrowercharacteristics', 1, 'ethnicities', self.ethnicity_rate_list)
		self.calc_mean_11_12(table_X, build_X.minority_statuses, 'borrowercharacteristics', 2, 'minoritystatuses', self.minority_rate_list)
		self.calc_mean_11_12(table_X, build_X.applicant_income_bracket, 'borrowercharacteristics', 3, 'incomes', self.income_rate_list)
		self.calc_mean_11_12(table_X, build_X.gender_names2, 'borrowercharacteristics', 4, 'genders', self.gender_rate_list)
		self.calc_mean_11_12(table_X, build_X.tract_pct_minority, 'censuscharacteristics', 0, 'compositions', self.composition_rate_list)
		self.calc_mean_11_12(table_X, build_X.income_bracket_names, 'censuscharacteristics', 1, 'incomes', self.tract_income_rate_list)

	def calc_median_11_12(self, container, list_name, section, section_index, key_plural, ratespread_list):
		for x in range(0, len(list_name)):
			if len(ratespread_list[x]) > 0:
				container[section][section_index][key_plural][x]['pricinginformation'][9]['count'] = round(numpy.median(numpy.array(ratespread_list[x])),2)

	def fill_medians_11_12(self, table_X, build_X):
		self.calc_median_11_12(table_X, build_X.race_names, 'borrowercharacteristics', 0, 'races', self.race_rate_list)
		self.calc_median_11_12(table_X, build_X.ethnicity_names, 'borrowercharacteristics', 1, 'ethnicities', self.ethnicity_rate_list)
		self.calc_median_11_12(table_X, build_X.minority_statuses, 'borrowercharacteristics', 2, 'minoritystatuses', self.minority_rate_list)
		self.calc_median_11_12(table_X, build_X.applicant_income_bracket, 'borrowercharacteristics', 3, 'incomes', self.income_rate_list)
		self.calc_median_11_12(table_X, build_X.gender_names2, 'borrowercharacteristics', 4, 'genders', self.gender_rate_list)
		self.calc_median_11_12(table_X, build_X.tract_pct_minority, 'censuscharacteristics', 0, 'compositions', self.composition_rate_list)
		self.calc_median_11_12(table_X, build_X.income_bracket_names, 'censuscharacteristics', 1, 'incomes', self.tract_income_rate_list)

	def fill_report_11_12(self, table, inputs, key, key_index):
		self.fill_by_characteristics(table, inputs, 'borrowercharacteristics', 0, 'races', inputs['race'], key, key_index)
		self.fill_by_characteristics(table, inputs, 'borrowercharacteristics', 1, 'ethnicities', inputs['ethnicity'], key, key_index)
		if inputs['minority status'] < 2:
			self.fill_by_characteristics(table, inputs, 'borrowercharacteristics', 2, 'minoritystatuses', inputs['minority status'], key, key_index)
		if inputs['income bracket'] < 6:
			self.fill_by_characteristics(table, inputs, 'borrowercharacteristics', 3, 'incomes', inputs['income bracket'], key, key_index)
		self.fill_by_characteristics(table, inputs, 'borrowercharacteristics', 4, 'genders', inputs['gender'], key, key_index)
		if inputs['minority percent index'] <5:
			self.fill_by_characteristics(table, inputs, 'censuscharacteristics', 0, 'compositions', inputs['minority percent index'], key, key_index)
		if inputs['tract income index'] < 4:
			self.fill_by_characteristics(table, inputs, 'censuscharacteristics', 1, 'incomes', inputs['tract income index'], key, key_index)

	def compile_report_11_x(self, table11x, inputs):
		self.fill_11_12_rates(inputs)
		self.fill_11_12_weights(inputs)
		self.fill_report_11_12(table11x, inputs, 'pricinginformation', inputs['rate spread index']) #fill all columns except 'prciing infomraiton reported'
		if inputs['rate spread index'] > 0:
			self.fill_report_11_12(table11x, inputs, 'pricinginformation', 1) #fill the 'pricing information reported column'

	def compile_report_12_1(self, table12x, inputs):
		self.fill_report_11_12(table12x, inputs, 'dispositions', inputs['action taken'])
		if inputs['action taken'] < 6:
			self.fill_report_11_12(table12x, inputs, 'dispositions', 0)

	def compile_report_12_2(self, table12x, inputs):
		self.fill_11_12_rates(inputs)
		self.fill_11_12_weights(inputs)
		self.fill_report_11_12(table12x, inputs, 'pricinginformation', inputs['rate spread index'])
		if inputs['rate spread index'] > 0:
			self.fill_report_11_12(table12x, inputs, 'pricinginformation', 1)

	def compile_report_A_x(self, container, inputs):
		if inputs['action taken index'] < 8:
			if inputs['lien status'] == '1':
				container['dispositions'][0]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['firstliencount'] +=1
				container['dispositions'][inputs['action taken index']]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['firstliencount']+=1
				if inputs['purchaser'] >0:
					container['dispositions'][7]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['firstliencount'] +=1
				if inputs['action taken index'] == 1 and inputs['preapproval'] == '1':
					container['dispositions'][6]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['firstliencount'] +=1

			elif inputs['lien status'] == '2':
				container['dispositions'][0]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['juniorliencount'] +=1
				container['dispositions'][inputs['action taken index']]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['juniorliencount']+=1
				if inputs['purchaser'] >0:
					container['dispositions'][7]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['juniorliencount'] +=1
				if inputs['action taken index'] == 1 and inputs['preapproval'] == '1':
					container['dispositions'][6]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['juniorliencount'] +=1

			elif inputs['lien status'] == '3':
				container['dispositions'][0]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['noliencount'] +=1
				container['dispositions'][inputs['action taken index']]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['noliencount']+=1
				if inputs['purchaser'] >0:
					container['dispositions'][7]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['noliencount'] +=1
				if inputs['action taken index'] == 1 and inputs['preapproval'] == '1':
					container['dispositions'][6]['loantypes'][inputs['loan type']]['purposes'][inputs['loan purpose']]['noliencount'] +=1

	def compile_report_A_4(self, container, inputs):
		if inputs['preapproval'] == '1' and inputs['action taken'] == '1':
			self.fill_by_characteristics(container, inputs, 'borrowercharacteristics', 0, 'races', inputs['race'], 'preapprovalstatuses', 0)
			self.fill_by_characteristics(container, inputs, 'borrowercharacteristics', 1, 'ethnicities', inputs['ethnicity'], 'preapprovalstatuses', 0)
			if inputs['minority status'] < 2:
				self.fill_by_characteristics(container, inputs, 'borrowercharacteristics', 2, 'minoritystatuses', inputs['minority status'], 'preapprovalstatuses', 0)
			if inputs['income bracket'] < 6:
				self.fill_by_characteristics(container, inputs, 'borrowercharacteristics', 3, 'incomes', inputs['income bracket'], 'preapprovalstatuses',0)
			self.fill_by_characteristics(container, inputs, 'borrowercharacteristics', 4, 'genders', inputs['gender'], 'preapprovalstatuses', 0)
			self.fill_by_characteristics(container, inputs, 'censuscharacteristics', 0, 'compositions', inputs['minority percent index'], 'preapprovalstatuses', 0)
			if inputs['tract income index'] < 4:
				self.fill_by_characteristics(container, inputs, 'censuscharacteristics', 1, 'incomes', inputs['tract income index'], 'preapprovalstatuses', 0)

		#fill NAs for MSA level reports
		for i in range(1, 3):
			self.fill_by_characteristics_NA(container, inputs, 'borrowercharacteristics', 0, 'races', inputs['race'], 'preapprovalstatuses', i)
			self.fill_by_characteristics_NA(container, inputs, 'borrowercharacteristics', 1, 'ethnicities', inputs['ethnicity'], 'preapprovalstatuses', i)
			if inputs['minority status'] < 2:
				self.fill_by_characteristics_NA(container, inputs, 'borrowercharacteristics', 2, 'minoritystatuses', inputs['minority status'], 'preapprovalstatuses', i)
			if inputs['income bracket'] < 6:
				self.fill_by_characteristics_NA(container, inputs, 'borrowercharacteristics', 3, 'incomes', inputs['income bracket'], 'preapprovalstatuses', i)
			self.fill_by_characteristics_NA(container, inputs, 'borrowercharacteristics', 4, 'genders', inputs['gender'], 'preapprovalstatuses', i)
			self.fill_by_characteristics_NA(container, inputs, 'censuscharacteristics', 0, 'compositions', inputs['minority percent index'], 'preapprovalstatuses', i)
			if inputs['tract income index'] < 4:
				self.fill_by_characteristics_NA(container, inputs, 'censuscharacteristics', 1, 'incomes', inputs['tract income index'], 'preapprovalstatuses', i)

	def compile_report_B(self, container, inputs):
		self.fill_rates_B(inputs)
		table_b_pricing = self.rate_spreads[0:2] + self.rate_spreads[-2:]
		#aggregate 1-4 family loans
		if inputs['lien status'] == 1 and inputs['property type'] == 1:
			if inputs['rate spread index'] == 0:
				container['singlefamily'][0]['pricinginformation'][0]['purposes'][inputs['loan purpose']]['firstliencount'] += 1
			if inputs['rate spread index'] > 0:
				container['singlefamily'][0]['pricinginformation'][1]['purposes'][inputs['loan purpose']]['firstliencount'] += 1
			container['singlefamily'][1]['pricinginformation'][inputs['hoepa flag']-1]['purposes'][inputs['loan purpose']]['firstliencount'] += 1
		if inputs['lien status'] == 2 and inputs['property type'] == 1:
			if inputs['rate spread index'] == 0:
				container['singlefamily'][0]['pricinginformation'][0]['purposes'][inputs['loan purpose']]['juniorliencount'] += 1
			if inputs['rate spread index'] > 0:
				container['singlefamily'][0]['pricinginformation'][1]['purposes'][inputs['loan purpose']]['juniorliencount'] += 1
			container['singlefamily'][1]['pricinginformation'][inputs['hoepa flag']-1]['purposes'][inputs['loan purpose']]['juniorliencount'] += 1

		#aggregate manufactured loans
		if inputs['lien status'] == 1 and inputs['property type'] == 2:
			if inputs['rate spread index'] == 0:
				container['manufactured'][0]['pricinginformation'][0]['purposes'][inputs['loan purpose']]['firstliencount'] += 1
			if inputs['rate spread index'] > 0:
				container['manufactured'][0]['pricinginformation'][1]['purposes'][inputs['loan purpose']]['firstliencount'] += 1
			container['manufactured'][1]['pricinginformation'][inputs['hoepa flag']-1]['purposes'][inputs['loan purpose']]['firstliencount'] += 1

		if inputs['lien status'] == 2 and inputs['property type'] == 2:
			if inputs['rate spread index'] == 0:
				container['manufactured'][0]['pricinginformation'][0]['purposes'][inputs['loan purpose']]['juniorliencount'] += 1
			if inputs['rate spread index'] > 0:
				container['manufactured'][0]['pricinginformation'][1]['purposes'][inputs['loan purpose']]['juniorliencount'] += 1

			container['manufactured'][1]['pricinginformation'][inputs['hoepa flag']-1]['purposes'][inputs['loan purpose']]['juniorliencount'] += 1

	def fill_table_B_mean(self, container, inputs):
		# list nesting order: [property type][lien status][loan purpose]

			for i in range(0,3): #cycle loan purpose
				if len(self.table_B_rates[0][0][i]) >0:
					#single family
					container['singlefamily'][0]['pricinginformation'][2]['purposes'][i]['firstliencount'] = round(numpy.mean(numpy.array(self.table_B_rates[0][0][i])),2) #mean for first liens
					container['singlefamily'][0]['pricinginformation'][3]['purposes'][i]['firstliencount'] = round(numpy.median(numpy.array(self.table_B_rates[0][0][i])),2) #median for first liens

				if len(self.table_B_rates[0][1][i]) >0:
					container['singlefamily'][0]['pricinginformation'][2]['purposes'][i]['juniorliencount'] = round(numpy.mean(numpy.array(self.table_B_rates[0][1][i])),2) #mean for first liens
					container['singlefamily'][0]['pricinginformation'][3]['purposes'][i]['juniorliencount'] = round(numpy.median(numpy.array(self.table_B_rates[0][1][i])),2) #median for first liens

				if len(self.table_B_rates[1][0][i]) >0:
					#manufactured
					container['manufactured'][0]['pricinginformation'][2]['purposes'][i]['firstliencount'] = round(numpy.mean(numpy.array(self.table_B_rates[1][0][i])),2) #mean for junior liens
					container['manufactured'][0]['pricinginformation'][3]['purposes'][i]['firstliencount'] = round(numpy.median(numpy.array(self.table_B_rates[1][0][i])),2) #median for junior liens
				if len(self.table_B_rates[1][1][i]) >0:
					container['manufactured'][0]['pricinginformation'][2]['purposes'][i]['juniorliencount'] = round(numpy.mean(numpy.array(self.table_B_rates[1][1][i])),2) #mean for junior liens
					container['manufactured'][0]['pricinginformation'][3]['purposes'][i]['juniorliencount'] = round(numpy.median(numpy.array(self.table_B_rates[1][1][i])),2) #median for junior liens
		#self.container['singlefamily'][0][2] #median
		#round(numpy.median(numpy.array(inputs[self.purchaser_first_lien_rates[n]])),2) #for normal median

	def fill_rates_B(self, inputs):
		property_type = inputs['property type'] -1
		lien_status = inputs['lien status'] -1

		if inputs['rate spread'] != 'NA   ' and inputs['rate spread'] != '     ':
			#first list 'property type', second list 'lien status', third list 'loan purpose'
			self.table_B_rates[property_type][lien_status][inputs['loan purpose']].append(Decimal(inputs['rate spread']))