from collections import OrderedDict
import os.path
import json
from builder import build_JSON as build

class report_list_maker(object):
	#generates a list of reports that were created for an MSA or MD. This list is stored in report-list.json in the MSA or MD folder.
	def __init__(self, build_object):
		self.state_names = build_object.state_names #this is a dictionary in format {"DE":"Delaware"}
		self.msa_names = build_object.state_msa_list
		self.build = build() #instantiate build_JSON object to retrieve table names
	def write_JSON(self, name, data, path): #writes a json object to file
		with open(os.path.join(path, name), 'w') as outfile: #writes the JSON structure to a file for the path named by report's header structure
			json.dump(data, outfile, indent=4, ensure_ascii = False)

	def report_lists(self, report_type, report_year, report_list):
		#report_type is aggregate or disclosure
		path_intro = '/Users/roellk/Desktop/HMDA/hmda-viz-prototype/'
		for state, state_name in self.state_names.iteritems(): #loop states
			msa_reports = OrderedDict({})
			state_path = path_intro + report_type + '/' + report_year + '/' + self.state_names[state].replace(' ',  '-').lower()

			for msa_code, msa_name in self.msa_names[state].iteritems(): #loop MSAs -- report list files live here
				msa_path = state_path+ '/' + msa_name #needs to loop through MSAs in a state
				msa = {}
				report_holding = []

				for report in report_list: #loop reports -- folder and file
					file_directory = report[2:]
					file_path = msa_path + '/' + file_directory + '/' + file_directory+'.json' #file directory and file path are the same string

					if os.path.isfile(file_path) == True: #a report exists for the MSA, add the MSA name and id to the msa-mds.json file
						print "adding report {report_number} to report list for {MSA_name} in {state}".format(report_number = file_directory, MSA_name = msa_name, state=state_name)
						holding = OrderedDict({})
						holding['id'] = file_directory
						holding['name'] = self.build.table_headers(file_directory)
						report_holding.append(holding) #add the report name to the list of reports in the MSA
					else:
						pass
				msa_reports['reports'] = report_holding
				if os.path.exists(msa_path): #check if path exists
					self.write_JSON('report-list.json', msa_reports, msa_path) #write report_list file

