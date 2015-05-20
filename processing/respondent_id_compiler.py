import psycopg2
import psycopg2.extras

class id_compiler(object):
	#selects the distinct list of respondent IDs in an MSA and creates a dictionary mapping the id numbers to institution names
	#this is used to generate disclosure reports by MSA
	def __init__(self):
		self.name_id_map = {}

	def get_ids(self, cur, MSA, year):
		SQL = '''SELECT DISTINCT(respondentid), respondentname FROM HMDAPub{year} WHERE msaofproperty = '{msa}' '''.format(msa=MSA, year=year)
		cur.execute(SQL)
		names = cur.fetchall()
		#print names
		for i in range(0, len(names)):
			self.name_id_map[names[i][0]] = names[i][1]
		#print self.name_id_map
