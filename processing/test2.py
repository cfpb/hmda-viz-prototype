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

def set_brackets(bracket_singular, bracket_list):
	brackets = []
	for bracket in bracket_list:
		holding = OrderedDict({})
		holding[bracket_singular] = "{}".format(bracket)
		brackets.append(holding)
	return brackets

def set_dispositions(end_points): #builds the dispositions of applications section of report 4-1 JSON
	dispositions = []
	for item in dispositions_list:
		dispositionsholding = OrderedDict({})
		dispositionsholding['disposition'] = "{}".format(item)
		dispositions.append(dispositionsholding)
		for point in end_points:
			dispositionsholding[point] = 0
	return dispositions
def table_7x_builder():
	#container['censuscharacteristics'] = set_brackets('race', tract_pct_minority)
	container['censuscharacteristics'] = []
	holding = OrderedDict({})
	holding['characteristic'] = 'Race/Ethnic Composition'
	holding['compositions'] = set_brackets('composition', tract_pct_minority)
	container['censuscharacteristics'].append(holding)
	holding = OrderedDict({})
	holding['characteristic'] = 'Income Characteristics'
	holding['incomes'] = set_brackets('income', tract_income)
	container['censuscharacteristics'].append(holding)
	holding = OrderedDict({})
	holding['characteristic'] = 'Income & Racial/Ethnic Composition'
	holding['incomes'] = set_brackets('income', tract_income)
	for i in range(0, len(holding['incomes'])):
		holding['incomes'][i]['compositions'] = set_brackets('composition', tract_pct_minority)
		for j in range(0, len(holding['incomes'][i]['compositions'])):
			holding['incomes'][i]['compositions'][j]['dispositions'] = set_dispositions(end_points)

	container['censuscharacteristics'].append(holding)
	for i in range(0,len(container['censuscharacteristics'][0]['compositions'])):
		container['censuscharacteristics'][0]['compositions'][i]['dispositions'] = set_dispositions(end_points)
	for i in range(0, len(container['censuscharacteristics'][1]['incomes'])):
		container['censuscharacteristics'][1]['incomes'][i]['dispositions'] = set_dispositions(end_points)
	'''

	for i in range(0, len(container['income&racial/ethnic_composition'])):
		container['income&racial/ethnic_composition'][i]['censuscharacteristics'] = set_brackets('race', tract_pct_minority)
		for j in range(0, len(container['income&racial/ethnic_composition'][i]['censuscharacteristics'])):
			container['income&racial/ethnic_composition'][i]['censuscharacteristics'][j]['disposition'] = set_dispositions(end_points)
	'''
table_7x_builder()

print_JSON()
