import os, pandas as pd, numpy as np
from urllib import request
from urllib.request import Request, urlopen
from io import StringIO

#define parameters

#number of counties
counties=4
county=range(1,counties+1)

# import OH voterfile by looping through each county

for i in county:

	#link to each county voterfile 
	url='https://www6.ohiosos.gov/ords/f?p=VOTERFTP:DOWNLOAD::FILE:NO:2:P2_PRODUCT_NUMBER:{}'.format(i)
	
	#read in the file
	request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})
	webpage = urlopen(request_site).read()
	
	#convert byte data to dataframe
	conv=str(webpage,'utf-8')
	data = StringIO(conv) 
	
	#staging dataframe for the individual county voterfile
	df_stg=pd.read_csv(data)
	#print(df_stg.head())

	#create the overall dataframe and append each county after the first into the final dataframe
	if i==1:
		df_final=df_stg

	else:
		df_final=df_final.append(df_stg)

voterfile=df_final

# import csv to match against

match=pd.read_csv("~/Downloads/eng-matching-input-v3.csv")
print(match.head())

# copy of the match dataframe
match_1=match

# clean matching file - split the name column

# add column to count spaces in the name column
match_1['name_count']=match_1['name'].str.count(' ')

# split into two dataframes based on whether there is a middle name/initial
match_first_last=match_1[match_1['name_count'] <= 2]
match_middle=match_1[match_1['name_count'] >= 3]

# split the name column into first and last
match_first_last_stg=match_first_last['name'].str.split(' ', expand=True)
match_first_last['first']=match_first_last_stg[0]
match_first_last['middle']=np.nan
match_first_last['last']=match_first_last_stg[1]

print(match_first_last.head())
# split the name column into first, last, and middle
match_middle_stg=match_first_last['name'].str.split(' ', expand=True)
match_middle['first']=match_middle_stg[0]
match_middle['middle']=match_middle_stg[1]
match_middle['last']=match_middle_stg[2]

# back into single dataframe

match_1=match_first_last.append(match_middle)

#adjust birth year and zipcode datatypes

match_1['birth_year_1']=match_1['birth_year'].astype(str).str[:4]

match_1['zip_1']=match_1["zip"].astype(float)
voterfile['RESIDENTIAL_ZIP_1']=voterfile['RESIDENTIAL_ZIP'].astype(float)

#lowercase names, address, city

match_1["last_lower"]=match_1["last"].str.lower()
match_1["first_lower"]=match_1["first"].str.lower()
match_1["address_lower"]=match_1["address"].str.lower()
match_1["city_lower"]=match_1["city"].str.lower()

voterfile['LAST_NAME_lower']=voterfile['LAST_NAME'].str.lower()
voterfile['FIRST_NAME_lower']=voterfile['FIRST_NAME'].str.lower()
voterfile['RESIDENTIAL_ADDRESS1_lower']=voterfile['RESIDENTIAL_ADDRESS1'].str.lower()
voterfile['RESIDENTIAL_CITY_lower']=voterfile['RESIDENTIAL_CITY'].str.lower()


# clean voterfile - adjust DOB to just birth year
vf_stg=voterfile['DATE_OF_BIRTH'].str.split('-', expand=True)
voterfile['birth_year']=vf_stg[0]

# matching

#first, last, birth year, address, city, zip
print(voterfile[["LAST_NAME_lower", "FIRST_NAME_lower", "birth_year", "RESIDENTIAL_ADDRESS1_lower", "RESIDENTIAL_CITY_lower", "RESIDENTIAL_ZIP_1"]])
print(match_1[["last_lower", "first_lower", "birth_year_1", "address_lower", "city_lower", "zip_1"]])

match_stg=match_1.merge(voterfile, how="inner", left_on=["last_lower", "first_lower", "birth_year_1", "address_lower", "city_lower", "zip_1"],
	right_on=["LAST_NAME_lower", "FIRST_NAME_lower", "birth_year", "RESIDENTIAL_ADDRESS1_lower", "RESIDENTIAL_CITY_lower", "RESIDENTIAL_ZIP_1"])

matched=match_stg
print(matched)

#first, last, birth year, city, zip

#filter out already matched records
match_stg = pd.merge(left=match_1, right=matched, how='left', indicator=True, on='row')
match_stg = match_stg.loc[match_stg._merge == 'left_only', :].drop(columns='_merge')

match_stg=match_1.merge(voterfile, how="inner", left_on=["last_lower", "first_lower", "birth_year_1", "city_lower", "zip_1"],
	right_on=["LAST_NAME_lower", "FIRST_NAME_lower", "birth_year", "RESIDENTIAL_CITY_lower", "RESIDENTIAL_ZIP_1"])

matched=matched.append(match_stg)
print(matched)

#first, last, city, zip

#filter out already matched records
match_stg = pd.merge(left=match_1, right=matched, how='left', indicator=True, on='row')
match_stg = match_stg.loc[match_stg._merge == 'left_only', :].drop(columns='_merge')

match_stg=match_1.merge(voterfile, how="inner", left_on=["last_lower", "first_lower", "city_lower", "zip_1"],
	right_on=["LAST_NAME_lower", "FIRST_NAME_lower", "RESIDENTIAL_CITY_lower", "RESIDENTIAL_ZIP_1"])

matched=matched.append(match_stg)
print(matched)

#first, last, birth year

#filter out already matched records
match_stg = pd.merge(left=match_1, right=matched, how='left', indicator=True, on='row')
match_stg = match_stg.loc[match_stg._merge == 'left_only', :].drop(columns='_merge')

match_stg=match_1.merge(voterfile, how="inner", left_on=["last_lower", "first_lower", "birth_year_1"],
	right_on=["LAST_NAME_lower", "FIRST_NAME_lower", "birth_year"])

matched=matched.append(match_stg)
print(matched)

#final dataframe:
matched=matched[["row", "name", "birth_year", "address", "city", "zip","SOS_VOTERID"]]

