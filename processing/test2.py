from collections import OrderedDict
end_points = ['count', 'value']
dispositions_list = ['Applications Received', 'Loans Originated', 'Apps. Approved But Not Accepted', 'Aplications Denied', 'Applications Withdrawn', 'Files Closed For Incompleteness']
tract_income = ['Low income', 'Moderate income', 'Middle income', 'Upper income']
tract_pct_minority = ['Less than 10% minority', '10-19% minority', '20-49% minority', '50-79% minority', '80-100% minority']
container = {}


def print_JSON(): #prints a json object to the terminal
	import json
	print json.dumps(container, indent=4)

def write_JSON(name, data): #writes a json object to file
	with open(name, 'w') as outfile: #writes the JSON structure to a file for the path named by report's header structure
		json.dump(data, outfile, indent=4, ensure_ascii = False)

def table_7x_builder():
	container['racial_ethnic_composition'] = set_brackets('race', tract_pct_minority)
	for i in range(0,len(container['racial/ethnic composition'])):
		container['racial/ethnic composition'][i]['dispositions'] = set_stuff(end_points, dispositions_list, 'disposition')
		#container['racial/ethnic composition'][i]['race'] = set_stuff(end_points, tract_income, 'income')
		#for j in range(0, len(container['racial/ethnic composition'][i]['dispositions'])):
		#	container['racial/ethnic composition'][i]['dispositions'][j] = set_stuff(end_points, dispositions_list, 'disposition')
	container['incomecharacteristics'] = set_brackets('income', tract_income)

def set_brackets(bracket_singular, bracket_list):
	brackets = []
	for bracket in bracket_list:
		holding = OrderedDict({})
		holding[bracket_singular] = "{}".format(bracket)
		brackets.append(holding)
	return brackets

def set_stuff(end_points, thing_list, thing_singular):
	listyness = []
	for thing in thing_list:
		things_holding = OrderedDict({})
		things_holding[thing_singular] = "{}".format(thing)
		listyness.append(things_holding)
	return listyness

table_7x_builder()

print_JSON()