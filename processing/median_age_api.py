import requests
class median_age_API(object):
	def get_age(self, state, county, tract):
		try:
			try:
				with open('/Users/roellk/Documents/api_key.txt', 'r') as f:
					key = f.read()

				api_key = key.strip("'")
				field = 'B25035_001E'
			except:
				print "Error loading API key from file"
			#documentation on ACS 5 year is here: http://www.census.gov/data/developers/data-sets/acs-survey-5-year-data.html
			#the 2013 A&D reports use the ACS 2010 API
			r = requests.get('http://api.census.gov/data/2010/acs5?get=NAME,'+field+'&for=tract:'+tract+'&in=state:'+state+'+county:'+county+'&key='+api_key)
			median_list =  r.text
			return_list = median_list.split(',')
			return return_list[8]
		except:
			print "Unable to connect to Census API"

	def get_all_tract_ages_MSA(self, MSA):
		#get list of tracts from cbsa db for the MSA
		# call API for each tract and store the age as a value with the 11 digit tract number as the key
		pass

	def get_all_tract_ages(self):
		pass
		#get a list of MSAs from cbsa db
		#get a list of tracts for each MSA (call get atll tract ages MSA)
		#build a dict of MSAs with lists of dictionaries holding 11 digit tract numbers as keys and median ages as values
		#write to a file