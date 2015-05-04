import requests
#http://api.census.gov/data/2013/acs5?get=NAME,B25035_001E&for=tract:*&in=state:01&key=212402c9545fabd1b7cbe40772f804f877c8547e
#http://api.census.gov/data/2013/acs5?get=NAME,B25035_001E&for&county=073&state=01&tract=000100


#http://api.census.gov/data/2013/acs5?get=NAME,B01001_001E&for=tract:000100&in=state:01+county:073&key=212402c9545fabd1b7cbe40772f804f877c8547e

api_key = '212402c9545fabd1b7cbe40772f804f877c8547e'
api_url = 'http://api.census.gov/data/2013/'
tract = '000100'
state = '01'
county = '073'
r = requests.get('http://api.census.gov/data/2013/acs5?get=NAME,B25035_001E&for=tract:'+tract+'&in=state:'+state+'+county:'+county+'&key='+api_key)
#print(r.url)
median_list =  r.text
print median_list
print '*'*10
print r.json
#print median_list[1][0]
return_list = median_list.split(',')
print return_list[8]
