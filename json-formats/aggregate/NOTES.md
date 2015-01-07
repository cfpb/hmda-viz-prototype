- look at each table as an object
- then break down the rows
	- some rows are empty, so those are arrays
	- eg, in table 1 the tracts/county-names are arrays that contain several objects, the dispositions. then the dispositions contain arrays of loan types
- try to look at each table like that

- if possible a consistent naming scheme would be great (leslie can help here), there maybe a dictionary defined already that we can use

- followed a general pattern of using arrays for "like-things"

- each report of same #, 4-1, 4-2, etc are nearly identical
	- so i worked through each at the beginning but the stopped
	- meaning for 7-1 you can easily see 7-2, 7-3, etc
	- same for A's (B falls with A's)

- each report only gives a sample representation of the data, enough to get the structure, there is more to them

- some reports contain 2 tables, one with counts and then one with values, like 11-1
	- in these cases the tables are nearly identical so i merged that data into the same object
	- on the front-end we would just need to loop through again (or build two outputs at the same time) to get the tables