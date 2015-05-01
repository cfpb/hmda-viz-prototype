import csv
class report_selector(object):
	def __init__(self):
		self.report_list = {} #fill this dictionary with the headers in the CSV as dict keys

	def initalize_lists(self, infile):
		with open(infile, 'rU') as csvfile:
			msareader = csv.DictReader(csvfile, delimiter = ',', quotechar='"')
			for row in msareader:
				for key in row:
					self.report_list[key] = [] #initialize a value list for each column header in the input file

	def get_report_lists(self, infile):
		#file will have MSA list (entire population)
		#list of FIs in MSA to generate reports for?
		#open the controller file that tells which reports to generate
		self.initalize_lists(infile) #initialize all reports lists
		with open(infile, 'rU') as csvfile:
			msareader = csv.DictReader(csvfile, delimiter = ',', quotechar='"')
			for row in msareader:
				for key in row: # scan through keys to check all report flags in a row
					if row[key] == '1':
						self.report_list[key].append(row['MSA number']) #if an MSA has a report flagged as '1' add it to the generation list
					if key == 'year': #create a year variable for each row, filepath and query should key off this year
						self.report_list[key].append(row['year'])

		#need to find a work around to add lists for disclosure reports that will return lists of FIs and not flags
