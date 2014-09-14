
# coding: utf-8

# ### U.S. Baby names iPython notebooks #
# 
#   * By David Taylor, [www.prooffreader.com](http://www.prooffreader.com)
#   * using data from United States Social Security Administration

# ## Download data and create pandas dataframes ##
# 
# * A .py version of this script is %run in other notebooks to load primary dataframes
# * Last cell contains descriptions of dataframe schemas
# * Script is smart enough not to download or perform lengthy procedures if the files already exist

##### Set working path and import libraries

# In[1]:

data_path = "user_data" 

import os
if not os.path.isdir(data_path): # creates path if it does not exist
    os.makedirs(data_path)

import pandas as pd


##### Download files from Social Security website unless files already exist in working_path

# In[2]:

os.chdir(data_path)

ssa_url = 'http://www.socialsecurity.gov/oact/babynames/names.zip' 

if not os.path.isfile("names.zip"):
    print "Downloading."
    import urllib
    urllib.urlretrieve(ssa_url, 'names.zip')
else: print "Data already downloaded."

if not os.path.isfile("yob1880.txt") or not os.path.isfile("yob2013.txt"):
    print "Extracting."
    import zipfile
    with zipfile.ZipFile('names.zip') as zf:
        for member in zf.infolist():
            zf.extract(member)
else: print "Data already extracted."

os.chdir("../")


##### Create pandas dataframes from U.S. Social Security baby names database and pickle for later use in other notebooks  This block takes well under a minute on my medium-quality desktop Windows PC.

# In[3]:

redo_dataframes = False
os.chdir(data_path)

