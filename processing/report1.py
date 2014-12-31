#this file pulls the data required to build the MSA aggregate report 1 covering application dispositions
#rows are application disposition pulled from the action taken field
# 1) loan originated, 2)loan not accepted, 3) application denied, 4) applicatoin withdrawn, 5)incomplete, 6)loan purchased (for report 2)
import json
import psycopg2
#attempte a connection to the SQL database hosting the LAR information
try:
	conn = psycopg2.connect("dbname='hmdamaster' user='roellk' host='localhost' password=''")
#if database connection results in an error print the following
except:
    print "I am unable to connect to the database"
inputs = {}

def parse_inputs(row):
		#splits the tuples into word variables for easy reading
	inputs['census_tract'] = row[0]
	inputs['loan_type'] = row[1] 
	inputs['occupancy_status'] = row[2]
	inputs['loan_amount'] = row[3]
	inputs['action_type'] = row[4]
	inputs['loan_purpose'] = row[5]
	inputs['property_type'] = row[6]

def table_1_aggregator(inputs):

	#convert action_type code to a word for inputting data into dictionary
	if inputs['action_type'] == '1':
		action = 'originated'
	elif inputs['action_type'] == '2':
		action = 'not accepted'
	elif inputs['action_type'] == '3':
		action = 'denied'
	elif inputs['action_type'] == '4':
		action = 'withdrawn'
	elif inputs['action_type'] == '5':
		action = 'incomplete'
	elif inputs['action_type'] == '6':
		action = 'purchased'

	#convert occupancy status to word for inputting into data dictionary
	if inputs['occupancy_status'] == '1':
		occupancy = 'owner occupied'
	elif inputs['occupancy_status'] == '2':
		occupancy = 'non-occupant'

	#convert loan_purpose to word for inputting into data dictionary
	if inputs['loan_purpose'] == '1':
		purpose = 'purchase'
	elif inputs['loan_purpose'] == '2':
		purpose = 'home improvement'
	elif inputs['loan_purpose'] =='3':
		purpose = 'refinance'

	#convert property type to word for inputting into data dictionary
	if inputs['property_type'] == '1':
		prop = '1-4 family' #excludes manufactured housing
	elif inputs['property_type'] == '2':
		prop = 'manufactured'
	elif inputs['property_type'] == '3':
		prop = 'multifamily'

	#convert loan type to word for inputting into data dictionary
	if inputs['loan_type'] == '1':
		loan = 'conventional'
	elif inputs['loan_type'] == '2' or inputs['loan_type'] == '3' or inputs['loan_type'] == '4':
		loan = 'GS'

	#concatenate the count and value strings to access the dictionary
	occupancy_count = occupancy + ' count'
	occupancy_value = occupancy + ' value'
	loan_type_count = loan + ' count'
	loan_type_value = loan + ' value'
	property_type_count = prop + ' count'
	property_type_value = prop + ' value'
	loan_purpose_count = purpose + ' count'
	loan_purpose_value = purpose + ' value'
	

	if action in table_1['action'] and loan_type_count in table_1['action'][action] and prop == '1-4 family' or prop == 'manufactured':
		if purpose == 'purchase' and prop != 'multifamly':
			table_1['action'][action][loan_type_count] +=1
			table_1['action'][action][loan_type_value] += int(inputs['loan_amount'])
		if purpose == 'refinance' or purpose == 'home improvement' and prop != 'multifamily':
			table_1['action'][action][loan_purpose_count] += 1
			table_1['action'][action][loan_purpose_value] += int(inputs['loan_amount'])
		if prop == 'multifamily':
			table_1['action'][action][property_type_count] +=1
			table_1['action'][aciton][property_type_value] += int(inputs['loan_amount'])
		if prop != 'multifamly' and occupancy == 'non-occupant':
			table_1['action'][action][occupancy_count] += 1
			table_1['action'][action][occupancy_value] += int(inputs['loan_amount'])
		if prop == 'manufactured':
			table_1['action'][action][property_type_count] +=1
			table_1['action'][action][property_type_value] += int(inputs['loan_amount'])
	else:
		print "error, key not in dictionary"

