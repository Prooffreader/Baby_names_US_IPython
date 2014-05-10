# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ### U.S. Baby names iPython notebooks #
# 
#   * By David Taylor, [www.prooffreader.com](http://www.prooffreader.com)
#   * using data from United States Social Security Administration
#   * I am making this public in case it gives a head start to those who want to explore this dataset, so they don't have to download and format the data and the python objects used to do preliminary analysis. Please let me know if you find this helpful!
#   * I'm relatively new to Python; often my code is non-pythonic and I tend to use inefficient list iterations that are easy for me to code instead of comprehensions or Boolean indexing that would result in faster processing. Also, everything right now is in IPython notebooks instead of .py with classes, double underscores, etc., because it's more convenient for my workflow in data spelunking. Your mileage may vary, and constructive criticism is very welcome.

# <markdowncell>

# ## Notebook 1: Download data and create pandas dataframes ##
# 
# * Last cell contains descriptions of dataframe schemas
# * Script is smart enough not to download or perform lengthy procedures if the files already exist

# <rawcell>

# Set working path and import libraries

# <codecell>

data_path = "data" 

import os
if not os.path.isdir(data_path): # creates path if it does not exist
    os.makedirs(data_path)

import pandas as pd

# <rawcell>

# Download files from Social Security website unless files already exist in working_path

# <codecell>

os.chdir(data_path)

ssa_url = 'http://www.socialsecurity.gov/oact/babynames/names.zip' 

if not os.path.isfile("names.zip"):
    print "Downloading."
    import urllib
    urllib.urlretrieve(ssa_url, 'names.zip')

if not os.path.isfile("yob1880.txt") or not os.path.isfile("yob2013.txt"):
    print "Extracting."
    import zipfile
    with zipfile.ZipFile('names.zip') as zf:
        for member in zf.infolist():
            zf.extract(member)
            
os.chdir("../")

# <rawcell>

# Create pandas dataframes from U.S. Social Security baby names database and pickle for later use in other notebooks
# 
# This block takes well under a minute on my medium-quality desktop Windows PC.

# <codecell>

os.chdir(data_path)

