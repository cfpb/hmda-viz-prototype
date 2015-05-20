#test a module takes an input and returns an index
class testing(object):
	def __init__(self):
		pass

	def key_return(self, class_name, function_name, input_dict, key):
		if getattr(class_name, function_name)(input_dict[key]) == input_dict['output']:
			print 'passed for output {output}'.format(output=input_dict)
		else:
			print 'FAILED for output {output}'.format(output=input_dict)

	def basic_return(self, class_name, function_name, input_dict):
		if getattr(class_name, function_name)(input_dict) == input_dict['output']:
			print 'passed for output {output}'.format(output=input_dict)
		else:
			print 'FAILED for output {output}'.format(output=input_dict)