#this dictionary holds the data values needed to build tables 1 and 2
table_1 = {
"action": { 
	"originated": {
		"GS count": 0,
		"GS value": 0,
		"conventional count": 0,
		"conventional value": 0,
		"refinance count": 0,
		"refinance value": 0,
		"home improvement count": 0,
		"home improvement value": 0,
		"multifamily count": 0,
		"multifamily value": 0,
		"non-occupant count": 0,
		"non-occupant value": 0,
		"manufactured count": 0,
		"manufactured value": 0
},
	"not accepted": {
		"GS count": 0,
		"GS value": 0,
		"conventional count": 0,
		"conventional value": 0,
		"refinance count": 0,
		"refinance value": 0,
		"home improvement count": 0,
		"home improvement value": 0,
		"multifamily count": 0,
		"multifamily value": 0,
		"non-occupant count": 0,
		"non-occupant value": 0,
		"manufactured count": 0,
		"manufactured value": 0
},
	"denied": {
		"GS count": 0,
		"GS value": 0,
		"conventional count": 0,
		"conventional value": 0,
		"refinance count": 0,
		"refinance value": 0,
		"home improvement count": 0,
		"home improvement value": 0,
		"multifamily count": 0,
		"multifamily value": 0,
		"non-occupant count": 0,
		"non-occupant value": 0,
		"manufactured count": 0,
		"manufactured value": 0
},
	"withdrawn": {
		"GS count": 0,
		"GS value": 0,
		"conventional count": 0,
		"conventional value": 0,
		"refinance count": 0,
		"refinance value": 0,
		"home improvement count": 0,
		"home improvement value": 0,
		"multifamily count": 0,
		"multifamily value": 0,
		"non-occupant count": 0,
		"non-occupant value": 0,
		"manufactured count": 0,
		"manufactured value": 0		
},
	"incomplete": { 
		"GS count": 0,
		"GS value": 0,
		"conventional count": 0,
		"conventional value": 0,
		"refinance count": 0,
		"refinance value": 0,
		"home improvement count": 0,
		"home improvement value": 0,
		"multifamily count": 0,
		"multifamily value": 0,
		"non-occupant count": 0,
		"non-occupant value": 0,
		"manufactured count": 0,
		"manufactured value": 0	
},
	"purchased": {
		"GS count": 0,
		"GS value": 0,
		"conventional count": 0,
		"conventional value": 0,
		"refinance count": 0,
		"refinance value": 0,
		"home improvement count": 0,
		"home improvement value": 0,
		"multifamily count": 0,
		"multifamily value": 0,
		"non-occupant count": 0,
		"non-occupant value": 0,
		"manufactured count": 0,
		"manufactured value": 0	
	}
	}
}
#tables 1 and 2 require using: geocode, loanpurpose, occupancy, actiontype, loanvalue
#census_tract is the 11 digit state/county/tract number for the address of the loan
#loantype is conventional(1), FHA(2), VA(3), FSA/RHS(4)
#loanpurpose determines purchase (1), refinance(2), or home improvement(3)
#occupancy shows owner(1) vs non-owner(2) or not applicable(3) occupancy status
#actiontype shows the application disposition originated(1), not accepted(2), denied(3), withdrawn(4), incomplete(5), purchased(6)
#loanvalue is the amount of the loan
#propertytype determines 1-4 family(1),manufactured housing(2), or multifamily(3)

cur = conn.cursor()
cur.execute("""SELECT count(censustractnumber) FROM HMDA_LAR_PUBLIC_FINAL_2012 WHERE statecode = '31' and countycode = '153' and censustractnumber = '0105.02'; """)

rows = cur.fetchone()
count = rows[0]
print count

cur.execute("""SELECT 
	censustractnumber, loantype, occupancy, loanamount, actiontype, loanpurpose, propertytype, 
	statecode, countycode
 FROM HMDA_LAR_PUBLIC_FINAL_2012 
 where statecode = '31' and countycode = '153' and censustractnumber = '0105.02'; """)

for i in range(0, count):

	row = cur.fetchone() # fetches all the rows with census_tracts matching the passed value
	#how many rows were returned?
	#what if no rows are returned? -- all values stay at 0
	#what if more than 1 row is returned -- this code returns all rows in a loop and parses the tuples into the 
	#appropriate filters

	#splits the tuples into word variables for easy reading
	parse_inputs(row)

	#issues:
	##need to sort geographic identifiers that are NA, invalid or unavailable.
	#build tracts into MSA/MD total
	#State totals may be needed if MSA/MD is not available
	#county totals will be needed

	#the following conditionals section aggregates the counts and values of different loan types and uses the aggregates to fill the dictionary/JSON object
	table_1_aggregator(inputs)

	#columns 1 and 2 on table 1
	#Government sponsored home purchase
	#home purchase, FHA RSA or VA loan, on 1-4 family, originated 
		
#output check 

print "\n" *4
print "originated loans\n", "*" * 10
for key, value in table_1['action']['originated'].iteritems():
	print key, value

print "\nnot accepted loans\n", "*" * 10
for key, value in table_1['action']['not accepted'].iteritems():
	print key, value

print "\ndenied applications\n", "*" * 10
for key, value in table_1['action']['denied'].iteritems():
	print key, value

print "\nwithdrawn applications\n", "*" * 10
for key, value in table_1['action']['withdrawn'].iteritems():
	print key, value

print "\nincomplete applications\n", "*" * 10
for key, value in table_1['action']['incomplete'].iteritems():
	print key, value

print "\npurchased loans\n", "*" * 10
for key, value in table_1['action']['purchased'].iteritems():
	print key, value

#with open('report_1v2.json', 'wb') as outfile:
#	json.dump(report, outfile)

with open('report1v4.txt', 'w') as outfile:
     json.dump(table_1, outfile, sort_keys = True, indent = 4, ensure_ascii=False)








