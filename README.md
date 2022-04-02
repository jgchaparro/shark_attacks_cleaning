# Cleaning 'shark attack' database

The goal of this project is to tidy as much as possible the [Shark Attack database](https://www.kaggle.com/datasets/teajay/global-shark-attacks) with two additional constrains:

1) Not deleting any columns
2) Final dataframe must contain over 20k rows

This project is part of the Ironhack Madrid's Data Analytics bootcamp training programme.

## Steps

### First look at the data

To start with, I inspect the data to detect NaNs and other anomalies. To do so, I graph a plot which colours NaNs and access the `full_df` variable through Spyder's Variable Explorer. A first inspection shows that around 75 % of the rows are composed uniquely or mostly out of NaNs, so it might be worth focusing on the 25 % with unclean data, which we will call `df`. Within this subset, a significant part of the data has some kind of problem (incorrect format or missing data). The next step is to tackle this subset column by column. 

### Cleaning column names

Underscores and periods are removed from the column names and capital letters are lowered. Besides, some column names are simplified. For instance, `investigator_or_source` becomes `source`.

### Unnamed columns

Our instructor told us not to delete them, but there is nothing preventing us to just fill them with whatever we feel like. And so we do.

### `fatal` column

First, I replace 'Y' and 'N' to booleans. Then, if the injury description points that the attack was fatal, the corresponding cell is changes to `True`. Otherwise, we assume that the attack was not fatal: it is likely that if that was the case, there was some indication of the fatality.

### `sex` column

I inspect the `names` column to check if it has some information about the sex. If so, the correspondent `sex` cell is updated. If there is no information, 'U' (for 'unknown') is udes.

### `age` column

I filter the `age` column using a regex to extract valid digit combinations and filter the rest. I plot the valid ages and conclude that they have a somewhat skewed distribution, so I use the median to fill the invalid cells.

### `name` column

I remove 'male' and 'female' from the columns as the information is being already contained in the `sex` column

### `activity`, `injury`, `country`, `area` and `location` columns
As there is no way to systematically find information for these columns, I opted for filling NaNs with 'Unknown'. As exceptions, I manually added information for two rows as the `location` column gives information about the country the event took place.

### `species` column

This column has a mix of information between the species and the size of the shark in meters and feet. First, I extracted the size through a regex, distinguished between different measurements and converted them to meters. All this information went to the new `size_m` column. A second regex extracted the species of the shark and rewrote the old `species` column. If no information was found, the cell was filled with 'Unknown'.

### `time` column

A significant portion of the `time` cells contains short and vague descriptions of the time of the event, such as 'Afternoon' or 'Morning'. To avoid losing too much data, I converted the strings to a fixed hour so that they could be treated as integers. The time included hours and minutes, so I rounded them to the nearest hour. If no information was provided, `hour` was set to 99 so that the column type can be `int`.

### Other columns

Some other columns still contained NaNs. Given that its number was sufficiently small (< 100), I dropped them and reset the index.

### End step: filling in the remaining rows

Given that the final data frmae must contain over 20k rows, dropping them was not an option. Instead, I wrote a function that generates random rows based on pieces of information from previously cleaned rows. Those were appended to the subset dataframe `df` to form `clean_full_df`. Finally, `clean_full_df` is exported to a .csv file.