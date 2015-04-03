import json
from collections import OrderedDict
race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Other Pacific Islander', 'White', '2 or more minority races', 'Joint (White/Minority Race', 'Not Available']

race_list = []
container = OrderedDict({})
disp_list = ['Applications Received', 'Loans Originated', 'Aps. Approved But Not Accepted', 'Aplications Denied', 'Applications Withdrawn', 'Files Closed For Incompleteness']
holding_list = ['count', 'value']
gender_list = ['Male', 'Female', 'Joint (Male/Female)']
ethnicity_names = ['Hispanic or Latino', 'Not Hispanic or Latino', 'Joint (Hispanic or Latino/Not Hispanic or Latino', 'Ethnicity Not Available']
minority_statuses = ['White Non-Hispanic', 'Others, Including Hispanic']
applicant_income_bracket = ['Less than 50% of MSA/MD median', '50-79% of MSA/MD median', '80-99% of MSA/MD median', '100-119% of MSA/MD median', '120% or more of MSA/MD median', 'income not available']
tract_pct_minority = ['Less than 10% minority', '10-19% minority', '20-49% minority', '50-79% minority', '80-100% minority']
def set_41_dispositions(holding_list): #this function sets the purchasers section of report 3-2
	dispositions = []
	for item in disp_list:
		dispositionsholding = OrderedDict({})
		dispositionsholding['disposition'] = "{}".format(item)
		dispositions.append(dispositionsholding)
		for thing in holding_list:
			dispositionsholding[thing] = 0
	return dispositions

def set_41_gender():
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

def table_7x_builder():
	set_41_races()
	set_41_ethnicity()
	set_41_minority()
	set_41_incomes()

def set_41_races():
	races = []
	for race in tract_pct_minority:
		holding = OrderedDict({})
		holding['race'] = "{}".format(race)
		races.append(holding)
	container['races'] = races
	for i in range(0,len(container['races'])):
		container['races'][i]['dispositions'] = set_41_dispositions(holding_list)
		#container['races'][i]['genders'] = set_41_gender()

def set_41_ethnicity():
	ethnicities = []
	for ethnicity in ethnicity_names:
		holding = OrderedDict({})
		holding['ethnicity'] = "{}".format(ethnicity)
		ethnicities.append(holding)
	container['ethnicities'] = ethnicities
	for i in range(0, len(container['ethnicities'])):
		container['ethnicities'][i]['dispositions'] = set_41_dispositions(holding_list)
		#container['ethnicities'][i]['genders'] = set_41_gender()

def set_41_minority():
	minoritystatuses = []
	for status in minority_statuses:
		holding = OrderedDict({})
		holding['minoritystatus'] = "{}".format(status)
		minoritystatuses.append(holding)
	container['minoritystatuses'] = minoritystatuses
	for i in range(0, len(container['minoritystatuses'])):
		container['minoritystatuses'][i]['dispositions'] = set_41_dispositions(holding_list)
		#container['minoritystatuses'][i]['genders'] = set_41_gender()

def set_41_incomes():
	applicantincomes = []
	for income in applicant_income_bracket:
		holding = OrderedDict({})
		holding['incomes'] = "{}".format(income)
		applicantincomes.append(holding)
	container['incomes'] = applicantincomes
	for i in range(0, len(container['incomes'])):
		container['incomes'][i]['dispositions'] = set_41_dispositions(holding_list)
		#container['incomes'][i]['dispositions'] = set_41_gender()
	container['total'] = set_41_dispositions(holding_list)

table_7x_builder()
print json.dumps(container, indent=4)
with open('7x_json.json', 'w') as outfile:
	json.dump(container, outfile, indent=4, ensure_ascii = False)



