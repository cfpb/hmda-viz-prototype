import psycopg2
import psycopg2.extras
def connect():
	with open('/Users/roellk/Desktop/python/credentials.txt', 'r') as f:
		credentials = f.read()
	cred_list = credentials.split(',')
	dbname = cred_list[0]
	user = cred_list[1]
	host = cred_list[2]
	password = cred_list[3]

	connect_string = "dbname=%s user=%s host=%s password =%s" %(dbname, user, host, password) #set a string for connection to SQL
	try:
		conn = psycopg2.connect(connect_string)
		print "i'm connected"
	#if database connection results in an error print the following
	except:
		print "I am unable to connect to the database"
	return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def msas_in_state(cursor, state_list):
	SQL = '''SELECT DISTINCT name10, geoid_msa
		FROM tract_to_cbsa_2012
		WHERE geoid_msa != '     ' and stateabbr = %s;'''
	state_list = []
	for state in state_list:
		location = (state,) #convert state to tuple list for psycopg2
		cursor.execute(SQL, location) #execute SQL statement against server
		msas = [] #holding list for MSA id and names for entire state
		for row in cursor.fetchall():
			temp = {} #holding dict for single MSA id and name
			cut_point =str(row['name10'])[::-1].find(' ')+1 #find index to remove state abbreviations
			temp['id'] = row['geoid_msa'] #set MSA number to id in dict
			temp['name'] = str(row['name10'])[:-cut_point].replace(' ', '-').upper()
			msas.append(temp)
		state_msas['msa-mds'] = msas
		name = state+'.json'
		path = 'json'+"/"+'aggregate'+"/"+'2012'+"/"+state
		print path
		print state_msas
		if not os.path.exists(path): #check if path exists
			os.makedirs(path) #if path not present, create it
		write_json(name, state_msas, path)

def write_JSON(name, data, path):
	#with open(name, 'w') as outfile:
	#	json.dump(data, outfile, indent = 4, ensure_ascii=False)
	with open(os.path.join(path, name), 'w') as outfile: #writes the JSON structure to a file for the path named by report's header structure
		json.dump(data, outfile, indent=4, ensure_ascii = False)
state_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE':'Delaware',
'FL':'Florida', 'GA':'Georgia', 'HI':'Hawaii', 'ID':'Idaho', 'IL':'Illinois', 'IN':'Indiana', 'IA':'Iowa', 'KS':'Kansas', 'KY': 'Kentucky', 'LA':'Louisiana', 'ME': 'Maine', 'MD':'Maryland',
'MA':'Massachusetts', 'MI':'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE':'Nebraska', 'NV':'Nevada', 'NH':'New Hampshire', 'NJ':'New Jersey', 'NM':'New Mexico',
'NY':'New York', 'NC':'North Carolina', 'ND':'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR':'Oregon','PA':'Pennsylvania', 'RI':'Rhode Island', 'SC':'South Carolina',
	'SD':'South Dakota', 'TN':'Tensessee', 'TX':'Texas', 'UT':'Utah', 'VT':'Vermont', 'VA':'Virginia', 'WA': 'Washington', 'WV':'West Virginia', 'WI':'Wisconsin', 'WY':'Wyoming', 'PR':'Puerto Rico', 'VI':'Virgin Islands'}

for key in state_names:
	print key,
state_list = ['AL', 'NE']
state_msas = {}
cur = connect()
msas_in_state(cur, state_list)
