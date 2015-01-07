import json
import psycopg2
from geo_aggregator_one import geo_aggregator

#from report1v2 import report_1_
#report 3 aggregates 1 census tract from inside an MSA
#to build a report, loop over all tracts and then sum the appropriate lines
from report31 import report_3_
#credentials read in as variables in the format "'dbname', 'username', 'serverhost', 'password'"
#comments for which reports require which variables
with open('/users/roellk/desktop/python/credentials.txt', 'r') as f:
	credentials = f.read()

cred_list = credentials.split(',')

#access geo_aggregator and pull all sub geographies for one MSA
#pass cred_list to geo_aggregator for SQL login
#controller sends a list of MSAs to the geo_aggregator_one to get a list of all sub geographies
#passing test will use MSA 36540
MSA = ['36540']

geo_aggregator = geo_aggregator()
geo_aggregator.main(cred_list, MSA)
geo_aggregator.write_geo_dict('geotest.json')
#geo_aggregator.print_geo_dict()

#create a report 3 object to use functions
report_3 = report_3_()

#return a geography dictionary of all sub geographies from the MSA list
geography_list = geo_aggregator.return_geo_dict()

#print geography_list #test print of geography dict
#set state and county to pass to location tuples, this will be used to generate multiple instances of report 3 (multiple tracts)
state = geography_list['MSAs'][0]['States'][0]['State name']
county =geography_list['MSAs'][0]['States'][0]['Counties'][0]['County name']
print len(geography_list['MSAs'][0]['States'][0]['Counties'][0]['Tracts']), "length of loop"
for i in range(0, len(geography_list['MSAs'][0]['States'][0]['Counties'][0]['Tracts'])):
	tract = str(geography_list['MSAs'][0]['States'][0]['Counties'][0]['Tracts'][i]['Tract name'])
	location = (state, county, tract)
	print tract
	report3_1 = 'report3_1_' + tract + '.json'
	report_3.report_3_main(location, cred_list)
	report_3.write_report_3(report3_1)
	#print geography_list['MSAs'][0]['States'][0]['Counties'][0]['Tracts'][i]

#for i in range(0, len(geography_list['MSAs'][0]['States'][0]['Counties'][0]['Tracts']):
	#print geography_list['MSAs'][0]['States'][0]['Counties'][0]['Tracts'][i]

#location is statecode, countycode, censustractnumber (as in SQL)
#location = ('29', '119', '0702.00')
location = ('31', '153', '0105.02')
#report_1 = report_1_()

#report_1.report_1_main(location)
#report_1.print_table_1()
junk = 'junk.txt'
#report_1.write_report_1_json(junk)


report3_1 = 'report3_1.json'

report_3.report_3_main(location, cred_list)
#report_3.print_report_3()
report_3.write_report_3(report3_1)
