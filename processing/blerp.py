from demographics_indexing import demographics

demo=demographics()
print demo.rate_spread_index('1.80')
print demo.rate_spread_index('NA   ')
print demo.rate_spread_index('2.25')
