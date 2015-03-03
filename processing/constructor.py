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
		self.query_string = self.query_return(self.year, report)
		self.aggregation = self.aggregation_return(self.year, report)
		self.count_string = self.count_return(self.year, report)
		self.report_number = report


	def aggregation_return(self, year, report_number):
		if report_number == 'A 3-1':
			return 'build_report_31'
		elif report_number == 'A 3-2':
			return 'build_report_32'
		elif report_number[:3] == 'A 4':
			return 'build_report4x'

	def JSON_constructor_return(self, report_number):
		if report_number == 'A 3-1':
			return 'table_31_builder'
		elif report_number == 'A 3-2':
			return 'table_32_builder'
		elif report_number[:3] == 'A 4':
			return 'table_4x_builder'

	def parse_return(self, report_number):
		if report_number == 'A 3-1':
			return 'parse_t31'
		elif report_number == 'A 3-2':
			return 'parse_t32'
		elif report_number[:3] == 'A 4':
			return 'parse_t4x'

	def query_return(self, year, report_number):
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

	def count_return(self, year, report_number):
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

	def report_x(self, MSA):
		table_number = self.report_number[2:]
		if self.report_number[0] == 'A':
			report_type = 'Aggregate'
		elif self.report_number[0] == 'D':
			report_type = 'Disclosure'
		elif self.report_number[0] == 'N':
			report_type = 'National'

		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres

		#for MSA in selector.report_list[report_number]: #take this loop out
		build_X = build()
		build_X.set_msa_names(cur) #builds a list of msa names as a dictionary
		location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)

		SQL = getattr(self.queries, self.count_string)()
		cur.execute(SQL, location)
		count = int(cur.fetchone()[0])

		if count > 0:
			print count, 'LAR rows in MSA %s, for report %s, in %s' %(MSA, self.report_number, self.year)

			SQL = getattr(self.queries, self.query_string)()
			cur.execute(SQL, location)
			for num in range(0, count):
				row = cur.fetchone()
				getattr(self.parsed, self.parse_function)(row)
				if num == 0:
					build_X.set_header(self.parsed.inputs, MSA, report_type, table_number)
					table_X = getattr(build_X, self.json_builder)()

				#this line needs generalization
				getattr(self.agg, self.aggregation)(table_X, self.parsed.inputs)
				#self.agg.build_report4x(table_X, self.parsed.inputs)
			path = "json" + "/" +table_X['type']+"/"+table_X['year']+"/"+build_X.get_state_name(table_X['msa']['state']).replace(' ', '-').lower()+"/"+build_X.msa_names[MSA].replace(' ', '-').lower()+"/"+table_X['table']
			if not os.path.exists(path): #check if path exists
				os.makedirs(path) #if path not present, create it
			build_X.write_JSON(table_X['table']+'.json', table_X, path)
			#use an if exists check for jekyll files
			build_X.jekyll_for_report(path) #create and write jekyll file to report path
			#year in the path is determined by the asofdate in the LAR entry
			path2 = "json"+"/"+table_X['type']+"/"+table_X['year']+"/"+build_X.get_state_name(table_X['msa']['state']).replace(' ', '-').lower()+"/"+build_X.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
			build_X.jekyll_for_msa(path2) #create and write jekyll file to the msa path
