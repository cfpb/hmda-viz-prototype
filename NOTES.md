# NOTES

Here are the URL patterns:

- aggregate/year/state/msa-md/report-type/report.json
/aggregate
	- years.json
	/year
		- states.json
		/state
			- msa-md.json
			/msd-ma
				- report-types.json
				/report-type
					- report.json - what i'll use to generate the table (current pdf)

Example:
/aggregate/2013/Alabama/11500/i.json

the other files along the way, states.json, msa-md.json, etc, are used as the user flows through the front-end to get to the end.
these will allow us to show only the appropriate options.
we should also create static.json files for states, msa-mds, and report-types. these could be used in combination with the dynamic ones to show all options but make some unavailable. it's possible that some reports don't exist down certain paths but having options 'grayed-out' (or something else) will show that the report doesn't exist.


- aggregate/year/national/report-type
- disclosure/year/bank-name-id/location/report-type
- disclosure/year/home-office-city/institution/msa-md/report-type
- disclosure/year/home-office-city/home-office-state/institution/msa-md/report-type
- disclosure/year/home-office-state/institution/msa-md/report-type
- disclosure/year/loan-state/report-type
- disclosure/year/loan-msa-md/report-type







There are some one-offs too.

Need to figure out exact json objects along the whole path. Take this URL for example:

aggregate/year/state/msa-md/report-type

we would need the type of report json file, the years json file, the states per year, the msa-md per state and then the available report types per msa-md

the problem is that we need to be able to trace the path the whole way, so in the aggregates directory we would need a list of years, in the years directory we would need a list of states, in the states we would need a list of msa-mds, and in there we would need the list of available reports

look into json-ld as a possible solution

- http://www.w3.org/TR/json-ld/
- 