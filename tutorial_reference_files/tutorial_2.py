# This tutorial is focused on learning the basics of pandas dataframe
# Link to youtube video tutorial: https://www.youtube.com/watch?v=vmEHCJofslg
import pandas as pd
import re

df = pd.read_csv('pokemon_data.csv')

# Print the first or last rows of the dataframe
# print(df.tail(3))
# print(df.tail(3))

# read headers
# print(df.columns)

# Read a specific column
# print(df[['Name', 'Type 2']][0:5])

# Read each row
# print(df.iloc[1:4])
# for index, row in df.iterrows():
#     print(index, row['Name'])

# Find only the rows with the filter requirement
# print(df.loc[df['Type 1'] == "Fire"])

# Read a specific location (Row, Column)
# print(df.iloc[2, 1])

# Describe data
# print(df.describe())

# Sorting value
# print(df.sort_values(['Type 1', 'HP'], ascending=[False, True]))

# Making changes to data
df['Total'] = df['HP'] + df['Attack'] + df['Defense'] + df['Sp. Atk'] + df['Sp. Def'] + df['Speed']

# Another way to add a column
df['Total'] = df.iloc[:, 4:10].sum(axis=1)

# Reposition column
cols = list(df.columns.values)
df = df[cols[0:4] + [cols[-1]] + cols[4:12]]

# Drop a column
# df = df.drop(columns=['Speed', 'Generation', 'Legendary', 'Type 1'])

# print(df.head(5))

# Create a new csv file
# df.to_csv('tutorial_reference_files/modified_pokemon_data.csv')

# Create excel file from data
# df.to_excel('tutorial_reference_files/modified_pokemon_data.xlsx', index=False)

# Create text file from data
# df.to_csv('tutorial_reference_files/modified_pokemon_data.txt', index=False, sep='\t')


# Advanced filtering data
new_df = df.loc[(df['Type 1'] == 'Grass') & (df['Type 2'] == 'Poison') & (df['HP'] > 70)]

# Reset index of new dataframe
new_df = new_df.reset_index(drop=True)
# print(new_df)

# filtering with cells that contain a specific substring
# print(df.loc[df['Name'].str.contains('Mega')])

# removing specific data
# print(df.loc[~df['Name'].str.contains('Mega')])

# Filtering using regular expressions
# print(df.loc[df['Type 1'].str.contains('fire|grass', flags=re.I, regex=True)])

# print(df.loc[df['Name'].str.contains('^pi[a-z]*', flags=re.I, regex=True)])


# Conditional changes
# df.loc[df['Type 1'] == 'Fire', 'Type 1'] = 'Flamer'

# df.loc[df['Type 1'] == 'Fire', 'Legendary'] = True
# print(df.loc[df['Legendary'] == True])

# df.loc[df['Total'] > 500, ['Generation', 'Legendary']] = ['TEST VALUE 1', 'test value 2']
# print(df.loc[df['Total'] > 500])

# Aggregate Statistics
# print(df.groupby(['Type 1']).mean().sort_values('HP', ascending=False))
# print(df.groupby(['Type 1']).sum())

# Guarantee absolute count numbers
# df['Count'] = 1

# print(df.groupby(['Type 1']).count().sort_values('#', ascending=False))
# print(df.groupby(['Type 1', 'Type 2']).count().sort_values('#', ascending=False)['Count'])

# Working with large amounts of data

new_df = pd.DataFrame(columns=df.columns)

for df in pd.read_csv('modified_pokemon_data.csv', chunksize=5):
    # print(df)
    results = df.groupby(['Type 1']).count()

    new_df = pd.concat([new_df, results])

    print(new_df)