if (redo_dataframes == True or
    not os.path.isfile("yob.pickle") or 
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
    names_count = pd.DataFrame(yobf['name'].value_counts())
    names_count.columns= ['year_count']
    names_min = pd.DataFrame(yobf.groupby('name').year.min()) 
    names_min.columns = ['year_min']
    names_max = pd.DataFrame(yobf.groupby('name').year.max()) 
    names_max.columns = ['year_max']
    names_pctsum = pd.DataFrame(yobf.groupby('name').pct.sum()) 
    names_pctsum.columns = ['pct_sum']
    names_pctmax = pd.DataFrame(yobf.groupby('name').pct.max())
    names_pctmax.columns = ['pct_max']
    names_f = names_count.join(names_min)
    names_f = names_f.join(names_max)
    names_f = names_f.join(names_pctsum)
    names_f = names_f.join(names_pctmax)
    names_f['sex'] = "F"
    names_f.reset_index(inplace=True, drop=False)
    names_f.columns = ['name', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max', 'sex']
    names_f = names_f[['name', 'sex', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max']]
    names_count = pd.DataFrame(yobm['name'].value_counts()) 
    names_count.columns=['year_count']
    names_min = pd.DataFrame(yobm.groupby('name').year.min()) 
    names_min.columns = ['year_min']
    names_max = pd.DataFrame(yobm.groupby('name').year.max()) 
    names_max.columns = ['year_max']
    names_pctsum = pd.DataFrame(yobm.groupby('name').pct.sum()) 
    names_pctsum.columns = ['pct_sum']
    names_pctmax = pd.DataFrame(yobm.groupby('name').pct.max()) 
    names_pctmax.columns = ['pct_max']
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
    total = pd.DataFrame(yob.pivot_table('births', index='year', columns = 'sex', aggfunc=sum))
    total.reset_index(drop=False, inplace=True)
    total.columns = ['year', 'births_f', 'births_m']
    total['births_t'] = total.births_f + total.births_m
    newnames = pd.DataFrame(names.groupby('year_min').year_min.count())
    newnames.columns = ['firstyearcount']
    newnames.reset_index(drop=False, inplace=True)
    newnames.columns = ['year', 'new_names']
    uniquenames = pd.DataFrame()
    for yr in range(1880, 2013):
        uniquenames = uniquenames.append(pd.DataFrame([{'year':yr, 'unique_names':len(yob[yob.year == yr].name.unique())}]), ignore_index=True)
    years = pd.merge(left=total, right=newnames, on='year', right_index=False, left_index=False)
    years = pd.merge(left=years, right=uniquenames, on='year', right_index=False, left_index=False)
    years['sexratio'] = 100.0 * years.births_m / years.births_f
    years.to_pickle('years.pickle')
    
else:
    
    print "Reading from pickle."
    yob = pd.read_pickle('yob.pickle')
    names = pd.read_pickle('names.pickle')
    years = pd.read_pickle('years.pickle')
    
os.chdir("../")


# #### Dataframe schemas: ####
# 
# Note dataframes have only an arbitrary ordinal index. Indexes and multi-indexes are added later where needed.
# 
# -----------------
# 
# yob = a dataframe with each record comprising a unique name, sex and year.
# Length: approx. 1.76 million records; pickle = ~100 MB
# 
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
# 
#     name              Same as in df
#     sex               Same as in df
#     year_count        Number of different years in which that name appears in dataframe, from 1 to 133.
#     year_min          First year name appears in database
#     year_max          Last year name appears in database
#     pct_sum           Sum of pct field for that name for all years. Not a statistically meaningful number
#                       (because the underlying distribution of names varies from year to year),
#                       but I have found it a useful rough metric during development
#     pct_max           Maximum value in pct field for all years, indicating the most popular that name has ever been in the database.
# 
# ------------------
# 
# years = a dataframe with each record comprising a unique year, with individual name data discarded but summary and additional data added.
# Length: 133 records; pickle = ~ 8 kB
# 
#     year              Same as in df
#     births_f          Number of female births during that year
#     births_m          Number of male births during that year
#     births_t          Total number of births during that year
#     new_names         Number of names that appear for the first time during that year
#     unique_names      Number of different names that appear during that year
#     sexratio          Number of boys born per hundred girls
# 

##### Make versions from 1940 on:

# In[5]:

os.chdir(data_path)

if (redo_dataframes == True or
    not os.path.isfile("yob1940.pickle") or 
    not os.path.isfile("names1940.pickle") or 
    not os.path.isfile("years1940.pickle")):

    yob1940 = yob[yob.year >= 1940]
    yob1940.to_pickle("yob1940.pickle")

    yobf = yob1940[yob1940.sex == 'F']
    yobm = yob1940[yob1940.sex == 'M']
    names_count = pd.DataFrame(yobf['name'].value_counts())
    names_count.columns= ['year_count']
    names_min = pd.DataFrame(yobf.groupby('name').year.min()) 
    names_min.columns = ['year_min']
    names_max = pd.DataFrame(yobf.groupby('name').year.max()) 
    names_max.columns = ['year_max']
    names_pctsum = pd.DataFrame(yobf.groupby('name').pct.sum()) 
    names_pctsum.columns = ['pct_sum']
    names_pctmax = pd.DataFrame(yobf.groupby('name').pct.max())
    names_pctmax.columns = ['pct_max']
    names_f = names_count.join(names_min)
    names_f = names_f.join(names_max)
    names_f = names_f.join(names_pctsum)
    names_f = names_f.join(names_pctmax)
    names_f['sex'] = "F"
    names_f.reset_index(inplace=True, drop=False)
    names_f.columns = ['name', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max', 'sex']
    names_f = names_f[['name', 'sex', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max']]
    names_count = pd.DataFrame(yobm['name'].value_counts()) 
    names_count.columns=['year_count']
    names_min = pd.DataFrame(yobm.groupby('name').year.min()) 
    names_min.columns = ['year_min']
    names_max = pd.DataFrame(yobm.groupby('name').year.max()) 
    names_max.columns = ['year_max']
    names_pctsum = pd.DataFrame(yobm.groupby('name').pct.sum()) 
    names_pctsum.columns = ['pct_sum']
    names_pctmax = pd.DataFrame(yobm.groupby('name').pct.max()) 
    names_pctmax.columns = ['pct_max']
    names_m = names_count.join(names_min)
    names_m = names_m.join(names_max)
    names_m = names_m.join(names_pctsum)
    names_m = names_m.join(names_pctmax)
    names_m['sex'] = "M"
    names_m.reset_index(inplace=True, drop=False)
    names_m.columns = ['name', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max', 'sex']
    names_m = names_m[['name', 'sex', 'year_count', 'year_min', 'year_max', 'pct_sum', 'pct_max']]
    names1940 = pd.concat([names_f, names_m], ignore_index=True)
    names1940.to_pickle('names1940.pickle')
    
    # create years dataframe. Discards individual name data, aggregating by year.
    total = pd.DataFrame(yob1940.pivot_table('births', index='year', columns = 'sex', aggfunc=sum))
    total.reset_index(drop=False, inplace=True)
    total.columns = ['year', 'births_f', 'births_m']
    total['births_t'] = total.births_f + total.births_m
    newnames = pd.DataFrame(names.groupby('year_min').year_min.count())
    newnames.columns = ['firstyearcount']
    newnames.reset_index(drop=False, inplace=True)
    newnames.columns = ['year', 'new_names']
    uniquenames = pd.DataFrame()
    for yr in range(1940, 2013):
        uniquenames = uniquenames.append(pd.DataFrame([{'year':yr, 'unique_names':len(yob1940[yob1940.year == yr].name.unique())}]), ignore_index=True)
    years1940 = pd.merge(left=total, right=newnames, on='year', right_index=False, left_index=False)
    years1940 = pd.merge(left=years, right=uniquenames, on='year', right_index=False, left_index=False)
    years1940['sexratio'] = 100.0 * years.births_m / years.births_f
    years1940.to_pickle('years.pickle')
    
else:
    
    print "Reading from pickle (1940+ versions)."
    yob1940 = pd.read_pickle('yob1940.pickle')
    names1940 = pd.read_pickle('names1940.pickle')
    years1940 = pd.read_pickle('years1940.pickle')
    
os.chdir("../")


##### Tails of all three dataframes:

# In[8]:

print "Tail of dataframe 'yob':"
print yob.tail()


# In[9]:

print "\nTail of dataframe 'names':"
print names.tail()


# In[12]:

print "\nTail of dataframe 'years':"
print years.tail()

