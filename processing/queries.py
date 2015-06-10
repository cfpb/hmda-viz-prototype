
class queries(object):
	#can I decompose these query parts into lists and concatenate them prior to passing to the cursor?
	#need to standardize field names in order to use the same query across eyars
		#ffiec_median_family_income vs HUD_median_family_income
		#no sequencenumber prior to 2012
	def __init__(self):

		self.SQL_Count = '''SELECT COUNT(msaofproperty) FROM hmdapub{year} WHERE msaofproperty = '{MSA}' '''
		self.SQL_Query = '''SELECT {columns} FROM hmdapub{year} WHERE msaofproperty = '{MSA}' '''

	def table_3_1_conditions(self):
		return ''' and purchasertype != '0' ;'''

	def table_3_2_conditions(self):
		return ''' and actiontype = '1' and purchasertype != '0' ;'''

	def table_4_1_conditions(self):
		return '''and (loantype = '2' or loantype = '3' or loantype = '4') and propertytype !='3' and loanpurpose = '1' ;'''

	def table_4_2_conditions(self):
		return '''and loantype = '1' and propertytype !='3' and loanpurpose = '1' ;'''

	def table_4_3_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '3' ;'''

	def table_4_4_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '2' ;'''

	def table_4_5_conditions(self):
		return '''and propertytype ='3' ;'''

	def table_4_6_conditions(self):
		return '''and propertytype !='3' and occupancy = '2' ;'''

	def table_4_7_conditions(self):
		return '''and propertytype ='2' ;'''

	def table_5_1_conditions(self):
		return '''and propertytype !='3' and loantype !='1' and loanpurpose = '1' ;'''

	def table_5_2_conditions(self):
		return '''and propertytype !='3' and loantype ='1' and loanpurpose = '1' ;'''

	def table_5_3_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '3' ;'''

	def table_5_4_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '2' ;'''

	def table_5_5_conditions(self):
		return '''and propertytype ='3' ;'''

	def table_5_6_conditions(self):
		return '''and occupancy ='1' and propertytype !='3' ;'''

	def table_5_7_conditions(self):
		return '''and propertytype ='2' ;'''

	def table_7_1_conditions(self):
		return '''and loantype != '1' and propertytype !='3' and loanpurpose = '1' ;'''

	def table_7_2_conditions(self):
		return '''and loantype = '1' and propertytype !='3' and loanpurpose = '1' ;'''

	def table_7_3_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '3' ;'''

	def table_7_4_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '2' ;'''

	def table_7_5_conditions(self):
		return '''and propertytype ='3' ;'''

	def table_7_6_conditions(self):
		return '''and propertytype !='3' and occupancy = '2' ;'''

	def table_7_7_conditions(self):
		return '''and propertytype ='3' ;'''

	def table_8_1_conditions(self):
		return '''and loantype != '1' and propertytype != '3' and loanpurpose = '1' ;'''

	def table_8_2_conditions(self):
		return '''and loantype ='1' and propertytype !='3' and loanpurpose = '1' ;'''

	def table_8_3_conditions(self):
		return '''and propertytype != '3' and loanpurpose = '3' ;'''

	def table_8_4_conditions(self):
		return '''and propertytype !='3' and loanpurpose = '2' ;'''

	def table_8_5_conditions(self):
		return '''and propertytype = '3' ;'''

	def table_8_6_conditions(self):
		return '''and occupancy = '2' and propertytype != '3' ;'''

	def table_8_7_conditions(self):
		return '''and propertytype = '2' ;'''

	def table_9_conditions(self):
		return '''and actiontype != '6' and actiontype != '7' and actiontype != '8' and actiontype != '9' ;'''

	def table_11_1_conditions(self):
		return '''and loantype = '2' and loanpurpose = '1' and lienstatus = '1' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_11_2_conditions(self):
		return '''and loantype = '3' and loanpurpose = '1' and lienstatus = '1' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_11_3_conditions(self):
		return '''and loantype = '1' and loanpurpose = '1' and lienstatus = '1' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_11_4_conditions(self):
		return '''and loantype = '1' and loanpurpose = '1' and lienstatus = '2' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_11_5_conditions(self):
		return '''and loantype = '2' and loanpurpose = '3' and lienstatus = '1' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_11_6_conditions(self):
		return '''and loantype = '3' and loanpurpose = '3' and lienstatus = '1' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_11_7_conditions(self):
		return '''and loantype = '1' and loanpurpose = '3' and lienstatus = '1' and propertytype = '1' and occupancy = '1' and actiontype = '1';'''

	def table_11_8_conditions(self):
		return '''and loantype = '1' and loanpurpose = '3' and lienstatus = '2' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_11_9_conditions(self):
		return '''and loantype = '1' and loanpurpose = '2' and lienstatus = '1' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_11_10_conditions(self):
		return '''and loantype = '1' and loanpurpose = '2' and lienstatus = '2' and propertytype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_12_1_conditions(self):
		return ''' and loantype = '1' and propertytype = '2' and loanpurpose = '1' and lienstatus = '1' and occupancy = '1' ;'''

	def table_12_2_conditions(self):
		return ''' and loantype = '1' and propertytype = '2' and loanpurpose = '1' and lienstatus = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_A_1_conditions(self):
		return ''' and propertytype = '1' ;'''

	def table_A_2_conditions(self):
		return ''' and propertytype = '2' ;'''

	def table_A_3_conditions(self):
		return ''' and propertytype = '3' ;'''

	def table_A_4_conditions(self):
		return ''' and loantype = '1' and loanpurpose = '1' and lienstatus = '1' and propertytype = '1' ;'''

	def table_B_conditions(self):
		return ''' and loantype = '1' and occupancy = '1' and actiontype = '1' ;'''

	def table_3_1_columns(self):
		return '''censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, hoepastatus,
			purchasertype, loanamount, asofdate, statecode, statename, countycode, countyname,
			ffiec_median_family_income, minoritypopulationpct, tract_to_msa_md_income, sequencenumber'''

	def table_3_2_columns(self):
		return '''censustractnumber,  ratespread, lienstatus, loanamount, hoepastatus, purchasertype, asofdate, statecode, statename, countycode, countyname'''

	def table_4_x_columns(self):
		return '''censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate, statecode,
			statename, countycode, countyname, ffiec_median_family_income, sequencenumber, actiontype,
			applicantsex, coapplicantsex, occupancy'''

	def table_5_x_columns(self):
		return '''applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, loanamount, asofdate,
			actiontype, ffiec_median_family_income, statecode, statename, sequencenumber '''

	def table_7_x_columns(self):
		return '''minoritypopulationpct, actiontype, loanamount, ffiec_median_family_income,
			tract_to_msa_md_income, asofdate, statecode, statename, censustractnumber,
			countycode, msaofproperty '''

	def table_8_x_columns(self):
		return '''applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, asofdate, applicantsex,
			coapplicantsex, denialreason1, denialreason2, denialreason3, ffiec_median_family_income,
			statecode, statename, censustractnumber, countycode, countyname '''

	def table_9_columns(self):
		return '''loantype, loanpurpose, propertytype, actiontype, asofdate, censustractnumber, statecode, statename,
			msaofproperty, countyname, countycode, occupancy, loanamount'''

	def table_11_x_columns(self):
		return '''applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, applicantsex, coapplicantsex,
			minoritypopulationpct, ffiec_median_family_income, statename, statecode, loanamount,
			sequencenumber, asofdate, ratespread, tract_to_msa_md_income, lienstatus'''

	def table_12_x_columns(self):
		return '''applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, applicantsex, coapplicantsex,
			minoritypopulationpct, ffiec_median_family_income, statename, statecode, loanamount,
			sequencenumber, asofdate, ratespread, tract_to_msa_md_income, actiontype '''

	def table_A_x_columns(self):
		return '''loantype, lienstatus, loanpurpose, actiontype, loanamount, propertytype
			msaofproperty, statename, statecode, asofdate, sequencenumber, preapproval, purchasertype
			'''
	def table_A_4_columns(self):
		return '''applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
			coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
			applicantethnicity, coapplicantethnicity, applicantincome, applicantsex, coapplicantsex,
			minoritypopulationpct, ffiec_median_family_income, statename, statecode, loanamount,
			sequencenumber, asofdate, ratespread, tract_to_msa_md_income, lienstatus, preapproval,
			actiontype '''

	def table_B_columns(self):
		return '''loanpurpose, lienstatus, hoepastatus, ratespread, propertytype, msaofproperty
			statecode, statename, asofdate, sequencenumber
			'''