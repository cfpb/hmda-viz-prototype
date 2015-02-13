import csv
'''
with open('MSAinputs.csv', 'r') as csvfile:
    msareader = csv.DictReader(csvfile)
    for row in msareader:
        MSA = row['MSA number']
'''
command_rows = []
report31_list = []
report32_list = []
with open('MSAinputs.csv', 'r') as csvfile:
    msareader = csv.reader(csvfile, delimiter = ',', quotechar='"')
    for row in msareader:
        #print row
        print row[4]
        if row[4] =='1':
            report31_list.append(row[0])
        #command_rows.append(row)
        if row[5] == '1':
            report32_list.append(row[0])
print report31_list
print report32_list
'''
#print command_rows[1:]
for i in range(1, len(command_rows)):
    MSA = command_rows[i][0]
    if command_rows[i][1] == '1':
        print MSA
        print 'do aggregate report 3-1'
    if command_rows[i][3] == '1':
        print MSA
        print 'do aggregate report 3-2'


'''