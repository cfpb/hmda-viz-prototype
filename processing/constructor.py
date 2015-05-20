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
from respondent_id_compiler import id_compiler

class report_construction(object):
	def __init__(self, report, selector):
		self.report_number = report
		self.original_report_number = report
		self.year = selector.report_list['year'][1]
		self.parsed = parse() #for parsing inputs from rows
		self.connection = connect() #connects to the DB
		self.queries = queries() #query text for all tables
		self.agg = agg() #aggregation functions for all tables

		self.json_builder = self.JSON_constructor_return()
		self.parse_return_string = self.parse_return()
		self.aggregation = self.aggregation_return(self.year, report)
		self.id_compiler = id_compiler()
		self.report_types = {'A':'Aggregate', 'D':'Disclosure', 'N':'National'}

	def disclosure_report(self, MSA, cur):
		table_number = self.report_number[2:]
		report_type = self.report_types[self.report_number[0]]
		#get list of respondent IDs for an MSA
		self.id_compiler.get_ids(cur, MSA, self.year)
		#self.id_compiler.name_id_map = {"0000451965": "WELLS FARGO BANK, NA"}
		for respondent_id in self.id_compiler.name_id_map:
			#print 'working on {respondent}'.format(respondent=self.id_compiler.name_id_map[respondent_id])
			id_condition = '''and respondentid = '{respondent_id}' ;'''.format(respondent_id=respondent_id)

			build_X = build()
			build_X.set_msa_names(cur) #builds a list of msa names as a dictionary

			if self.report_number[2] == '9':
				self.parsed.median_tract_age(cur, MSA) #call the Census API to get median housing stock age for each tract in the MSA
			location = (MSA,) #pass the MSA numbers as a tuple to Psycopg2 (doesn't take singletons)
			if self.report_number[2] == '7':
				self.parsed.inputs['small county flag'] = self.agg.get_small_county_flag(cur, MSA) #checks for small county flag for report 7

			conditions = getattr(self.queries, ('table_' + self.original_report_number[2:].replace(' ','_').replace('-','_') +'_conditions'))()
			conditions = conditions[:-1] + id_condition

			#print conditions
			SQL = (self.queries.SQL_Count + conditions).format(year=self.year, MSA=MSA)
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA "{MSA}", for "{bank}" report "{report}", in {year}'.format(MSA=MSA, report=self.original_report_number, year=self.year, bank= self.id_compiler.name_id_map[respondent_id])
				#TODO: manipulate report name to call query and aggregation functions

				if self.report_number[2] == '4' or self.report_number[2] == '5' or self.report_number[2] == '7' or self.report_number[2] == '8' or self.report_number[2:4] == '11' \
				or self.report_number[2:4] == '12' or (self.report_number[2] == 'A' and self.report_number[4] != '4'):
					self.report_number = self.report_number[:self.report_number.index('-')+1] + 'x' # removes the 1 and adds an x to reports that share a json template for the series

				columns = getattr(self.queries, ('table_' + self.report_number[2:].replace(' ','_').replace('-','_')+'_columns'))()

					#get distinct list of respondent IDs in the MSA
				SQL = (self.queries.SQL_Query + conditions[:-1] + id_condition).format(columns=columns, year=self.year, MSA=MSA)
				cur.execute(SQL, location)

				for num in range(0, count):
					row = cur.fetchone() #get a single LAR row

					getattr(self.parsed, self.parse_return_string)(row) #returns the parse_return string from parse_return and calls it on self.parsed
					#getattr(self.parsed, ('parse_' +self.report_number[2:].replace(' ','_').replace('-','_')))(row)

					if num == 0:
						build_X.set_header(self.parsed.inputs, MSA, report_type, table_number, respondent_id, self.id_compiler.name_id_map[respondent_id]) #sets header information for the JSON object
						table_X = getattr(build_X, self.json_builder)() #returns a string from the JSON_constructor_return function and uses it to call the json building function from A_D_Library

					getattr(self.agg, self.aggregation)(table_X, self.parsed.inputs)

				if self.report_number[2:] == '3-2': #report 3-2 requires out of loop aggregation functions for means and medians
					self.agg.fill_by_median_3_2(table_X, self.parsed.inputs)
					self.agg.fill_by_weighted_mean_3_2(table_X, self.parsed.inputs)
					self.agg.fill_by_weighted_median_3_2(table_X, self.parsed.inputs)
					self.agg.fill_by_mean_3_2(table_X, self.parsed.inputs)

				if self.report_number[2] == '8': #8 series of reports has calculation of denial reason by percent, these are done out of the main aggregation loop
					percent_list = ['races', 'ethnicities', 'minoritystatuses', 'genders', 'incomes']
					index_num = 0
					for item in percent_list:
						self.agg.fill_by_denial_percent(table_X, self.parsed.inputs, index_num, item)
						index_num +=1

				if self.report_number[2:4] == '11' or self.report_number[2:6] == '12-2': #means and medians for 11 and 12 series are done out of main aggregation loop
					self.agg.fill_means_11_12(table_X, build_X)
					self.agg.fill_medians_11_12(table_X, build_X)
					self.agg.fill_weighted_medians_11_12(table_X, self.parsed.inputs)
					self.agg.fill_weighted_means_11_12(table_X, self.parsed.inputs)

				if self.report_number[2:] == 'B': #table B means are done outside the aggregation loop
					self.agg.fill_table_B_mean(table_X, self.parsed.inputs)

				#path matches URL structure for front end
				path = "../" +table_X['type']+"/"+table_X['year']+"/"+self.id_compiler.name_id_map[respondent_id].lower().replace(' ','_').replace(',','')+"/"+build_X.msa_names[MSA].replace(' ', '-').lower() +"/"+table_X['table']
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build_X.write_JSON(table_X['table']+'.json', table_X, path)
				build_X.jekyll_for_report(path) #create and write jekyll file to report path

				#year in the path is determined by the asofdate in the LAR entry
				path2 = "../"+table_X['type']+"/"+table_X['year']+"/"+self.id_compiler.name_id_map[respondent_id].lower().replace(' ','_').replace(',','')+"/"+build_X.msa_names[MSA].replace(' ', '-').lower()+"/" #set path for writing the jekyll file to the msa directory
				build_X.jekyll_for_msa(path2) #create and write jekyll file to the msa path


	def aggregate_report(self, MSA, cur):
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
			print self.report_number
			if self.report_number[2] == '9':
				self.parsed.median_tract_age(cur, MSA) #call the Census API to get median housing stock age for each tract in the MSA
			location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
			if self.report_number[2] == '7':
				self.parsed.inputs['small county flag'] = self.agg.get_small_county_flag(cur, MSA) #checks for small county flag for report 7
				#print self.parsed.inputs['small county flag']
			conditions = getattr(self.queries, ('table_' + self.report_number[2:].replace(' ','_').replace('-','_') +'_conditions'))() #A 4-1 vs A A1

			SQL = (self.queries.SQL_Count + conditions).format(year=self.year, MSA=MSA)
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA "{MSA}", for report "{report}", in {year}'.format(MSA=MSA, report=self.report_number, year=self.year)
				#manipulate report name to call query and aggregation functions

				if self.report_number[2] == '4' or self.report_number[2] == '5' or self.report_number[2] == '7' or self.report_number[2] == '8' or self.report_number[2:4] == '11' \
				or self.report_number[2:4] == '12' or (self.report_number[2] == 'A' and self.report_number[4] != '4'):
					self.report_number = self.report_number[:self.report_number.index('-')+1] + 'x' # removes the 1 and adds an x to reports that share a json template for the series
				#elif self.report_number[2] == 'A' and self.report_number[3] != '4': #reports A1, A2, A3 have the same structure, A4 is different
				#	self.report_number = self.report_number[:-1] + 'x'
				columns = getattr(self.queries, ('table_' + self.report_number[2:].replace(' ','_').replace('-','_')+'_columns'))()

				SQL = (self.queries.SQL_Query + conditions).format(columns=columns, year=self.year, MSA=MSA)

				cur.execute(SQL, location)
				for num in range(0, count):
					row = cur.fetchone() #get a single LAR row
					getattr(self.parsed, self.parse_return_string)(row) #returns the parse_function string from parse_return and calls it on self.parsed

					if num == 0:
						build_X.set_header(self.parsed.inputs, MSA, report_type, table_number, '', '') #sets header information for the JSON object
						table_X = getattr(build_X, self.json_builder)() #returns a string from the JSON_constructor_return function and uses it to call the json building function from A_D_Library

					getattr(self.agg, self.aggregation)(table_X, self.parsed.inputs)

				if self.report_number[2:] == '3-2': #report 3-2 requires out of loop aggregation functions for means and medians
					self.agg.fill_by_median_3_2(table_X, self.parsed.inputs)
					self.agg.fill_by_weighted_mean_3_2(table_X, self.parsed.inputs)
					self.agg.fill_by_weighted_median_3_2(table_X, self.parsed.inputs)
					self.agg.fill_by_mean_3_2(table_X, self.parsed.inputs)

				if self.report_number[2] == '8': #8 series of reports has calculation of denial reason by percent, these are done out of the main aggregation loop
					percent_list = ['races', 'ethnicities', 'minoritystatuses', 'genders', 'incomes']
					index_num = 0
					for item in percent_list:
						self.agg.fill_by_denial_percent(table_X, self.parsed.inputs, index_num, item)
						index_num +=1

				if self.report_number[2:4] == '11' or self.report_number[2:6] == '12-2': #means and medians for 11 and 12 series are done out of main aggregation loop
					self.agg.fill_means_11_12(table_X, build_X)
					self.agg.fill_medians_11_12(table_X, build_X)
					self.agg.fill_weighted_medians_11_12(table_X, self.parsed.inputs)
					self.agg.fill_weighted_means_11_12(table_X, self.parsed.inputs)

				if self.report_number[2:] == 'B': #table B means are done outside the aggregation loop
					self.agg.fill_table_B_mean(table_X, self.parsed.inputs)

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
		if report_number[2:5] == '3-1':
			return 'compile_report_3_1'
		elif report_number[2:5] == '3-2':
			return 'compile_report_3_2'
		elif report_number[2] == '4':
			return 'compile_report_4_x'
		elif report_number[2] == '5':
			return 'compile_report_5_x'
		elif report_number[2] == '7':
			return 'compile_report_7_x'
		elif report_number[2] == '8':
			return 'compile_report_8_x'
		elif report_number[2] == '9':
			return 'compile_report_9_x'
		elif report_number[2:4] == '11':
			return 'compile_report_11_x'
		elif report_number[2:6] == '12-1':
			return 'compile_report_12_1'
		elif report_number[2:6] == '12-2':
			return 'compile_report_12_2'
		elif report_number[2:5] == 'A-1':
			return 'compile_report_A_x'
		elif report_number[2:5] == 'A-2':
			return 'compile_report_A_x'
		elif report_number[2:5] == 'A-3':
			return 'compile_report_A_x'
		elif report_number[2:5] == 'A-4':
			return 'compile_report_A_4'
		elif report_number[2] == 'B':
			return 'compile_report_B'

	def JSON_constructor_return(self):
		if self.report_number[2:5] == '3-1':
			return 'table_3_1_builder'
		elif self.report_number[2:5] == '3-2':
			return 'table_3_2_builder'
		elif self.report_number[2] == '4':
			return 'table_4_x_builder'
		elif self.report_number[2] == '5':
			return 'table_5_x_builder'
		elif self.report_number[2] == '7':
			return 'table_7_x_builder'
		elif self.report_number[2] == '8':
			return 'table_8_x_builder'
		elif self.report_number[2] == '9':
			return 'table_9_x_builder'
		elif self.report_number[2:4] == '11':
			return 'table_11_x_builder'
		elif self.report_number[2:6] == '12-1':
			return 'table_12_1_builder'
		elif self.report_number[2:6] == '12-2':
			return 'table_12_2_builder'
		elif self.report_number[2:5] == 'A-1' or self.report_number[2:5] == 'A-2' or self.report_number[2:5] == 'A-3':
			return 'table_A_x_builder'
		elif self.report_number [2:5]== 'A-4':
			return 'table_A_4_builder'
		elif self.report_number[2] == 'B':
			return 'table_B_builder'
		else:
			print 'json return failed'
			return None

	def parse_return(self):
		if self.report_number[2:5] == '3-1':
			return 'parse_3_1'
		elif self.report_number[2:5] == '3-2':
			return 'parse_3_2'
		elif self.report_number[2] == '4':
			return 'parse_4_x'
		elif self.report_number[2] == '5':
			return 'parse_5_x'
		elif self.report_number[2] == '7':
			return 'parse_7_x'
		elif self.report_number[2] == '8':
			return 'parse_8_x'
		elif self.report_number[2] == '9':
			return 'parse_9_x'
		elif self.report_number[2:4] == '11':
			return 'parse_11_x'
		elif self.report_number[2:4] == '12':
			return 'parse_12_x'
		elif self.report_number[2:5] == 'A-1':
			return 'parse_A_x'
		elif self.report_number[2:5] == 'A-2':
			return 'parse_A_x'
		elif self.report_number[2:5] == 'A-3':
			return 'parse_A_x'
		elif self.report_number[2:5] == 'A-4':
			return 'parse_A_4'
		elif self.report_number[2] == 'B':
			return 'parse_B_x'
		else:
			print 'parse return fail'
			return None