import sys

#print sys.path
sys.path.append('/users/roellk/desktop/HMDA/hmda-viz-prototype/processing')
from demographics_indexing import demographics

from nose.tools import assert_equals
from nose_parameterized import parameterized

# #get a distinct list as csv from the HMDApub file
@parameterized([
	('NA   ', 8),
	('     ',   8),
	('1.55', 0),
	('2.14', 1),
	('2.78', 2),
	('3.00', 3),
	('3.50', 4),
	('5.49', 5),
	('5.50', 6),
	('7.00', 7),
	('0.00', None) # value that's out of range
])
def test_rate_spread_index(rate, expected_result): # #test rate spread index (for 3.2)
	# Arrange
	demo = demographics()

	# Action
	actual_result = demo.rate_spread_index_3_2(rate)

	# Assert
	assert_equals(actual_result, expected_result)


@parameterized([
	('NA   ', 0),
	('     ', 0),
	('1.55',  2),
	('2.01', 3),
	('2.55', 4),
	('3.14', 5),
	('4.00', 6),
	('5.98', 7),
	('5.99', 7),
	('7.99', 8)
	])
def test_rate_spread_index_11_x(rate, expected_result):
	# Arrange
	demo = demographics()

	# Action
	actual_result = demo.rate_spread_index_11_x(rate)

	# Assert
	assert_equals(actual_result, expected_result)


@parameterized([
	({'app sex':'1', 'co app sex': '1'}, 0),
	({'app sex':'1', 'co app sex': '2'}, 2),
	({'app sex':'1', 'co app sex': '3'}, 0),
	({'app sex':'1', 'co app sex': '4'}, 0),
	({'app sex':'1', 'co app sex': '5'}, 0),
	({'app sex':'2', 'co app sex': '1'}, 2),
	({'app sex':'2', 'co app sex': '2'}, 1),
	({'app sex':'2', 'co app sex': '3'}, 1),
	({'app sex':'2', 'co app sex': '4'}, 1),
	({'app sex':'2', 'co app sex': '5'}, 1),
	({'app sex':'3', 'co app sex': '1'}, 3),
	({'app sex':'3', 'co app sex': '2'}, 3),
	({'app sex':'3', 'co app sex': '3'}, 3),
	({'app sex':'3', 'co app sex': '4'}, 3),
	({'app sex':'3', 'co app sex': '5'}, 3),
	({'app sex':'4', 'co app sex': '1'}, 3),
	({'app sex':'4', 'co app sex': '2'}, 3),
	({'app sex':'4', 'co app sex': '3'}, 3),
	({'app sex':'4', 'co app sex': '4'}, 3),
	({'app sex':'4', 'co app sex': '5'}, 3)
	])
def test_gender(input_dict, expected_result): #testing set_gender
	# Arrange
	demo = demographics()

	# Action
	actual_result = demo.set_gender(input_dict)

	# Assert
	assert_equals(actual_result, expected_result)


@parameterized([
	([1,2,5,5,0], 2),

	])
def test_minority_count(race_list, expected_result):#testing minority_count
	# Arrange
	demo = demographics()

	# Action
	actual_result = demo.minority_count(race_list)

	# Assert
	assert_equals(actual_result, expected_result)


@parameterized([
	([1,0,0,0,0], True),
	([5,0,0,0,0], False),
	([0,0,0,0,5], False),
	([0,0,0,0,1], True),
	([1,1,1,1,1], True),
	([2,5,3,6,0], True),
	([7,0,0,0,0], None)
	])
def test_set_non_white(input_list, expected_result):
	# Arrange
	demo = demographics()

	# Action
	actual_result = demo.set_non_white(input_list)

	# Assert
	assert_equals(actual_result, expected_result)


@parameterized([
	({'app non white flag': False, 'co non white flag': False}, False),
	({'app non white flag': True, 'co non white flag': True}, False),
	({'app non white flag': True, 'co non white flag': False}, True),
	({'app non white flag': False, 'co non white flag': True}, True)
	])
def test_set_joint(input_dict, expected_result):
	# Arrange
	demo = demographics()

	# Action
	actual_result = demo.set_joint(input_dict)

	# Assert
	assert_equals(actual_result, expected_result)


@parameterized([
	({'race': 7, 'ethnicity': 1}, 3)
	])
#need good test cases here
def test_set_minority_status(input_dict, expected_result):
	# Arrange
	demo = demographics()

	# Action
	actual_result = demo.set_minority_status(input_dict)

	# Assert
	assert_equals(actual_result, expected_result)

@parameterized([
	({'a ethn': '1', 'co ethn': '4'}, 0)
	])
def test_set_ethnicity(input_dict, expected_result):
	# Arrange
	demo = demographics()

	# Action
	actual_result = demo.set_ethnicity(input_dict)

	# Assert
	assert_equals(actual_result, expected_result)

@parameterized([
	(['1','2',' ',' ',' ',], [1,2,0,0,0]),
	([' ','5','3','2',' '], [0,5,3,2,0])
	])
def test_make_race_list(race_list, expected_result):
	# Arrange
	demo = demographics()

	# Action
 	actual_result = demo.make_race_list(race_list)

	# Assert
	assert_equals(actual_result, expected_result)

@parameterized([
	({'joint status': True}, [5,2,1,0,0], 6)
	]) #expand test parameters with actual LAR data from edge cases
def test_set_race(input_dict, race_list, expected_result):
	# Arrange
	demo = demographics()

	# Action
 	actual_result = demo.set_race(input_dict, race_list)

	# Assert
	assert_equals(actual_result, expected_result)
