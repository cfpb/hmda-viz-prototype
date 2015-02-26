import json
from collections import OrderedDict
race_names = ['American Indian/Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Other Pacific Islander', 'White', '2 or more minority races', 'Joint (White/Minority Race', 'Not Available']
races = []
race_list = []
container = OrderedDict({})
def set_gender(self, end_point):
    genders = ['male', 'female', 'joint (male/female']
    for item in genders:
        end_point[item] = 0

for race in race_names:
    holding = OrderedDict({})
    holding['race'] = "{}".format(race)
    races.append(holding)

container['races'] = races
for i in range(0,len(container['races'])):
    container['races'][i]['dispositions'] = []

print json.dumps(container, indent=4)