import json
from collections import OrderedDict
class A_D_library():
    pass

    def set_header(self, inputs, MSA, desc, table_type, table_num): #add a variable for desc_string
        msa = OrderedDict({})
        container['table'] = table_num
        container['type'] = table_type
        container['desc'] = desc
        container['year'] = inputs['year']
        msa['id'] = MSA
        #msa['name'] = inputs['MSA name'] #need to add MSA names to a database or read-in file
        msa['state'] = inputs['state name']
        container['msa'] = msa
        return container

    def set_purchasers32(self):
        from collections import OrderedDict
        purchasers = []
        purchaser_names = ['Loan was not originated or was not sold in calendar year', 'Fannie Mae', 'Ginnie Mae', 'Freddie Mac', 'Farmer Mac', 'Private Securitization', 'Commercial bank, savings bank or association', 'Life insurance co., credit union, finance co.', 'Affiliate institution', 'Other']
        for item in purchaser_names:
            purchasersholding = OrderedDict({})
            purchasersholding['name'] = "{}".format(item)
            purchasersholding['first lien count'] = 0
            purchasersholding['first lien value'] = 0
            purchasersholding['junior lien count'] = 0
            purchasersholding['junior lien value'] = 0
            purchasers.append(purchasersholding)
        return purchasers

    def build_JSON32(self):
        pricinginformation = []
        categories = ['No reported pricing data', 'reported pricing data', 'percentage points above average prime offer rate: only includes loans with APR above the threshold', 'mean', 'median', 'HOEPA Loans']

        for cat in categories:
            holding = OrderedDict({})
            holding['pricing']= "{}".format(cat) #race is overwritten each pass of the loop (keys are unique in dictionaries)
            if cat == 'percentage points above average prime offer rate: only includes loans with APR above the threshold':
                holding['points'] = self.build_rate_spreads()
            else:
                holding['purchasers']  = self.set_purchasers32() #purchasers is overwritten each pass in the holding dictionary
            pricinginformation.append(holding)
        container['pricinginformation'] = pricinginformation
        return container

    def build_rate_spreads(self):
        spreads = []
        rate_spreads = ['3 - 3.99', '4 - 4.99', '5 - 5.99', '6 - 6.99', '7 - 7.99', '8 - 8.99', '9 - 9.99', '10 or more']
        for rate in rate_spreads:
            holding = OrderedDict({})
            holding['point'] = "{}".format(rate)
            holding['purchasers'] = self.set_purchasers32()
            spreads.append(holding)
        return spreads

    def write_JSON(self, name):
        #writes the JSON structure to a file
        import json
        with open(name, 'w') as outfile:
         json.dump(container, outfile, indent = 4, ensure_ascii=False)

start = A_D_library()
container = OrderedDict({})
inputs = {}
MSA = '36540'
inputs['state name'] = 'NE'
inputs['year'] = '2012'
table_num = '3-2'
table_type = 'aggregate'
desc = 'Pricing Information for First and Junio Lien Loans Sold by Type of Purchaser (includes originations only).'
container = start.set_header(inputs, MSA, desc, table_type, table_num)
purch32 = start.set_purchasers32()
table32 = start.build_JSON32()
#rate_tastic = start.build_rate_spreads()
start.write_JSON('test_JSON.json')
#print json.dumps(rate_tastic, indent = 4)
print json.dumps(container, indent=4)

