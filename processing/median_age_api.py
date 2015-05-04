import requests
#http://api.census.gov/data/2013/acs5?get=NAME,B25035_001E&for=tract:*&in=state:01&key=212402c9545fabd1b7cbe40772f804f877c8547e
#http://api.census.gov/data/2013/acs5?get=NAME,B25035_001E&for&county=073&state=01&tract=000100


#http://api.census.gov/data/2013/acs5?get=NAME,B01001_001E&for=tract:000100&in=state:01+county:073&key=212402c9545fabd1b7cbe40772f804f877c8547e
class A_D_report(object):
	def __init__(self):
		pass

class median_age_API(A_D_report):
	def get_age(self, state, county, tract):

		with open('/Users/roellk/Documents/api_key.txt', 'r') as f:
			key = f.read()

		api_key = key.strip("'")
		field = 'B25035_001E'
		#documentation on ACS 5 year is here: http://www.census.gov/data/developers/data-sets/acs-survey-5-year-data.html
		#the 2013 A&D reports use the ACS 2010 API
		#field = 'B25034_007E'
		#print api_key
		#api_key = '212402c9545fabd1b7cbe40772f804f877c8547e'
		#api_url = 'http://api.census.gov/data/2013/'
		#tract = '000700'
		#state = '01'
		#county = '015'
		#x = 'http://api.census.gov/data/2013/acs5?get=NAME,B25035_001E&for=tract:'+tract+'&in=state:'+state+'+county:'+county+'&key='+api_key
		#print x
		r = requests.get('http://api.census.gov/data/2010/acs5?get=NAME,'+field+'&for=tract:'+tract+'&in=state:'+state+'+county:'+county+'&key='+api_key)
		#r = requests.get('http://api.census.gov/data/2013/acs5?get=NAME,'+field+'&for=tract:'+tract+'&in=state:'+state+'+county:'+county+'&key='+api_key)
		#print(r.url)
		median_list =  r.text
		#print tract, state, county
		#print median_list
		#print median_list
		return_list = median_list.split(',')
		#print return_list
		#print return_list[8]
		return return_list[8]

#age = median_age_API()
#age.get_age('000100', '01', '073')