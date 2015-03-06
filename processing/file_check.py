import os.path
path_intro = '/Users/roellk/Desktop/HMDA/hmda-viz-prototype/processing/json/'
path =path_intro + report_type + report_year + state + report_number + report_name # 'aggregate/2012/michigan/lansing-east-lansing/4-1/4-1.json'
print os.path.isfile()
if os.path.isfile() == True:
    pass
    #add id and name to msa-mds.json
else:
    pass

#need check path and write paths
if not os.path.exists(path): #check if path exists
    os.makedirs(path) #if path not present, create it