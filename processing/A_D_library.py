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
        self.inputs['a ethn'] = rows[11]
        self.inputs['co ethn'] = rows[12]
        self.inputs['income'] = rows[13]
        self.inputs['rate spread'] = rows[14]
        self.inputs['lien status'] = rows[15]
        self.inputs['hoepa flag'] = rows[16]
        self.inputs['purchaser'] = int(rows[17])
        self.inputs['loan value'] = float(rows[18])
        self.inputs['a race'] = a_race
        self.inputs['co race']= co_race
        self.inputs['joint status'] = ''
        self.inputs['race'] = ''
        self.inputs['app non white flag'] = ''
        self.inputs['co non white flag'] = ''
        self.inputs['sequence'] = rows[19] # the sequence number to track loans in error checking
        self.inputs['year'] = rows[20]
        self.inputs['state code'] = rows[21]
        self.inputs['state name'] = rows[22]
        self.inputs['census tract'] = rows[0] # this is currently the 7 digit tract used by the FFIEC, it includes a decimal prior to the last two digits
        self.inputs['county code'] = rows[23]
        self.inputs['county name'] = rows[24]
        self.inputs['minority status'] = ' '
        self.inputs['MSA median income'] = rows[25]
        self.inputs['minority percent'] = rows[26]
        self.inputs['tract to MSA income'] = rows[27]


class set_joint_status(AD_report):
    #loop over all elements in both race lists to flag presence of minority race
    #assigning non-white boolean flags for use in joint race status and minority status checks
    #set boolean flag for white/non-white status for applicant
    #need to check App A ID2 for race 6
    def set_joint(inputs): #takes a dictionary 'inputs' which is held in the controller(?) object and used to process each loan row
        for i in range(0,5):
            if self.inputs['a race'][i] < 5 and self.inputs['a race'][i] != 0:
                self.inputs['app non white flag'] = True #flag true if applicant listed a minority race
                break
            elif self.inputs['a race'][i] == 5:
                self.inputs['app non white flag'] = False

        for i in range(0,5):
            if self.inputs['co race'][i] < 5 and self.inputs['co race'][i] != 0:
                self.inputs['co non white flag'] = True #flag true if co-applicant exists and has a non-white race listed
                break
            elif self.inputs['co race'][i] == 5:
                self.inputs['co non white flag'] = False

        #joint status exists if one borrower is white and one is non-white
        #check to see if joint status exists
        if self.inputs['app non white flag'] == False and self.inputs['co non white flag'] == False:
            self.inputs['joint status'] = False #flag false if both applicant and co-applicant are white
            self.inputs['joint status'] = False #flag false if both applicant and co-applicant are minority
        elif self.inputs['app non white flag'] == True and self.inputs['co non white flag'] ==  False:
            self.inputs['joint status'] = True #flag true if one applicant is minority and one is white
        elif self.inputs['app non white flag'] == False and self.inputs['co non white flag'] == True:
            self.inputs['joint status'] = True #flag true if one applicant is minority and one is white

class set_minority_status(AD_report):
    pass

class set_ethnicity(AD_report):
    pass

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

