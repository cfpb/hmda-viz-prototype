#decimal_test.
from decimal import *
my_list = ['1.5', '2.0', '2.5']
new_list = []
float_list = []
for item in my_list:
    print type(Decimal(item))
    x = Decimal(item)
    y = float(item)
    new_list.append(x)
    float_list.append(y)
for item in new_list:
    x = x + item
    print x
print float_list