class MSA_info(object): #contains functions for setting aggregate information for the MSA
	def __init__(self):
		pass

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
