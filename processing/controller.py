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
#use the year column to select whichd databases to connect to (create more functions for each year)
connection = connect() #connects to the DB
selector = selector() #holds lists of reports to be generated for each MSA
cur = connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
selector.get_report_lists('MSAinputs2013.csv') #fills the dictionary of lists of reports to be generated
build_msa = build() #instantiate the build object
#need to make a switch to build aggregate and disclosure MSA in state lists
build_msa.msas_in_state(cur, selector, 'aggregate') #creates a list of all MSAs in each state and places the file in the state's aggregate folder
build_msa.msas_in_state(cur, selector, 'disclosure')#creates a list of all MSAs in each state and places the file in the state's disclosure folder

def aggregation_return(year, report_number):
	if report_number == 'A 3-1':
		return 'build_report_31'
	elif report_number == 'A 3-2':
		return 'build_report_32'
	elif report_number[:3] == 'A 4':
		return 'build_report4x'

def JSON_constructor_return(report_number):
	if report_number == 'A 3-1':
		return 'table_31_builder'
	elif report_number == 'A 3-2':
		return 'table_32_builder'
	elif report_number[:3] == 'A 4':
		return 'table_4x_builder'
def parse_return(report_number):
	if report_number == 'A 3-1':
		return 'parse_t31'
	elif report_number == 'A 3-2':
		return 'parse_t32'
	elif report_number[:3] == 'A 4':
		return 'parse_t4x'

def query_return(year, report_number):
	if year == '2013':
		if report_number == 'A 3-1':
			return 'table_3_1_2013'
		elif report_number == 'A 3-2':
			return 'table_3_2_2013'
		elif report_number == 'A 4-1':
			return 'table_4_1_2013'
		elif report_number == 'A 4-2':
			return 'table_4_2_2013'
		elif report_number == 'A 4-3':
			return 'table_4_3_2013'
		elif report_number == 'A 4-4':
			return 'table_4_4_2013'
		elif report_number == 'A 4-5':
			return 'table_4_5_2013'
		elif report_number == 'A 4-6':
			return 'table_4_6_2013'
		elif report_number == 'A 4-7':
			return 'table_4_7_2013'
	elif year == '2012':
		if report_number == 'A 3-1':
			return 'table_3_1_2012'
		elif report_number == 'A 3-2':
			return 'table_3_2_2012'
		elif report_number == 'A 4-1':
			return 'table_4_1_2012'
		elif report_number == 'A 4-2':
			return 'table_4_2_2012'
		elif report_number == 'A 4-3':
			return 'table_4_3_2012'
		elif report_number == 'A 4-4':
			return 'table_4_4_2012'
		elif report_number == 'A 4-5':
			return 'table_4_5_2012'
		elif report_number == 'A 4-6':
			return 'table_4_6_2012'
		elif report_number == 'A 4-7':
			return 'table_4_7_2012'

def count_return(year, report_number):
	if year == '2013':
		if report_number == 'A 3-1':
			return 'count_rows_2013'
		elif report_number == 'A 3-2':
			return 'count_rows_2013'
		elif report_number == 'A 4-1':
			return 'count_rows_41_2013'
		elif report_number == 'A 4-2':
			return 'count_rows_42_2013'
		elif report_number == 'A 4-3':
			return 'count_rows_43_2013'
		elif report_number == 'A 4-4':
			return 'count_rows_44_2013'
		elif report_number == 'A 4-5':
			return 'count_rows_45_2013'
		elif report_number == 'A 4-6':
			return 'count_rows_46_2013'
		elif report_number == 'A 4-7':
			return 'count_rows_47_2013'
	elif year == '2012':
		if report_number == 'A 3-1':
			return 'count_rows_2012'
		elif report_number == 'A 3-2':
			return 'count_rows_2012'
		elif report_number == 'A 4-1':
			return 'count_rows_41_2012'
		elif report_number == 'A 4-2':
			return 'count_rows_42_2012'
		elif report_number == 'A 4-3':
			return 'count_rows_43_2012'
		elif report_number == 'A 4-4':
			return 'count_rows_44_2012'
		elif report_number == 'A 4-5':
			return 'count_rows_45_2012'
		elif report_number == 'A 4-6':
			return 'count_rows_46_2012'
		elif report_number == 'A 4-7':
			return 'count_rows_47_2012'


report_4x = report_4x()
#report_3x = report_3x()
selector.report_list['A 4-2'] = ['29620']
selector.report_list['A 4-1'] = ['29620']

report_list = ['A 4-2', 'A 4-1']
for report in report_list:
	report_4x.report_x(selector, report, query_return(selector.report_list['year'][1], report), count_return(selector.report_list['year'][1], report), parse_return(report), JSON_constructor_return(report)) #variabalize funciton inputs!!!!


#report_4x.report_47(selector)
#report_4x.report_46(selector)
#report_4x.report_45(selector)
#report_4x.report_44(selector)
#report_4x.report_43(selector)
#report_4x.report_42(selector)
#report_4x.report_41(selector)
#report_3x.report_31(selector)
#report_3x.report_32(selector)




