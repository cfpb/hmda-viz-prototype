# NOTES

Here are the URL patterns:
aggregate/year/state/msa-md/report-type
aggregate/year/national/report-type
disclosure/year/bank-name-id/location/report-type
disclosure/year/home-office-city/institution/msa-md/report-type
disclosure/year/home-office-city/home-office-state/
institution/msa-md/report-type
disclosure/year/home-office-state/institution/msa-md/report-type
disclosure/year/loan-state/report-type
disclosure/year/loan-msa-md/report-type

There are some one-offs too.

Need to figure out exact json objects along the whole path.
Take this URL for example:
aggregate/year/state/msa-md/report-type

we would need the type of report json file, the years json file, the states, the msa-md and then the available report types

the problem is that we need to be able to trace the path the whole way, so in the aggregates directory we would need a list of years, in the years directory we would need a list of states, in the states we would need a list of msa-mds, and in there we would need the list of available reports

