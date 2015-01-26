from JSON_Template_Master import report_3_1_json as r3
inputs = {}

race = 'Asian'
race_code = 1
purchaser = 'Fannie Mae'
inputs['purchaser'] = 1
inputs['ethnicity'] = 0
ethnicity = 'Hispanic or Latino'
inputs['minority status'] = 0
minority_status = 'White non-hispanic'
#print r3.table_3_1['borrower-characteristics'][0]['Race'][0]['American Indian/Alaska Native']['purchasers'][1]['Fannie Mae']['count'], "\n"
#print race in r3.table_3_1['borrower-characteristics'][0]['Race'][race_code], "\n"
#print purchaser in r3.table_3_1['borrower-characteristics'][0]['Race'][race_code][race]['purchasers'][inputs['purchaser']]
#print len(r3.table_3_1['borrower-characteristics'][0]['Race'])
#print r3.table_3_1['borrower-characteristics'][0]['Race']
#print len(r3.table_3_1['borrower-characteristics'][0]['Race'][race_code][race]['purchasers'])
#print r3.table_3_1['borrower-characteristics'][0]['Race'][race_code][race]['purchasers'][inputs['purchaser']][purchaser]['count']
#print r3.table_3_1['borrower-characteristics'][0]['Race'][race_code][race]['purchasers'][inputs['purchaser']][purchaser]['value']
#print r3.table_3_1['borrower-characteristics'][1]['Ethnicity'][0][ethnicity]
#print ethnicity in r3.table_3_1['borrower-characteristics'][1]['Ethnicity'][inputs['ethnicity']], "\n"
#print purchaser in r3.table_3_1['borrower-characteristics'][1]['Ethnicity'][inputs['ethnicity']][ethnicity]['purchasers'][inputs['purchaser']], "\n"
#print r3.table_3_1['borrower-characteristics'][1]['Ethnicity'][inputs['ethnicity']][ethnicity]['purchasers'][inputs['purchaser']][purchaser]['count'], "\n"
#print r3.table_3_1['borrower-characteristics'][1]['Ethnicity'][inputs['ethnicity']][ethnicity]['purchasers'][inputs['purchaser']][purchaser]['value']

#print purchaser in r3.table_3_1['borrower-characteristics'][2]['Minority Status'][inputs['minority status']][minority_status]['purchasers'][inputs['purchaser']]
#print minority_status in r3.table_3_1['borrower-characteristics'][2]['Minority Status'][inputs['minority status']]
#print r3.table_3_1['borrower-characteristics'][2]['Minority Status'][inputs['minority status']][minority_status]['purchasers'][inputs['purchaser']][purchaser]['count']
#print r3.table_3_1['borrower-characteristics'][2]['Minority Status'][inputs['minority status']][minority_status]['purchasers'][inputs['purchaser']][purchaser]['value']
#r3.table_3_1['year'] = '2013'
#print r3.table_3_1['year']
#print type(r3.table_3_1)
print r3.table_3_1['total']['purchasers'][inputs['purchaser']][purchaser]['count']