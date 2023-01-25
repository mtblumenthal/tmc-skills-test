# The Movement Cooperative Skills Test: Matching

## Pulling in the OH Voterfile

The first step of the matching is to pull in the voterfiles from the OH Secretary of State website.  This is done by looping through the links in order by county in alphabetical order (based on how many counties are specified in the counties definition in line 9).

For each url, the url is opened using an agent and converted into a dataframe like a csv and appended into a final dataframe which at the end of the loop will have all the county voterfiles in a single dataframe.

## Pulling in the Matching File

In this job, I have the csv pulling in from the local machine because depending on how this would look in a broader workflow there are a lot of different options on the best way to pull an external csv dependng on how often this workflow would be run with different matching files.

## Cleaning the data

In order to make the matching files and the voterfile compatible, there are a few things that have to be cleaned:

* Splitting the name column in the matching file to first name and last name columns - based on if there is a middle name in the column, split each the name column into two or three columns
* Pull the birth year from the Date of Birth column in the Voterfile
* add columns that are all lowercase so that the joins are not case sensitive
* make sure that the data types match for zipcodes and birth year columns across the voterfile and matching files.

## Matching

