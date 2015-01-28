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

#print r3.table_3_1['borrower-characteristics'][1]['ethnicities'][inputs['ethnicity']]['purchasers'][inputs['purchaser']]['name']
#print r3.table_3_1['borrower-characteristics'][1]['ethnicities'][inputs['ethnicity']]['purchasers'][inputs['purchaser']]['name']
print r3.table_3_1['borrower-characteristics'][0]['races'][race_code]['purchasers'][inputs['purchaser']]['purchaser']
#print r3.table_3_1['borrower-characteristics'][1]['ethnicities'][inputs['ethnicity']]['purchasers'][inputs['purchaser']]['count'] += 1