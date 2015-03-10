import os.path

class file_checker(object):
	pass

class check_file(file_checker):

	def __init__(self, build_object):
		self.state_names = build_object.state_names #this is a dictionary in format {"DE":"Delaware"}
		#self.report_list = report_list #list of reports in format ['A 3-1', 'A 4-1']
		self.msa_names = build_object.state_msa_list

	def is_file(self, report_type, report_year, report_list):
		#report_type is aggregate or disclosure
		path_intro = '/Users/roellk/Desktop/HMDA/hmda-viz-prototype/processing/json/'
		for state, state_name in self.state_names.iteritems(): #loop states -- files live here
			state_path = path_intro + report_type + '/' + report_year + '/' + self.state_names[state].lower()
			print state
			for msa_code, msa_name in self.msa_names[state].iteritems(): #loop MSAs
				print msa_code, msa_name
				msa_path = state_path+ '/' + msa_name #needs to loop through MSAs in a state
				for report in report_list: #loop reports -- folder and file
					file_directory = report[2:]
					file_path = msa_path + '/' + file_directory + '/' + file_directory+'.json' #file directory and file path are the same string
					#print file_path
					if os.path.isfile(file_path) == True:
						print file_path, "*"*10, "huzzah it's here!\n"
						pass

						#add id and name to msa-mds.json
					else:
						#print "booooooo, it's not here"
						pass

