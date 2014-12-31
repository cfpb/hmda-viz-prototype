import json
import psycopg2

from report1v6 import report_1_
from report3v4 import report_3_
#credentials read in as variables
#comments for which reports require which variables


'''
report_1 = report_1_()
location = ('31', '153', '0105.02' )
report_1.report_1_main(location)
report_1.print_table_1()
junk = 'junk.txt'
report_1.write_report_1_json(junk)
'''
location = ('31', '153', '0105.02')
test = 'testfile.txt'
report_3 = report_3_()
report_3.report_3_main(location)
report_3.print_report_3()
report_3.write_report_3(test)