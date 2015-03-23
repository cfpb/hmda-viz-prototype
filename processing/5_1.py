from collections import OrderedDict
dispositions_list = ['Applications Received', 'Loans Originated', 'Apps. Approved But Not Accepted', 'Aplications Denied', 'Applications Withdrawn', 'Files Closed For Incompleteness']
race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Other Pacific Islander', 'White', '2 or more minority races', 'Joint (White/Minority Race)', 'Race Not Available']
applicant_income_bracket = ['Less than 50% of MSA/MD median', '50-79% of MSA/MD median', '80-99% of MSA/MD median', '100-119% of MSA/MD median', '120% or more of MSA/MD median', 'Income Not Available']
ethnicity_names = ['Hispanic or Latino', 'Not Hispanic or Latino', 'Joint (Hispanic or Latino/Not Hispanic or Latino)', 'Ethnicity Not Available']
minority_statuses = ['White Non-Hispanic', 'Others, Including Hispanic']
end_points = ['count', 'value']
container = OrderedDict({})
def print_JSON(container): #prints a json object to the terminal
	import json
	print json.dumps(container, indent=4)



def set_stuff(end_points, thing_list, thing_singular):
	listyness = []
	for thing in thing_list:
		things_holding = OrderedDict({})
		things_holding[thing_singular] = "{}".format(thing)
		listyness.append(things_holding)
		for point in end_points:
			things_holding[point] = 0
	return listyness

def set_income_brackets():
	income_brackets = []
	for bracket in applicant_income_bracket[:-1]:
		income_holding = OrderedDict({})
		income_holding['incomebracket'] = "{}".format(bracket)
		income_brackets.append(income_holding)
	return income_brackets
def build_5x():
	income_brackets= []
	container['incomebrackets'] = set_income_brackets()
	for i in range(0,len(container['incomebrackets'])):
		container['incomebrackets'][i]['races'] = set_stuff(end_points, race_names, 'race')
		container['incomebrackets'][i]['ethnicities'] = set_stuff(end_points, ethnicity_names, 'ethnicity')
		container['incomebrackets'][i]['minoritystatuses'] = set_stuff(end_points, minority_statuses, 'minoritystatus')
	#container['races'] = set_5x_races(end_points)

build_5x()
print_JSON(container)