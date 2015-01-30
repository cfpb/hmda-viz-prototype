#this file holds the classes used to create the A&D reports using the HMDA LAR files combined with Census demographic information

class AD_report(object):
    def __init__(self):
        pass

class report_selector(AD_report):
    pass

class set_race(AD_report):
    pass
    #store FFIEC codes

class set_income_bracket(AD_report):
    pass

class pct_MSA_median(AD_report):
    pass

class parse_inputs(AD_report):
    #needs to take all the variables used in all the reports
    #use if exists logic to pass in a row and parse it to a dictionary
    #does this require standardization of the SQL query to return the same string?
    #check the psycopg2.extras docs on dictcursor
    inputs = {}

    def parse_t31(self, rows): #takes a row from a table 3-1 query and parses it to the inputs dictionary (28 tuples)
        #parsing inputs for report 3.1
        #self.inputs will be returned to for use in the aggregation function
        #filling the applicant and co-applicant race code lists (5 codes per applicant)
        a_race = [race for race in rows[1:6]]
        co_race = [race for race in rows[6:11]]
        #convert ' ' entries to 0 for easier comparisons and loan aggregation
        for i in range(0, 5):
            if a_race[i] == ' ':
                a_race[i] = 0
        for i in range(0,5):
            if co_race[i] == ' ':
                co_race[i] = 0

        #convert string entries to int for easier comparison and loan aggregation
        a_race = [int(race) for race in a_race]
        co_race = [int(race) for race in co_race]

        #add data elements to dictionary
        self.inputs['a ethn'] = rows['applicantethnicity']
        self.inputs['co ethn'] = rows['co_applicantethnicity']
        self.inputs['income'] = rows['applicantincome']
        self.inputs['rate spread'] = rows['ratespread']
        self.inputs['lien status'] = rows['lienstatus']
        self.inputs['hoepa flag'] = rows['hoepastatus']
        self.inputs['purchaser'] = int(rows['purchasertype'])
        self.inputs['loan value'] = float(rows['loanamount'])
        self.inputs['a race'] = a_race #change to the function
        self.inputs['co race']= co_race #change to the function
        self.inputs['race'] = ''
        self.inputs['app non white flag'] = self.set_non_white(a_race)
        self.inputs['co non white flag'] = self.set_non_white(co_race)
        self.inputs['joint status'] = self.set_joint(self.inputs)
        self.inputs['sequence'] = rows['sequencenumber'] # the sequence number to track loans in error checking
        self.inputs['year'] = rows['asofdate']
        self.inputs['state code'] = rows['statecode']
        self.inputs['state name'] = rows['statname']
        self.inputs['census tract'] = rows['censustractnumber'] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
        self.inputs['county code'] = rows['countycode']
        self.inputs['county name'] = rows['countyname']
        self.inputs['minority status'] = self.set_minority_status()
        self.inputs['MSA median income'] = rows['ffiec_median_family_income']
        self.inputs['minority percent'] = rows['minoritypopulationpct']
        self.inputs['tract to MSA income'] = rows['tract_to_msa_md_income']
        #instantiate the ethnicity class and then set loan ethnicity
        ethn = set_ethnicity()
        self.inputs['ethnicity'] = ethn.set_loan_ethn(self.inputs)
    #loop over all elements in both race lists to flag presence of minority race
    #assigning non-white boolean flags for use in joint race status and minority status checks
    #set boolean flag for white/non-white status for applicant
    #need to check App A ID2 for race 6

    def set_non_white(self, race_list): #pass in a list of length 5, return a boolean
        for i in range(0,5):
            if race_list[i] < 5 and race_list[i] != 0:
                return True #flag true if applicant listed a minority race
                break
            elif race_list[i] == 5:
                return False #flag false if the only race listed was white (5)

    def set_joint(self, inputs): #takes a dictionary 'inputs' which is held in the controller(?) object and used to process each loan row
        #joint status exists if one borrower is white and one is non-white
        #check to see if joint status exists
        if self.inputs['app non white flag'] == False and self.inputs['co non white flag'] == False:
            return False #flag false if both applicant and co-applicant are white
        elif self.inputs['app non white flag'] == True and self.inputs['co non white flag'] == True:
            return False #flag false if both applicant and co-applicant are minority
        elif self.inputs['app non white flag'] == True and self.inputs['co non white flag'] ==  False:
            return True #flag true if one applicant is minority and one is white
        elif self.inputs['app non white flag'] == False and self.inputs['co non white flag'] == True:
            return True #flag true if one applicant is minority and one is white

    def set_minority_status(self):
        #determine minority status
        #if either applicant reported a non-white race or an ethinicity of hispanic or latino then minority status is true
        if self.inputs['app non white flag'] == True or self.inputs['co non white flag'] == True or self.inputs['a ethn'] == '1' or self.inputs['co ethn'] == '1':
            return  1
        #if both applicants reported white race and non-hispanic/latino ethnicity then minority status is false
        elif self.inputs['app non white flag'] != True and self.inputs['co non white flag'] != True and self.inputs['a ethn']  != '1' and self.inputs['co ethn'] != '1':
            return 0
        else:
            print 'minority status not set'

