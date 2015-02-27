import json
from collections import OrderedDict
race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Other Pacific Islander', 'White', '2 or more minority races', 'Joint (White/Minority Race', 'Not Available']

race_list = []
container = OrderedDict({})
disp_list = ['Applications Received', 'Loans Originated', 'Aps. Approved But Not Accepted', 'Aplications Denied', 'Applications Withdrawn', 'Files Closed For Incompleteness']
holding_list = ['count', 'value']
gender_list = ['Male', 'Female', 'Joint (Male/Female)']

def set_dispositions(holding_list): #this function sets the purchasers section of report 3-2
	dispositions = []
	for item in disp_list:
		dispositionsholding = OrderedDict({})
		dispositionsholding['disposition'] = "{}".format(item)
		for thing in holding_list:
			dispositionsholding[thing] = 0
			dispositions.append(dispositionsholding)
		dispositions.append(dispositionsholding)
	return dispositions

def set_gender():
	genders = []
	gendersholding = {}
	for gender in gender_list:
		holding = OrderedDict({})
		holding['gender'] = "{}".format(gender)
		genders.append(holding)
	gendersholding['genders'] = genders
	for j in range(0, len(gender_list)):
		gendersholding['genders'][j]['dispositions'] = set_dispositions(holding_list)
	return gendersholding

def table_41_builder():
	races = []
	for race in race_names:
		holding = OrderedDict({})
		holding['race'] = "{}".format(race)
		races.append(holding)
	container['races'] = races
	for i in range(0,len(container['races'])):
		container['races'][i]['dispositions'] = set_dispositions(holding_list)
		container['races'][i]['genders'] = set_gender()


set_races()


print json.dumps(container, indent=4)



