import csv
report_list = {} #fill this dictionary with the headers in the CSV as dict keys

def get_report_lists():
    #file has MSA list (entire population)
    #flag for aggregate
    #flag for each aggregate report (1 print, 0 don't print)
    #list of FIs in MSA to generate reports for?
    #open the controller file that tells which reports to generate
    with open('MSAinputs.csv', 'r') as csvfile:
        msareader = csv.DictReader(csvfile, delimiter = ',', quotechar='"')
        for row in msareader:
            for key in row:
                report_list[key] = []


get_report_lists()
print report_list
