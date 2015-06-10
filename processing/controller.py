#import json
import time
import psycopg2
import psycopg2.extras
from connector import connect_DB as connect
from builder import build_JSON as build
from selector import report_selector as selector
from constructor import report_construction
from file_check import check_file
from report_list import report_list_maker

connection = connect() #connects to the DB
selector = selector() #holds lists of reports to be generated for each MSA
cur = connection.connect() #creates cursor object connected to HMDAPub2013 sql database, locally hosted postgres
selector.get_report_lists('MSAinputs2013.csv') #fills the dictionary of lists of reports to be generated
build_msa = build() #instantiate the build object for file path, jekyll files
#build_msa.msas_in_state(cur, selector, 'aggregate') #creates a list of all MSAs in each state and places the file in the state's aggregate folder


#List of Alabama MSAs for test state case
#AL_MSAs = ['45180', '45980', '11500', '10760', '42460', '13820', '19460', '23460', '46740', '17980', '12220', '20020', '18980', '33860', '46260', '33660', '19300', '22840', '21460','10700','21640','42820','26620','22520','46220']
AL_MSAs = ['19740']

#report lists for testing
#selector.reports_to_run = ['A B']
#selector.reports_to_run = ['A 11-2']
#selector.reports_to_run = ['D 4-1', 'D 4-2', 'D 4-3', 'D 4-4', 'D 4-6', 'D 4-7']
#selector.reports_to_run = ['A 5-1', 'A 5-2', 'A 5-3', 'A 5-4', 'A 5-5', 'A 5-7']
#selector.reports_to_run = ['A 7-1', 'A 7-2', 'A 7-3', 'A 7-4', 'A 7-5', 'A 7-6', 'A 7-7']
#selector.reports_to_run = ['A 8-1', 'A 8-2', 'A 8-3', 'A 8-4', 'A 8-5', 'A 8-6', 'A 8-7']
#selector.reports_to_run = ['A 11-1', 'A 11-2', 'A 11-3', 'A 11-4', 'A 11-5', 'A 11-6', 'A 11-7', 'A 11-8', 'A 11-9', 'A 11-10']
#selector.reports_to_run = ['D 12-1', 'D 12-2']
#selector.reports_to_run = ['D A-1', 'D A-2', 'D A-3', 'D A-4']
#selector.reports_to_run = ['B']
selector.reports_to_run = ['A 11-1', 'A 11-2', 'D 11-1', 'D 11-2']
#complete report list
#selector.reports_to_run = ['A 3-1', 'A 3-2', 'A 4-1', 'A 4-2', 'A 4-3', 'A 4-4', 'A 4-5', 'A 4-6', 'A 4-7', 'A 5-1', 'A 5-2', 'A 5-3', 'A 5-4', 'A 5-5', 'A 5-7', 'A 7-1', 'A 7-2', 'A 7-3', 'A 7-4', 'A 7-5', 'A 7-6', 'A 7-7', 'A 8-1', 'A 8-2', 'A 8-3', 'A 8-4', 'A 8-5', 'A 8-6', 'A 8-7', 'A 9', 'A 11-1', 'A 11-2', 'A 11-3', 'A 11-4', 'A 11-5', 'A 11-6', 'A 11-7', 'A 11-8', 'A 11-9', 'A 11-10', 'A 12-1', 'A 12-2', 'A A-1', 'A A-2', 'A A-3', 'A A-4', 'A B'] #this needs to be changed to read from the input file
#selector.reports_to_run = ['D 3-1', 'D 3-2', 'D 4-1', 'D 4-2', 'D 4-3', 'D 4-4', 'D 4-5', 'D 4-6', 'D 5-1', 'D 5-2', 'D 5-3', 'D 5-4', 'D 5-5', 'D 7-1', 'D 7-2', 'D 7-3', 'D 7-4', 'D 7-5', 'D 7-6', 'D 8-1', 'D 8-2', 'D 8-3', 'D 8-4', 'D 8-5', 'D 8-6',  'D 11-1', 'D 11-2', 'D 11-3', 'D 11-4', 'D 11-5', 'D 11-6', 'D 11-7', 'D 11-8', 'D 11-9', 'D 11-10', 'D 12-1', 'D 12-2', 'D A-1', 'D A-2', 'D A-3', 'D A-4', 'D B'] #this needs to be changed to read from the input file
#selector.reports_to_run = ['D 11-1']
for i in range(0, len(selector.reports_to_run)):
	selector.report_list[selector.reports_to_run[i]] = AL_MSAs#['33660']
