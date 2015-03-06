import json
import os
import csv
import psycopg2
import psycopg2.extras
from collections import OrderedDict
#import the parse_inputs class to store the 'inputs' dictionary
from A_D_library import parse_inputs as parse
from A_D_library import connect_DB as connect
from A_D_library import build_JSON as build
from A_D_library import aggregate as agg
from A_D_library import queries
from A_D_library import report_selector as selector
from constructor import report_4x
#from constructor import report_3x
#instantiate library functions
#add a year column to the HMDA input file
#use the year column to select which databases to connect to (create more functions for each year)
connection = connect() #connects to the DB
selector = selector() #holds lists of reports to be generated for each MSA
cur = connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
selector.get_report_lists('MSAinputs2013.csv') #fills the dictionary of lists of reports to be generated
build_msa = build() #instantiate the build object


#build_msa.msas_in_state(cur, selector, 'aggregate') #creates a list of all MSAs in each state and places the file in the state's aggregate folder
#build_msa.msas_in_state(cur, selector, 'disclosure')#creates a list of all MSAs in each state and places the file in the state's disclosure folder

#report_3x = report_3x()
selector.report_list['A 3-2'] = ['11500']
#selector.report_list['A 4-1'] = ['29620']

report_list = ['A 3-2']
for report in report_list: #loop over a list of report names
	for MSA in selector.report_list[report]: #loop through MSAs flagged for report generation
		report_x = report_4x(report, selector) #instantiate class and set function strings
		report_x.report_x(MSA, cur) #variabalize funciton inputs!!!!
'''

report_list = ['A 3-1', 'A 3-2', 'A 4-1', 'A 4-2', 'A 4-3', 'A 4-4', 'A 4-5', 'A 4-6', 'A 4-7']
selector.get_report_list('MSAinputs2012.csv')
for report in report_list:
	for MSA in selector.report_list[report]:
		report_x = report_4x(report, selector)
		report_x.report_x(MSA, cur)
#selector.report_list['A 4-6'] = ['29620']
#selector.report_list['A 4-5'] = ['29620']




'''