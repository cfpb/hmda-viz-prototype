import psycopg2
import psycopg2.extras
msa_names = {}
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

def set_msa_names(cursor):
	SQL = '''SELECT DISTINCT name10, geoid_msa, geoid_metdiv
		FROM tract_to_cbsa_2012'''
	cursor.execute(SQL,)
	for row in cursor.fetchall():
		#msa_names[row['geoid_msa']] = str(row['name10'])[:-3].replace(" ", "-")
		cut_point =str(row['name10'])[::-1].rfind(' ', 0, len(str(row['name10'])))
		#print cut_point

		msa_names[row['geoid_msa']] = str(row['name10'])[:-cut_point], row['name10']
		#check in reverse for first space and take all preceding characters
	#return msa_names
def replace_right(source, target, replacement, replacements=None):
	return replacement.join(source.rsplit(target, replacements))
cur = connect()
set_msa_names(cur)
blurp = 'bingbading-derp-dip NA-FA'
glurp = replace_right(blurp, ' ', '-', 1)
print glurp
#print blurp[::-1].rfind(' ', 0, len(blurp))
#print blurp[:-5]

#for key, value in msa_names.iteritems():
#	print key, value
