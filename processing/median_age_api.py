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
