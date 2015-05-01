import os.path
import json

class check_file(object):
	#creates msa-mds.json files that show which MSAs or MDs have reports generated
	def __init__(self, build_object):
		self.state_names = build_object.state_names #this is a dictionary in format {"DE":"Delaware"}
		self.msa_names = build_object.state_msa_list

	def write_JSON(self, name, data, path): #writes a json object to file
		with open(os.path.join(path, name), 'w') as outfile: #writes the JSON structure to a file for the path named by report's header structure
			json.dump(data, outfile, indent=4, ensure_ascii = False)

	def is_file(self, report_type, report_year, report_list):
		#report_type is aggregate or disclosure
		path_intro = '/Users/roellk/Desktop/HMDA/hmda-viz-prototype/'
		for state, state_name in self.state_names.iteritems(): #loop states -- files live here
			state_msas = {}
			state_holding = []
			state_path = path_intro + report_type + '/' + report_year + '/' + self.state_names[state].replace(' ',  '-').lower()

			for msa_code, msa_name in self.msa_names[state].iteritems(): #loop MSAs
				msa_path = state_path+ '/' + msa_name #needs to loop through MSAs in a state

				for report in report_list: #loop reports -- folder and file
					file_directory = report[2:]
					file_path = msa_path + '/' + file_directory + '/' + file_directory+'.json' #file directory and file path are the same string

					if os.path.isfile(file_path) == True: #a report exists for the MSA, add the MSA name and id to the msa-mds.json file
						print 'reports exist in {msa_name} for {state}'.format(msa_name = msa_name, state=state_name)
						msa = {}
						msa['id'] = msa_code
						msa['name'] = msa_name
						state_holding.append(msa)
						state_msas['msa-mds'] = state_holding
						if not os.path.exists(state_path): #check if path exists
							os.makedirs(state_path) #if path not present, create it
						self.write_JSON('msa-mds.json', state_msas, state_path) #creates a JSON file storing each MSA with available reports
						break
					else:
						pass
