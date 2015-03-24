def table_3_1_2013(): #set the SQL statement to select the needed fields to aggregate loans for the table_3 JSON structure
	SQL = '''SELECT
		censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
		coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
		applicantethnicity, coapplicantethnicity, applicantincome, hoepastatus,
		purchasertype, loanamount, asofdate, statecode, statename, countycode, countyname,
		ffiec_median_family_income, minoritypopulationpct, tract_to_msa_md_income, sequencenumber
		FROM hmdapub2013 WHERE msaofproperty = %s;'''
	return SQL

def table_3_1_2012():
	SQL = '''SELECT
		censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
		coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
		applicantethnicity, coapplicantethnicity, applicantincome, hoepastatus,
		purchasertype, loanamount, asofdate, statecode, statename, countycode, countyname,
		ffiec_median_family_income, minoritypopulationpct, tract_to_msa_md_income, sequencenumber
		FROM hmdapub2012 WHERE msaofproperty = %s;'''
	return SQL

def count_rows_2012(): #get the count of rows in the LAR for an MSA, used to run the parsing/aggregation loop
	SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2012 WHERE msaofproperty = %s;'''
	return SQL

def count_rows_2013(): #get the count of rows in the LAR for an MSA, used to run the parsing/aggregation loop
	SQL = '''SELECT COUNT(msaofproperty) FROM hmdapub2013 WHERE msaofproperty = %s;'''
	return SQL



SQL = 'SELECT'
SQL2 = 'count(msaofproperty)'
print SQL +' '+ SQL2