import json
import psycopg2

from report1v6 import report_1_
#report 3 aggregates 1 census tract from inside an MSA
#to build a report, loop over all tracts and then sum the appropriate lines
from report3v6 import report_3_
#credentials read in as variables in the format "'dbname', 'username', 'serverhost', 'password'"
#comments for which reports require which variables
with open('/users/roellk/desktop/python/credentials.txt', 'r') as f:
	credentials = f.read()

cred_list = credentials.split(',')

#location is statecode, countycode, censustractnumber (as in SQL)
#location = ('29', '119', '0702.00')
location = ('31', '153', '0105.02')
#report_1 = report_1_()

#report_1.report_1_main(location)
#report_1.print_table_1()
junk = 'junk.txt'
#report_1.write_report_1_json(junk)


test = 'testfile.txt'
report_3 = report_3_()
report_3.report_3_main(location, cred_list)
report_3.print_report_3()
report_3.write_report_3(test)
