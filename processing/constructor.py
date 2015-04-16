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

class constructor(object):
	pass

class report_4x(constructor):
	def __init__(self, report, selector):
		self.year = selector.report_list['year'][1]
		self.parsed = parse() #for parsing inputs from rows
		self.connection = connect() #connects to the DB
		self.queries = queries() #query text for all tables
		self.agg = agg() #aggregation functions for all tables
		self.json_builder = self.JSON_constructor_return(report)
		self.parse_function = self.parse_return(report)
		#self.query_string = self.query_return(self.year, report)
		self.aggregation = self.aggregation_return(self.year, report)
		#self.count_string = self.count_return(self.year, report)
		self.report_number = report

	def report_x(self, MSA, cur):
		table_number = self.report_number[2:]
		if self.report_number[0] == 'A':
			report_type = 'Aggregate'
		elif self.report_number[0] == 'D':
			report_type = 'Disclosure'
		elif self.report_number[0] == 'N':
			report_type = 'National'

		#for MSA in selector.report_list[report_number]: #take this loop out
		build_X = build()
		build_X.set_msa_names(cur) #builds a list of msa names as a dictionary

		location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)

		self.parsed.inputs['small county flag'] = self.agg.get_small_county_flag(cur, location)
		conditions = getattr(self.queries, ('table_' + self.report_number.replace(' ','_').replace('-','_') +'_conditions'))()
		SQL = (self.queries.SQL_Count + conditions).format(year=self.year, MSA=MSA)
		cur.execute(SQL, location)
		count = int(cur.fetchone()[0])

		if count > 0:
			print count, 'LAR rows in MSA %s, for report %s, in %s' %(MSA, self.report_number, self.year)
			if self.report_number[2] == '4' or self.report_number[2] == '5' or self.report_number[2] == '7' or self.report_number[2] == '8' or self.report_number[2:4] == '11':
				self.report_number = self.report_number[:self.report_number.index('-')+1] + 'x' #'A 4-1'
			columns = getattr(self.queries, ('table_' + self.report_number[2:].replace(' ','_').replace('-','_')+'_columns'))()

			SQL = (self.queries.SQL_Query + conditions).format(columns=columns, year=self.year, MSA=MSA)

			cur.execute(SQL, location)
			for num in range(0, count):
				row = cur.fetchone()

				getattr(self.parsed, self.parse_function)(row)

				if num == 0:
					build_X.set_header(self.parsed.inputs, MSA, report_type, table_number)

					table_X = getattr(build_X, self.json_builder)()

				getattr(self.agg, self.aggregation)(table_X, self.parsed.inputs)

			if self.report_number[2:] == '3-2': #report 3-2 requires out of loop aggregation functions
				self.agg.by_median(table_X, self.parsed.inputs)
				self.agg.by_weighted_mean(table_X, self.parsed.inputs)
				self.agg.by_weighted_median(table_X, self.parsed.inputs)
				self.agg.by_mean(table_X, self.parsed.inputs)

			if self.report_number[2] == '8': #reports 8-x requires out of loop calculation of denial reason percents

				percent_list = ['races', 'ethnicities', 'minoritystatuses', 'genders', 'incomes']
				index_num = 0
				for item in percent_list:
					self.agg.by_denial_percent(table_X, self.parsed.inputs, index_num, item)
					index_num +=1

			path = "../" +table_X['type']+"/"+table_X['year']+"/"+build_X.get_state_name(table_X['msa']['state']).replace(' ', '-').lower()+"/"+build_X.msa_names[MSA].replace(' ', '-').lower()+"/"+table_X['table']
			if not os.path.exists(path): #check if path exists
				os.makedirs(path) #if path not present, create it
			build_X.write_JSON(table_X['table']+'.json', table_X, path)
			#use an if exists check for jekyll files
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
		elif report_number[:4] == 'A 12':
			return 'build_report12x'

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
		elif report_number[:4] == 'A 12':
			return 'table_12x_builder'

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