class set_ethnicity(AD_report):
    #this function outputs a number code for ethnicity: 0 - hispanic or latino, 1 - not hispanic/latino
    #2 - joint (1 applicant hispanic/latino 1 not), 3 - ethnicity not available
    def set_loan_ethn(self, inputs):
        #if both ethnicity fields are blank report not available(3)
        if inputs['a ethn'] == ' ' and inputs['co ethn'] == ' ':
            return  3 #set to not available

        #determine if the loan is joint hispanic/latino and non hispanic/latino(2)
        elif inputs['a ethn'] == '1' and inputs['co ethn'] != '1':
            return  2 #set to joint
        elif inputs['a ethn'] != '1' and inputs['co ethn'] == '1':
            return  2 #set to joint

        #determine if loan is of hispanic ethnicity (appplicant is hispanic/latino, no co applicant info or co applicant also hispanic/latino)
        elif inputs['a ethn'] == '1' and inputs['co ethn'] == '1':
            return  0
        elif inputs['a ethn'] == '1' and (inputs['co ethn'] == ' ' or inputs['co ethn'] == '3' or inputs['co ethn'] == '4' or inputs['co ethn']== '5'):
            return  0
        elif (inputs['a ethn'] == ' ' or inputs['a ethn'] == '3' or inputs['a ethn'] == '4' or inputs['a ethn'] == '5') and inputs['co ethn'] == '1':
            return  0
        #determine if loan is not hispanic or latino
        elif inputs['a ethn'] == '2' and inputs['co ethn'] != '1':
            return  1
        elif inputs['a ethn'] != '1' and inputs['co ethn'] == '2':
            return  1
        elif (inputs['a ethn'] == '3' or inputs['a ethn'] == '4') and (inputs['co ethn'] != '1' and inputs['co ethn'] != '2'):
            return  3
        else:
            print "error setting ethnicity"


class build_JSON(AD_report):
    pass

class connect_DB(AD_report):
#I'm not sure how to pass the cursor object back to the controller object
    def connect(self):
        import psycopg2
        import psycopg2.extras
        from collections import OrderedDict

        with open('/Users/roellk/Desktop/python/credentials.txt', 'r') as f:
            credentials = f.read()

        cred_list = credentials.split(',')
        dbname = cred_list[0]
        user = cred_list[1]
        host = cred_list[2]
        password = cred_list[3]

        #set a string for connection to SQL
        connect_string = "dbname=%s user=%s host=%s password =%s" %(dbname, user, host, password)

        try:
            conn = psycopg2.connect(connect_string)
            print "i'm connected"
        #if database connection results in an error print the following
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


class set_MSA_income_index(AD_report):
    pass

class queries(AD_report):

    def table_3_1(self):
        #set the SQL statement to select the needed fields to aggregate loans for the table_3 JSON structure
        SQL = '''SELECT
            censustractnumber, applicantrace1, applicantrace2, applicantrace3, applicantrace4, applicantrace5,
            coapplicantrace1, coapplicantrace2, coapplicantrace3, coapplicantrace4, coapplicantrace5,
            applicantethnicity, co_applicantethnicity, applicantincome, ratespread, lienstatus, hoepastatus,
            purchasertype, loanamount, sequencenumber, asofdate, statecode, statname, countycode, countyname,
            ffiec_median_family_income, minoritypopulationpct, tract_to_msa_md_income
            FROM hmdapub2012 WHERE msaofproperty = %s;'''
        return SQL

