import sys

#print sys.path
sys.path.append('/users/roellk/desktop/HMDA/hmda-viz-prototype/processing')
from demographics_indexing import demographics
from test_index import testing

demo = demographics()
testing = testing()

#test rate spread index (for 3.2)
#get a distinct list as csv from the HMDApub file
inputs_list = [
{'rate':'NA   ', 'output': 8}, {'rate':'     ', 'output': 8}, {'rate':'1.55 ', 'output': 0}, {'rate': '2.14 ', 'output': 1}, {'rate':'2.78', 'output': 2},
{'rate':'3.00', 'output':3}, {'rate':'3.50', 'output':4}, {'rate':'5.49 ', 'output': 5}, {'rate':'5.50', 'output' :6}, {'rate':'7.00','output': 7},
{'rate':'0.00', 'output':1}]
for inputs in inputs_list:
	testing.key_return(demo, 'rate_spread_index', inputs, 'rate')

#test rate spread index 11x
#get a distinct list as csv from the HMDApub file
inputs_list = [
{'rate':'NA   ', 'output':0}, {'rate':'     ', 'output':0}, {'rate':'1.55', 'output': 2}, {'rate':'2.01', 'output':3}, {'rate':'2.55', 'output':4},
{'rate':'3.14', 'output':5}, {'rate':'4.00', 'output':6}, {'rate':'5.98', 'output':7}, {'rate':'5.99', 'output':8}, {'rate':'7.99', 'output':9}]
for inputs in inputs_list:
	testing.key_return(demo, 'rate_spread_index_11x', inputs, 'rate')

#test gender index
#make an exhaustive list of combinations
#outputs: 0 = male, 1=female, 2=joint male/female
inputs_list = [
{'app sex':'1', 'co app sex': '1', 'output': 0}, {'app sex':'1', 'co app sex': '2', 'output': 2}, {'app sex':'1', 'co app sex': '3', 'output': 0},
{'app sex':'1', 'co app sex': '4', 'output': 0}, {'app sex':'1', 'co app sex': '5', 'output': 0},
{'app sex':'2', 'co app sex': '1', 'output': 2}, {'app sex':'2', 'co app sex': '2', 'output': 1}, {'app sex':'2', 'co app sex': '3', 'output': 1},
{'app sex':'2', 'co app sex': '4', 'output': 1}, {'app sex':'2', 'co app sex': '5', 'output': 1},
{'app sex':'3', 'co app sex': '1', 'output': 3}, {'app sex':'3', 'co app sex': '2', 'output': 3}, {'app sex':'3', 'co app sex': '3', 'output': 3},
{'app sex':'3', 'co app sex': '4', 'output': 3}, {'app sex':'3', 'co app sex': '5', 'output': 3},
{'app sex':'4', 'co app sex': '1', 'output': 3}, {'app sex':'4', 'co app sex': '2', 'output': 3}, {'app sex':'4', 'co app sex': '3', 'output': 3},
{'app sex':'4', 'co app sex': '4', 'output': 3}, {'app sex':'4', 'co app sex': '5', 'output': 3},]
for inputs in inputs_list:
	testing.basic_return(demo, 'set_gender', inputs)

minority_dict = {'races': [1,2,5,5,0], 'output': 2}
testing.key_return(demo, 'minority_count', minority_dict, 'races')

#testing set_non_white flag
inputs_list = [
{'races': [1,0,0,0,0], 'output': True}, {'races': [5,0,0,0,0], 'output': False}, {'races': [0,0,0,0,5], 'output': False}, {'races': [0,0,0,0,1], 'output': True},
{'races': [1,1,1,1,1], 'output': True}, {'races': [2,5,3,6,0], 'output': True}, {'races': [7,0,0,0,0], 'output': False}]
for inputs in inputs_list:
	testing.key_return(demo, 'set_non_white', inputs, 'races')

#testing set_joint status
inputs_list = [
{'app non white flag': False, 'co non white flag': False, 'output': False}, {'app non white flag': True, 'co non white flag': True, 'output': False},
{'app non white flag': True, 'co non white flag': False, 'output': True}, {'app non white flag': False, 'co non white flag': True, 'output': True}]
for inputs in inputs_list:
	testing.basic_return(demo, 'set_joint', inputs)

#testing set_minority_status
#expand test cases
inputs_list = [
{'race': 7, 'ethnicity': 1, 'output': 0}]
for inputs in inputs_list:
	testing.basic_return(demo, 'set_minority_status', inputs)

#testing set_loan_ethnicity
#expand test cases
inputs_list = [
{'a ethn': '1', 'co ethn': '4', 'output': 0}]
for inputs in inputs_list:
	testing.basic_return(demo, 'set_loan_ethn', inputs)