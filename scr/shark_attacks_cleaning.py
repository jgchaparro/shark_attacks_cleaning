# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 09:36:39 2022

@author: Jaime García Chaparro
"""

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import re

#%% Import dataset

raw_full_df = pd.read_csv('../data/attacks_raw.csv', encoding = 'latin1')
full_df = raw_full_df.copy()

#%% Detect NAs

plt.figure(figsize=(10, 6))

sns.heatmap(full_df.isna(),  # mapa de calor
            yticklabels=False,
            cmap='viridis',
            cbar=False)

#%% Rename columns

# Decapitalize and change sep to underscores
new_cols = [c.lower().strip().replace(' ', '_').replace('.', '_') for c in full_df.columns]
full_df.columns = new_cols

# Manual renaming
full_df.rename(columns = {
                    'fatal_(y/n)' : 'fatal', 
                    'investigator_or_source' : 'source',
                    'unnamed:_22' : 'unnamed1',
                    'unnamed:_23' : 'unnamed2'
                    }, inplace = True)


#%% Get subset with information

na_thresh = 15
df = full_df[full_df.isnull().sum(axis=1) < na_thresh]
raw_df = df.copy()

#%% --- !! Detect NAs in subset !! ---

plt.figure(figsize=(10, 6))

p = sns.heatmap(df.isna(),  # mapa de calor
            yticklabels=False,
            cmap='viridis',
            cbar=False)

print(df.isnull().any())

#%% Fill unnamed columns

df['unnamed1'] = 'Yona, si hay que rellenar con algo, ...' 
df['unnamed2'] = '... con algo te rellenaré.' 

#%% Recover `fatal` column

# By default, attacks should not be fatal. Replace to booleans.
df['fatal'] = df['fatal'].fillna('N').replace({'Y' : True, 'N' : False})
df = df.astype({'fatal' : bool})    

# If description contains 'fatal', change `fatal` to True
for st in ['fatal', 'FATAL']:
    fatal_ind = df[df.injury.str.contains(st) == True].index 
    df.loc[fatal_ind, 'fatal'] = True

#%% Recover `sex` column

# Add sex if provided in `name`column
for s, ab in zip(['male', 'female'], ['M', 'F']):
    ind = df[(df.sex.isnull()) & (df.name.str.contains(s))].loc[:, ['sex', 'name']].index
    df.loc[ind.tolist(), 'sex'] = ab

# 'U' for unknown sex
df['sex'] = df['sex'].fillna('U')

#%% Recover `age` column

# Get existent ages
def filter_ages(x):
    """Returns the first int is exists.
    If not, return NaN."""
    
    try:
        return int(re.search('\d+', x).group())
    except:
        return np.nan
    
valid_ages = df.age[~df.age.isnull()].apply(lambda x: filter_ages(x)).dropna()

# Shwo valid ages distribution
plt.hist(valid_ages, bins = 15) # Slightly skewed, use median

# Fill with median
df.age = df.age.apply(lambda x: filter_ages(x)).fillna(valid_ages.median())

#%% Clean `name` column

# Remove males and females

df['name'] = df['name'].replace({'male' : '', 'female' : ''})

df['name'][df.name == ''] = 'Unknown'
df['name'] = df['name'].fillna('Unknown')

#%% Fill `activity` column

df['activity'] = df['activity'].fillna('Unknown')


#%% Fill `injury` column

df['injury'] = df['injury'].fillna('Unknown')

#%% Fill `location` columns

df['location'] = df['location'].fillna('Unknown')
    
#%% Clean `country`, `area`, 'location` columns

df.loc[3387, 'country'] = 'ST. KITTS AND NEVIS'
df.loc[5020, 'country'] = 'FRANCE'

df['country'] = df['country'].fillna('Unknown')
df['area'] = df['country'].fillna('Unknown')
df['location'] = df['country'].fillna('Unknown')

#%% Clean `species`

# Fill NaNs
df['species'] = df['species'].fillna('Unknown')

# Extract size
def detect_measurement(el):
    regex = '(\d+) ?((m)|(meters)|(f(ee)?t)|(\'))'
    search = re.search(regex, el)
    if search != None:
        size = float(search.group(1))
        measurement = search.group(2)
        if 'f' in measurement or measurement == '\'':
            size = round(size * 0.3048, 2)
            return size
        else:
            return size
    
    else: # If empty, add a 0
        return 0 

# Create column for size in meters
size_col = df['species'].apply(lambda x: detect_measurement(x))

# Move next to `species`
i = df.columns.get_loc('species')
df.insert(i + 1, 'size_m', size_col)

# Create new column for species
def extract_species(el):
    regex = '(\w{4,} )?\w{4,} shark'
    search = re.search(regex, el)
    if search != None:
        return search.group()
    else:
        return 'Unknown'

df['species'] = df['species'].apply(lambda x: extract_species(x))
df['species'] = df['species'].replace({'small' : '', 'foot' : ''})
df['species'] = df['species'].apply(lambda x: x.capitalize())

#%% Clean `time` column

# Replace fixed terms with times
# Source: https://www.britannica.com/dictionary/eb/qa/parts-of-the-day-early-morning-late-morning-etc
dtimes = {
        'Afternoon' : '15h00',
        'Morning' : '10h00',
        'Night' : '23h00',
        'Late afternoon': '17h00',
        'Evening' : '19h00',
        'Dusk' : '20h00',
        'Early morning' : '7h00',
        'Midday' : '12h00'
        }

df['time'] = df['time'].replace(dtimes)

# Transform time into `hour` column 
def extract_hour(el):
    regex = '(\d{2})h(\d{2})?'
    search = re.search(regex, el)
    if search != None:
        h = int(search.group(1))
        mins = search.group(2)
        if mins is not None: 
            mins = int(mins)
            if int(str(mins)[0]) > 2: # If past half hour
                h += 1
                if h >= 24: # Correct for day
                    h -= 24
                    
        return h
    
    else: # For wrong data
        return 99

## Fill NaNs with 'unknown' to apply function
df['time'] = df['time'].fillna('Unknown')
df['time'] = df['time'].apply(lambda x: extract_hour(x))
df.rename(columns = {'time' : 'hour'}, inplace = True)

#%% Drop other rows with NaN

df.dropna(inplace = True)

# Reset index
df.index = [i for i in range(0, len(df))]

#%% Fill rows without information from random rows with information

def generate_random_row(df, index = 0):
    """Generates a random row with information from the provided df."""
    row = df.sample()
    groups = [
        ['type'],
        ['country', 'area', 'location'],
        ['activity'],
        ['name', 'sex', 'age'],
        ['injury', 'fatal'],
        ['species', 'size_m']
        ]
    for g in groups:
        lst = df.sample()[g].iloc[0, :].tolist()
        row[g] = lst
    
    row = row.iloc[0, :]
    row.name = index
    
    return row

clean_full_df = df.copy()

def populate_random_rows(df, full_df):
    #for i in range(len(df), len(full_df)):
    for i in range(len(df), len(full_df)):
        print('Replacing row ' + str(i))
        df = df.append(generate_random_row(df, i))
    
    print('Done')
    
    return df

# Commented because it takes too much time
# clean_full_df = populate_random_rows(clean_full_df, full_df)

#%% Save .csv

clean_full_df.to_csv('../data/attacks_clean.csv')