'''
	def report_47(self, selector):
		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 4-7']:
			build47 = build()
			build47.set_msa_names(cur) #builds a list of msa names as a dictionary
			location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
			if selector.report_list['year'][1] == '2012':
				SQL = self.queries.count_rows_47_2012()
			elif selector.report_list['year'][1] == '2013':
				SQL = self.queries.count_rows_47_2013()
			else:
				print "invalid year in selection"
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA %s, for report 4-7, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2012':
					SQL = self.queries.table_4_3_2012()
				elif selector.report_list['year'][1] == '2013':
					SQL = self.queries.table_4_3_2013()
				else:
					print "invalid year in input file"

				cur.execute(SQL, location)
				for num in range(0, count):
					row = cur.fetchone()
					self.parsed.parse_t4x(row)
					if num == 0:
						build47.set_header(self.parsed.inputs, MSA, build47.table_headers('4-7'), 'Aggregate', '4-7')
						table47 = build47.table_4x_builder()

					self.agg.build_report4x(table47, self.parsed.inputs)
				path = "json" + "/" +table47['type']+"/"+table47['year']+"/"+build47.get_state_name(table47['msa']['state']).lower()+"/"+build47.msa_names[MSA].replace(' ', '-').lower()+"/"+table47['table']
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build47.write_JSON(table47['table']+'.json', table47, path)
				build47.jekyll_for_report(path) #create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table47['type']+"/"+table47['year']+"/"+build47.get_state_name(table47['msa']['state']).lower()+"/"+build47.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build47.jekyll_for_msa(path2) #create and write jekyll file to the msa path

	def report_46(self, selector):
		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 4-6']:
			build46 = build()
			build46.set_msa_names(cur) #builds a list of msa names as a dictionary
			location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
			if selector.report_list['year'][1] == '2012':
				SQL = self.queries.count_rows_46_2012()
			elif selector.report_list['year'][1] == '2013':
				SQL = self.queries.count_rows_46_2013()
			else:
				print "invalid year in selection"
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA %s, for report 4-6, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2012':
					SQL = self.queries.table_4_3_2012()
				elif selector.report_list['year'][1] == '2013':
					SQL = self.queries.table_4_3_2013()
				else:
					print "invalid year in input file"

				cur.execute(SQL, location)
				for num in range(0, count):
					row = cur.fetchone()
					self.parsed.parse_t4x(row)
					if num == 0:
						build46.set_header(self.parsed.inputs, MSA, build46.table_headers('4-6'), 'Aggregate', '4-6')
						table46 = build46.table_4x_builder()

					self.agg.build_report4x(table46, self.parsed.inputs)
				path = "json" + "/" +table46['type']+"/"+table46['year']+"/"+build46.get_state_name(table46['msa']['state']).lower()+"/"+build46.msa_names[MSA].replace(' ', '-').lower()+"/"+table46['table']
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build46.write_JSON(table46['table']+'.json', table46, path)
				build46.jekyll_for_report(path) #create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table46['type']+"/"+table46['year']+"/"+build46.get_state_name(table46['msa']['state']).lower()+"/"+build46.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build46.jekyll_for_msa(path2) #create and write jekyll file to the msa path

	def report_45(self, selector):
		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 4-5']:
			build45 = build()
			build45.set_msa_names(cur) #builds a list of msa names as a dictionary
			location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
			if selector.report_list['year'][1] == '2012':
				SQL = self.queries.count_rows_45_2012()
			elif selector.report_list['year'][1] == '2013':
				SQL = self.queries.count_rows_45_2013()
			else:
				print "invalid year in selection"
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA %s, for report 4-5, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2012':
					SQL = self.queries.table_4_5_2012()
				elif selector.report_list['year'][1] == '2013':
					SQL = self.queries.table_4_5_2013()
				else:
					print "invalid year in input file"

				cur.execute(SQL, location)
				for num in range(0, count):
					row = cur.fetchone()
					self.parsed.parse_t4x(row)
					if num == 0:
						build45.set_header(self.parsed.inputs, MSA, build45.table_headers('4-5'), 'Aggregate', '4-5')
						table45 = build45.table_4x_builder()

					self.agg.build_report4x(table45, self.parsed.inputs)
				path = "json" + "/" +table45['type']+"/"+table45['year']+"/"+build45.get_state_name(table45['msa']['state']).lower()+"/"+build45.msa_names[MSA].replace(' ', '-').lower()+"/"+table45['table']
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build45.write_JSON(table45['table']+'.json', table45, path)
				build45.jekyll_for_report(path) #create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table45['type']+"/"+table45['year']+"/"+build45.get_state_name(table45['msa']['state']).lower()+"/"+build45.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build45.jekyll_for_msa(path2) #create and write jekyll file to the msa path

	def report_44(self, selector):
		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 4-4']:
			build44 = build()
			build44.set_msa_names(cur) #builds a list of msa names as a dictionary
			location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
			if selector.report_list['year'][1] == '2012':
				SQL = self.queries.count_rows_44_2012()
			elif selector.report_list['year'][1] == '2013':
				SQL = self.queries.count_rows_44_2013()
			else:
				print "invalid year in selection"
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA %s, for report 4-4, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2012':
					SQL = self.queries.table_4_4_2012()
				elif selector.report_list['year'][1] == '2013':
					SQL = self.queries.table_4_4_2013()
				else:
					print "invalid year in input file"

				cur.execute(SQL, location)
				for num in range(0, count):
					row = cur.fetchone()
					self.parsed.parse_t4x(row)
					if num == 0:
						build44.set_header(self.parsed.inputs, MSA, build44.table_headers('4-4'), 'Aggregate', '4-4')
						table44 = build44.table_4x_builder()

					self.agg.build_report4x(table44, self.parsed.inputs)
				path = "json" + "/" +table44['type']+"/"+table44['year']+"/"+build44.get_state_name(table44['msa']['state']).lower()+"/"+build44.msa_names[MSA].replace(' ', '-').lower()+"/"+table44['table']
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build44.write_JSON(table44['table']+'.json', table44, path)
				build44.jekyll_for_report(path) #create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table44['type']+"/"+table44['year']+"/"+build44.get_state_name(table44['msa']['state']).lower()+"/"+build44.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build44.jekyll_for_msa(path2) #create and write jekyll file to the msa path

	def report_43(self, selector):

		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 4-3']:
			build43 = build()
			build43.set_msa_names(cur) #builds a list of msa names as a dictionary
			location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
			if selector.report_list['year'][1] == '2012':
				SQL = self.queries.count_rows_43_2012()
			elif selector.report_list['year'][1] == '2013':
				SQL = self.queries.count_rows_43_2013()
			else:
				print "invalid year in selection"
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA %s, for report 4-3, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2012':
					SQL = self.queries.table_4_3_2012()
				elif selector.report_list['year'][1] == '2013':
					SQL = self.queries.table_4_3_2013()
				else:
					print "invalid year in input file"

				cur.execute(SQL, location)
				for num in range(0, count):
					row = cur.fetchone()
					self.parsed.parse_t4x(row)
					if num == 0:
						build43.set_header(self.parsed.inputs, MSA, build43.table_headers('4-2'), 'Aggregate', '4-2')
						table43 = build43.table_4x_builder()

					self.agg.build_report4x(table43, self.parsed.inputs)
				path = "json" + "/" +table43['type']+"/"+table43['year']+"/"+build43.get_state_name(table43['msa']['state']).lower()+"/"+build43.msa_names[MSA].replace(' ', '-').lower()+"/"+table43['table']
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build43.write_JSON(table43['table']+'.json', table43, path)
				build43.jekyll_for_report(path) #create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table43['type']+"/"+table43['year']+"/"+build43.get_state_name(table43['msa']['state']).lower()+"/"+build43.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build43.jekyll_for_msa(path2) #create and write jekyll file to the msa path

	def report_42(self, selector):
		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 4-2']:
			build42 = build()
			build42.set_msa_names(cur) #builds a list of msa names as a dictionary
			location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
			if selector.report_list['year'][1] == '2012':
				SQL = self.queries.count_rows_42_2012()
			elif selector.report_list['year'][1] == '2013':
				SQL = self.queries.count_rows_42_2013()
			else:
				print "invalid year in selection"
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA %s, for report 4-2, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2012':
					SQL = self.queries.table_4_2_2012()
				elif selector.report_list['year'][1] == '2013':
					SQL = self.queries.table_4_2_2013()
				else:
					print "invalid year in input file"

				cur.execute(SQL, location)
				for num in range(0, count):
					row = cur.fetchone()
					self.parsed.parse_t4x(row)
					if num == 0:
						build42.set_header(self.parsed.inputs, MSA, build42.table_headers('4-2'), 'Aggregate', '4-2')
						table42 = build42.table_4x_builder()

					self.agg.build_report4x(table42, self.parsed.inputs)
				path = "json" + "/" +table42['type']+"/"+table42['year']+"/"+build42.get_state_name(table42['msa']['state']).lower()+"/"+build42.msa_names[MSA].replace(' ', '-').lower()+"/"+table42['table']
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build42.write_JSON(table42['table']+'.json', table42, path)
				build42.jekyll_for_report(path) #create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table42['type']+"/"+table42['year']+"/"+build42.get_state_name(table42['msa']['state']).lower()+"/"+build42.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build42.jekyll_for_msa(path2) #create and write jekyll file to the msa path

	def report_41(self, selector):
		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 4-1']:
			build41 = build()
			build41.set_msa_names(cur) #builds a list of msa names as a dictionary
			location = (MSA,) #pass the MSA nubmers as a tuple to Psycopg2 (doesn't take singletons)
			if selector.report_list['year'][1] == '2012':
				SQL = self.queries.count_rows_41_2012()
			elif selector.report_list['year'][1] == '2013':
				SQL = self.queries.count_rows_41_2013()
			else:
				print "invalid year in selection"
			cur.execute(SQL, location)
			count = int(cur.fetchone()[0])

			if count > 0:
				print count, 'LAR rows in MSA %s, for report 4-1, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2012':
					SQL = self.queries.table_4_1_2012()
				elif selector.report_list['year'][1] == '2013':
					SQL = self.queries.table_4_1_2013()
				else:
					print "invalid year in input file"

				cur.execute(SQL, location)
				for num in range(0, count):
					row = cur.fetchone()
					self.parsed.parse_t4x(row)
					if num == 0:
						build41.set_header(self.parsed.inputs, MSA, build41.table_headers('4-1'), 'Aggregate', '4-1')
						table41 = build41.table_4x_builder()

					self.agg.build_report4x(table41, self.parsed.inputs)
				path = "json" + "/" +table41['type']+"/"+table41['year']+"/"+build41.get_state_name(table41['msa']['state']).lower()+"/"+build41.msa_names[MSA].replace(' ', '-').lower()+"/"+table41['table']
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build41.write_JSON(table41['table']+'.json', table41, path)
				build41.jekyll_for_report(path) #create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table41['type']+"/"+table41['year']+"/"+build41.get_state_name(table41['msa']['state']).lower()+"/"+build41.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build41.jekyll_for_msa(path2) #create and write jekyll file to the msa path

class report_3x(constructor):
	def __init__(self):
		self.parsed = parse() #for parsing inputs from rows
		self.connection = connect() #connects to the DB
		self.queries = queries() #query text for all tables
		self.agg = agg() #aggregation functions for all tables

	def report_31(self, selector):
		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 3-1']:
			build31 = build() #table 3-1 build object
			build31.set_msa_names(cur)
			location = (MSA,) #pass a tuple list to psycopg2, the library only takes tuples as inputs

			if selector.report_list['year'][1] == '2012': #use the year on the first line of the MSA inputs file to set the query
				SQL = self.queries.count_rows_2012() #get query text for getting count of loans for the MSA
			elif selector.report_list['year'][1] == '2013': #use the year on the first line of the MSA inputs file to set the query
				SQL = self.queries.count_rows_2013() #get query text for getting count of loans for the MSA

			cur.execute(SQL, location) #ping the database for numbers!
			count = int(cur.fetchone()[0]) #get count of rows for the MSA
			#add md numbers to input file list of msas, check name against last 5 digits if msa name has 0 rows or errors on check
			if count > 0:
				print count, 'LAR rows in MSA %s, for report 3-1, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2013': #use the year on the first line of the MSA inputs file to set the query
					SQL = self.queries.table_3_1_2013() #set query text to table 3-1 2013
				elif selector.report_list['year'][1] == '2012': #use the year on the first line of the MSA inputs file to set the query
					SQL = self.queries.table_3_1_2012() #set query text to table 3-1 2012
				else:
					print "something is wrong"
				cur.execute(SQL, location) #execute the query in postgres

				for num in range(0, count): #loop through all LAR rows in the MSA
					row = cur.fetchone() #fetch one row from the LAR
					self.parsed.parse_t31(row) #parse the row and store in the inputs dictionary - parse_inputs.inputs
					if num == 0:
						build31.set_header(self.parsed.inputs, MSA, build31.table_headers('3-1'), 'Aggregate', '3-1') #set the header information for the report
						table31 = build31.table_31_builder() #build the JSON object for the report
					self.agg.build_report_31(table31, self.parsed.inputs) #aggregate loan files into the JSON structure


				path = "json"+"/"+table31['type']+"/"+table31['year']+"/"+build31.get_state_name(table31['msa']['state']).lower()+"/"+build31.msa_names[MSA].replace(' ', '-').lower() + "/" +table31['table']#set path for writing the JSON file by geography
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build31.write_JSON(table31['table']+'.json', table31, path)
				build31.jekyll_for_report(path) #create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table31['type']+"/"+table31['year']+"/"+build31.get_state_name(table31['msa']['state']).lower()+"/"+build31.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build31.jekyll_for_msa(path2) #create and write jekyll file to the msa path
			else:
				pass #do nothing if no LAR rows exist for the MSA
	def report_32(self, selector):
		cur = self.connection.connect() #creates cursor object connected to HMDAPub2012 sql database, locally hosted postgres
		for MSA in selector.report_list['A 3-2']: #loop over all MSAs that had report 3-2 flagged for creation
			build32 = build() #table 3-2 build object
			build32.set_msa_names(cur)
			location = (MSA,)
			if selector.report_list['year'][1] == '2013': #use the year on the first line of the MSA inputs file to set the query
				SQL = self.queries.count_rows_2013()
			elif selector.report_list['year'][1] == '2012': #use the year on the first line of the MSA inputs file to set the query
				SQL = self.queries.count_rows_2012()
			cur.execute(SQL, location) #Query the database for number of rows in the LAR in the MSA
			count = int(cur.fetchone()[0]) #get tuple of LAR rows in MSA
			#end = int(count[0]) #convert the tuple to int for use in the control loop
			if count > 0:
				print count, 'LAR rows in MSA %s, for report 3-2, in %s' %(MSA, selector.report_list['year'][1])
				if selector.report_list['year'][1] == '2013':
					SQL = self.queries.table_3_2_2013() #set query text for table 3-2
				elif selector.report_list['year'][1] == '2012':
					SQL = self.queries.table_3_2_2012() #set query text for table 3-2
				else:
					print "something is wrong"
				cur.execute(SQL, location)
				for num in range(0,count):
					row = cur.fetchone() #pull a single row for parsing and aggregation
					self.parsed.parse_t32(row) #parse the row into a dictionary
					if num == 0:
						build32.set_header(self.parsed.inputs, MSA, build32.table_headers('3-2'), 'Aggregate', '3-2') #set the header information for the report
						table32 = build32.table_32_builder() #build the JSON object for the report
					self.agg.build_report_32(table32, self.parsed.inputs)
				self.agg.by_median(table32, self.parsed.inputs) #this stays outside the loop
				self.agg.by_mean(table32, self.parsed.inputs) #this stays outside the loop

				#move this section into the library
				MSA_name = 'council bluffs' # temp until sql table is modified: should be table31['msa']['name']
				path = "json"+"/"+table32['type']+"/"+table32['year']+"/"+build32.get_state_name(table32['msa']['state']).lower()+"/"+build32.msa_names[MSA].replace(' ', '-').lower() + "/" + table32['table'] #directory path to store JSON object
				if not os.path.exists(path): #check if path exists
					os.makedirs(path) #if path not present, create it
				build32.write_JSON(table['table']+'.json', table32, path) #write the json into the correct path
				build32.jekyll_for_report(path)#create and write jekyll file to report path
				#year in the path is determined by the asofdate in the LAR entry
				path2 = "json"+"/"+table32['type']+"/"+table32['year']+"/"+build32.get_state_name(table32['msa']['state']).lower()+"/"+build32.msa_names[MSA].replace(' ', '-').lower() #set path for writing the jekyll file to the msa directory
				build32.jekyll_for_msa(path2) #create and write jekyll file to the msa path

			else:
				pass #do nothing if no LAR rows exist for the MSA




'''