import json
import os
import csv
import psycopg2
import psycopg2.extras
from collections import OrderedDict
from parsing import parse_inputs as parse
from connector import connect_DB as connect
from builder import build_JSON as build
from aggregation import aggregate as agg
from queries import queries
from selector import report_selector as selector

class report_4x(object):
	def __init__(self, report, selector):
		self.year = selector.report_list['year'][1]
		self.parsed = parse() #for parsing inputs from rows
		self.connection = connect() #connects to the DB
		self.queries = queries() #query text for all tables
		self.agg = agg() #aggregation functions for all tables
		self.json_builder = self.JSON_constructor_return(report)
		self.parse_function = self.parse_return(report)
		self.aggregation = self.aggregation_return(self.year, report)
		self.report_number = report

	def report_x(self, MSA, cur):
		table_number = self.report_number[2:]
		if self.report_number[0] == 'A':
			report_type = 'Aggregate'
		elif self.report_number[0] == 'D':
			report_type = 'Disclosure'
		elif self.report_number[0] == 'N':
			report_type = 'National'
		else:
			print 'report type not set'

		build_X = build()
		build_X.set_msa_names(cur) #builds a list of msa names as a dictionary
		if self.report_number[2] == '9':
			self.parsed.median_tract_age(cur, MSA) #call the Census API to get median housing stock age for each tract in the MSA
		location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
		if self.report_number[2 == '7':
			self.parsed.inputs['small county flag'] = self.agg.get_small_county_flag(cur, location) #checks for small county flag for report 7
		conditions = getattr(self.queries, ('table_' + self.report_number.replace(' ','_').replace('-','_') +'_conditions'))() #A 4-1 vs A A1

		SQL = (self.queries.SQL_Count + conditions).format(year=self.year, MSA=MSA)
		cur.execute(SQL, location)
		count = int(cur.fetchone()[0])

		if count > 0:
			print count, 'LAR rows in MSA "{MSA}", for report "{report}", in {year}'.format(MSA=MSA, report=self.report_number, year=self.year)
			#manipulate report name to call query and aggregation functions

			if self.report_number[2] == '4' or self.report_number[2] == '5' or self.report_number[2] == '7' or self.report_number[2] == '8' or self.report_number[2:4] == '11' or self.report_number[2:4] == '12':
				self.report_number = self.report_number[:self.report_number.index('-')+1] + 'x' # removes the 1 and adds an x to reports that share a json template for the series
			elif self.report_number[2] == 'A' and self.report_number[3] != '4': #reports A1, A2, A3 have the same structure, A4 is different
				self.report_number = self.report_number[:-1] + 'x'
			columns = getattr(self.queries, ('table_' + self.report_number[2:].replace(' ','_').replace('-','_')+'_columns'))()

			SQL = (self.queries.SQL_Query + conditions).format(columns=columns, year=self.year, MSA=MSA)

			cur.execute(SQL, location)
			for num in range(0, count):
				row = cur.fetchone() #get a single LAR row
				getattr(self.parsed, self.parse_function)(row) #returns the parse_function string from parse_return and calls it on self.parsed

				if num == 0:
					build_X.set_header(self.parsed.inputs, MSA, report_type, table_number) #sets header information for the JSON object
					table_X = getattr(build_X, self.json_builder)() #returns a string from the JSON_constructor_return function and uses it to call the json building function from A_D_Library

				getattr(self.agg, self.aggregation)(table_X, self.parsed.inputs)

			if self.report_number[2:] == '3-2': #report 3-2 requires out of loop aggregation functions for means and medians
				self.agg.by_median(table_X, self.parsed.inputs)
				self.agg.by_weighted_mean(table_X, self.parsed.inputs)
				self.agg.by_weighted_median(table_X, self.parsed.inputs)
				self.agg.by_mean(table_X, self.parsed.inputs)

			if self.report_number[2] == '8': #8 series of reports has calculation of denial reason by percent, these are done out of the main aggregation loop
				percent_list = ['races', 'ethnicities', 'minoritystatuses', 'genders', 'incomes']
				index_num = 0
				for item in percent_list:
					self.agg.by_denial_percent(table_X, self.parsed.inputs, index_num, item)
					index_num +=1

			if self.report_number[2:4] == '11' or self.report_number[2:6] == '12-2': #means and medians for 11 and 12 series are done out of main aggregation loop
				self.agg.fill_means_11_12(table_X, build_X)
				self.agg.fill_medians_11_12(table_X, build_X)
				self.agg.fill_weighted_medians_11_12(table_X, self.parsed.inputs)

			if self.report_number[2:] == 'B': #table B means are done outside the aggregation loop
				self.agg.table_B_mean(table_X, self.parsed.inputs)

			#path matches URL structure for front end
			path = "../" +table_X['type']+"/"+table_X['year']+"/"+build_X.get_state_name(table_X['msa']['state']).replace(' ', '-').lower()+"/"+build_X.msa_names[MSA].replace(' ', '-').lower()+"/"+table_X['table']
			if not os.path.exists(path): #check if path exists
				os.makedirs(path) #if path not present, create it
			build_X.write_JSON(table_X['table']+'.json', table_X, path)
			build_X.jekyll_for_report(path) #create and write jekyll file to report path

			#year in the path is determined by the asofdate in the LAR entry
			path2 = "../"+table_X['type']+"/"+table_X['year']+"/"+build_X.get_state_name(table_X['msa']['state']).replace(' ', '-').lower()+"/"+build_X.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
			build_X.jekyll_for_msa(path2) #create and write jekyll file to the msa path

	'''find a way to rename the functions in the A_D libary so that string manipulation chan be used to call them insead of having the functions below'''
	def aggregation_return(self, year, report_number):
		if report_number == 'A 3-1':
			return 'build_report_31'
		elif report_number == 'A 3-2':
			return 'build_report_32'
		elif report_number[:3] == 'A 4':
			return 'build_report4x'
		elif report_number[:3] == 'A 5':
			return 'build_report5x'
		elif report_number[:3] == 'A 7':
			return 'build_report7x'
		elif report_number[:3] == 'A 8':
			return 'build_report8x'
		elif report_number[:3] == 'A 9':
			return 'build_report9x'
		elif report_number[:4] == 'A 11':
			return 'build_report11x'
		elif report_number == 'A 12-1':
			return 'build_report12_1'
		elif report_number == 'A 12-2':
			return 'build_report12_2'
		elif report_number == 'A A1':
			return 'build_reportAx'
		elif report_number == 'A A2':
			return 'build_reportAx'
		elif report_number == 'A A3':
			return 'build_reportAx'
		elif report_number == 'A A4':
			return 'build_reportA4'
		elif report_number == 'A B':
			return 'build_reportB'

	def JSON_constructor_return(self, report_number):
		if report_number == 'A 3-1':
			return 'table_31_builder'
		elif report_number == 'A 3-2':
			return 'table_32_builder'
		elif report_number[:3] == 'A 4':
			return 'table_4x_builder'
		elif report_number[:3] == 'A 5':
			return 'table_5x_builder'
		elif report_number[:3] == 'A 7':
			return 'table_7x_builder'
		elif report_number[:3] == 'A 8':
			return 'table_8x_builder'
		elif report_number[:3] == 'A 9':
			return 'table_9x_builder'
		elif report_number[:4] == 'A 11':
			return 'table_11x_builder'
		elif report_number == 'A 12-1':
			return 'table_12_1_builder'
		elif report_number == 'A 12-2':
			return 'table_12_2_builder'
		elif report_number == 'A A1' or report_number == 'A A2' or report_number == 'A A3':
			return 'table_Ax_builder'
		elif report_number == 'A A4':
			return 'table_A4_builder'
		elif report_number == 'A B':
			return 'table_B_builder'

	def parse_return(self, report_number):
		if report_number == 'A 3-1':
			return 'parse_t31'
		elif report_number == 'A 3-2':
			return 'parse_t32'
		elif report_number[:3] == 'A 4':
			return 'parse_t4x'
		elif report_number[:3] == 'A 5':
			return 'parse_t5x'
		elif report_number[:3] == 'A 7':
			return 'parse_t7x'
		elif report_number[:3] == 'A 8':
			return 'parse_t8x'
		elif report_number[:3] == 'A 9':
			return 'parse_t9x'
		elif report_number[:4] == 'A 11':
			return 'parse_t11x'
		elif report_number[:4] == 'A 12':
			return 'parse_t12x'
		elif report_number == 'A A1':
			return 'parse_tAx'
		elif report_number == 'A A2':
			return 'parse_tAx'
		elif report_number == 'A A3':
			return 'parse_tAx'
		elif report_number == 'A A4':
			return 'parse_tA4'
		elif report_number == 'A B':
			return 'parse_tBx'
		else:
			print 'parse return fail'