if (not os.path.isfile("yob.pickle") or 
    not os.path.isfile("names.pickle") or 
    not os.path.isfile("years.pickle")):

    print "Processing."
    
    # read individual files, yob1880.txt, yob1881.txt, etc. and assemble into a dataframe
    years = range(1880, 2014) # stops at 2013: update this when Social Security Administration adds to data 
    parts = []
    part_columns = ['name', 'sex', 'births']
    for year in years:
        path = 'yob' + str(year) + '.txt'
        part_df = pd.read_csv(path, names=part_columns)
        part_df['year'] = year
        parts.append(part_df)
    yob = pd.concat(parts, ignore_index=True)
    
    # add column 'pct': the number of births of that name and sex in that year
    # divided by the total number of births of that sex in that year, multiplied by
    # 100 to turn into a percentage and reduce leading zeroes
    def add_pct(group):
        births = group.births.astype(float)
        group['pct'] = (births / births.sum() * 100)
        return group
    yob = yob.groupby(['year', 'sex']).apply(add_pct)
    #add rank of each name each year each sex
    yob['ranked'] = yob.groupby(['year', 'sex'])['births'].rank(ascending=False)
    yob.to_pickle("yob.pickle")
    
    # names dataframe: discards individual birth or pct values, and instead collects data on unique names.
    # There is one row per unique combination of name and sex.
    yobf = yob[yob.sex == 'F']
    yobm = yob[yob.sex == 'M']
    names_count = pd.DataFrame(data=yobf['name'].value_counts(), columns=['year_count'])
    names_min = pd.DataFrame(data=yobf.groupby('name').year.min(), columns = ['year_min'])
    names_max = pd.DataFrame(data=yobf.groupby('name').year.max(), columns = ['year_max'])
    names_pctsum = pd.DataFrame(data=yobf.groupby('name').pct.sum(), columns = ['pct_sum'])
    names_pctmax = pd.DataFrame(data=yobf.groupby('name').pct.max(), columns = ['pct_max'])
    names_f = names_count.join(names_min)
    names_f = names_f.join(names_max)
    names_f = names_f.join(names_pctsum)
    names_f = names_f.join(names_pctmax)
    names_f['sex'] = "F"
    names_f.reset_index(inplace=True, drop=False)
    names_f.columns = ['name', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max', 'sex']
    names_f = names_f[['name', 'sex', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max']]
    names_count = pd.DataFrame(data=yobm['name'].value_counts(), columns=['year_count'])
    names_min = pd.DataFrame(data=yobm.groupby('name').year.min(), columns = ['year_min'])
    names_max = pd.DataFrame(data=yobm.groupby('name').year.max(), columns = ['year_max'])
    names_pctsum = pd.DataFrame(data=yobm.groupby('name').pct.sum(), columns = ['pct_sum'])
    names_pctmax = pd.DataFrame(data=yobm.groupby('name').pct.max(), columns = ['pct_max'])
    names_m = names_count.join(names_min)
    names_m = names_m.join(names_max)
    names_m = names_m.join(names_pctsum)
    names_m = names_m.join(names_pctmax)
    names_m['sex'] = "M"
    names_m.reset_index(inplace=True, drop=False)
    names_m.columns = ['name', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max', 'sex']
    names_m = names_m[['name', 'sex', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max']]
    names = pd.concat([names_f, names_m], ignore_index=True)
    names.to_pickle('names.pickle')
    
    # create years dataframe. Discards individual name data, aggregating by year.
    total = pd.DataFrame(yob.pivot_table('births', rows='year', cols = 'sex', aggfunc=sum))
    total.reset_index(drop=False, inplace=True)
    total.columns = ['year', 'births_f', 'births_m']
    total['births_t'] = total.births_f + total.births_m
    newnames = pd.DataFrame(data=names.groupby('year_min').year_min.count(), columns = ['firstyearcount'])
    newnames.reset_index(drop=False, inplace=True)
    newnames.columns = ['year', 'new_names']
    uniquenames = pd.DataFrame(columns=['year', 'unique_names'])
    for yr in range(1880, 2013):
        uniquenames = uniquenames.append(pd.DataFrame([{'year':yr, 'unique_names':len(unique(yob[yob.year == yr].name))}]), ignore_index=True)
    years = pd.merge(left=total, right=newnames, on='year', right_index=False, left_index=False)
    years = pd.merge(left=years, right=uniquenames, on='year', right_index=False, left_index=False)
    years.to_pickle('years.pickle')
    
else:
    
    print "Reading from pickle."
    yob = pd.read_pickle('yob.pickle')
    names = pd.read_pickle('names.pickle')
    years = pd.read_pickle('years.pickle')
    
os.chdir("../")

# <rawcell>

# Dataframe schemas:
# Note dataframes have only an arbitrary ordinal index. Indexes and multi-indexes are added later where needed.
# -----------------
# 
# yob = a dataframe with each record comprising a unique name, sex and year.
# Length: approx. 1.76 million records; pickle = ~100 MB
# Columns are:
#     name     String
#     sex      M or F
#     births   Number of birth with that name of that sex during that year;
#              names with fewer than 5 births in a given year are omitted due to privacy concerns
#     year     1880-2012
#     pct      Percentage of births of that sex during that year with that name (float)
#     ranked   Rank of number of births of that name among all births of that sex during that year
# 
# -----------------
# 
# names = a dataframe with each record comprising a unique name and sex, with data for individual years discarded but summary and additional data added.
# Length: approx. 101,000 records; pickle = ~ 7 MB
# Columns are:
#     name              Same as in df
#     sex               Same as in df
#     year_count        Number of different years in which that name appears in dataframe, from 1 to 133.
#     year_min          First year name appears in database
#     year_max          Last year name appears in database
#     pct_sum           Sum of pct field for that name for all years. Not a statistically meaningful number
#                       (because the underlying distribution of names varies from year to year),
#                       but I have found it a useful rough metric during development
#     pct_max           Maxmimum value in pct field for all years, indicating the most popular that name has ever been in the database.
# 
# ------------------
# 
# years = a dataframe with each record comprising a unique year, with individual name data discarded but summary and additional data added.
# Length: 133 records; pickle = ~ 8 kB
# Columns are:
#     year              Same as in df
#     births_f          Number of female births during that year
#     births_m          Number of male births during that year
#     births_t          Total number of births during that year
#     new_names         Number of names that appear for the first time during that year
#     unique_names      Number of different names that appear during that year

# <rawcell>

# Tails of all three dataframes:

# <codecell>

print yob.tail()

# <codecell>

print names.tail()

# <codecell>

print years.tail()

# <codecell>