#control loop
total_time_start2 = time.time()
total_time_start = time.clock() #set start time for total report batch
logfile = open('processing_log.txt', 'w')
for report in selector.reports_to_run: #loop over a list of report names
	#if len(selector.report_list[report]) >0:
	start = time.clock() #set start for one report
	start2 = time.time()
	for MSA in selector.report_list[report]: #loop through MSAs flagged for report generation
		if report[0] == 'A':
			aggregate_report = report_construction(report, selector) #instantiate class and set function strings
			aggregate_report.aggregate_report(MSA, cur) #variabalize funciton inputs!!!!
		elif report[0] == 'D':
			disclosure_report = report_construction(report, selector)
			disc_report_start = time.clock()
			disclosure_report.disclosure_report(MSA, cur)
			disc_report_end = time.clock()
			print 'time to run disclosure report', disc_report_end - disc_report_start
	end = time.clock() #set end for one report
	end2 = time.time()

	cpu_report_time = end-start
	clock_report_time = end2-start2
	#logfile.write('{time} CPU time to run report {report} on {date}\n'.format(report=report, time=cpu_report_time, date=time.asctime()))
	logfile.write('{time} human time to run {report} on {date}\n'.format(report=report, time=clock_report_time, date=time.asctime()))
	#print '{time} CPU time to run report {report} on {date}'.format(report=report, time=clock_report_time, date=time.asctime())
	print '{time} human time to run {report} on {date}'.format(report=report, time=clock_report_time, date=time.asctime())

total_time_end = time.clock() #set end time for total batch
total_time_end2 = time.time()
cpu_selection_time = total_time_end - total_time_start
clock_selection_time = total_time_end2 - total_time_start2
logfile.write('{time} time to run entire report selection on {date}\n'.format(time=cpu_selection_time, date=time.asctime()))
logfile.write('{time} human time to run entire report selection on {date}\n'.format(time=clock_selection_time, date=time.asctime()))
logfile.close()
print total_time_end-total_time_start, 'time to run entire report selection on\n', time.asctime()
print total_time_end2 - total_time_start2, 'human time to run entire report selection\n', time.asctime()
#check_file must be run after reports are generated
#report_list = ['A 3-1', 'A 3-2', 'A 4-1', 'A 4-2', 'A 4-3', 'A 4-4', 'A 4-5', 'A 4-6', 'A 4-7', 'A 5-1', 'A 5-2', 'A 5-3', 'A 5-4', 'A 5-5', 'A 5-7', 'A 7-1', 'A 7-2', 'A 7-3', 'A 7-4', 'A 7-5', 'A 7-6', 'A 7-7', 'A 8-1', 'A 8-2', 'A 8-3', 'A 8-4', 'A 8-5', 'A 8-6', 'A 8-7', 'A 11-1', 'A 11-2', 'A 11-3', 'A 11-4', 'A 11-5', 'A 11-6', 'A 11-7', 'A 11-8', 'A 11-9', 'A 11-10', 'A 12-1', 'A 12-2'] #this needs to be changed to read from the input file
#check_file = check_file(build_msa) #needs a report list, state list, and msa list
#check_file.is_file('aggregate', selector.report_list['year'][0], report_list) #creates msa-mds.json files showing which MSAs have reports in the sub folders
#report_lists = report_list_maker(build_msa) #takes a build object
#report_lists.report_lists('aggregate', selector.report_list['year'][0], report_list) #produces a list of all reports available for an MSA

