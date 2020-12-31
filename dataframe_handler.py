import pandas as pd
import numpy as np

from general import load_quickfs_help_file


def web_scrape_to_dataframe(table_dict):
    # Create the dataframe with header
    df = pd.DataFrame(table_dict['data'], columns=table_dict['headers'])

    # Add label column to dataframe
    df['Category'] = table_dict['labels']
    df = df[['Category'] + [col for col in df.columns if col != 'Category']]

    # Remove blank rows and the Operating Expenses row from the dataframe
    df = df.loc[df['Category'] != '']

    # Change all numbers stored as text to float
    for column in df.columns[1:]:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Fill in blank cells with NaN
    df = df.fillna(value=np.nan)

    return df


def merge_fs_dataframes(df_dict):
    # This function merges the 4 types of financial statements web scraped from QuickFS
    help_file = load_quickfs_help_file()['Translation List']

    df_help = pd.DataFrame(help_file)

    processed_df_list = list()

    for key, df in df_dict.items():
        # Change the category column to index
        df = df.set_index('Category')

        # Create the Topic column
        df.insert(0, 'Topic', "")

        # Identify the indexes which only has NaN values
        nan_indexes = np.where(np.isnan(df[df.columns[1]]))[0]

        # enter the topics in the dataframe on the correct position, if there are any
        if len(nan_indexes) > 0:
            for idx in nan_indexes:
                topic_name = list(df.index)[idx]

                for iteration in range(idx, df.shape[0]):
                    df.iat[iteration, df.columns.get_loc('Topic')] = topic_name

                # For the NaN rows, remove the topic
                df.iat[idx, df.columns.get_loc('Topic')] = np.nan

        # Remove all rows that only contain NaN's
        df = df.dropna(axis=0, how='all')

        # # Create a 'TTM' column on the dataframes that don't have it
        if not 'TTM' in df.columns:
            df['TTM'] = 'NaN'

        # Include column with the financial statement type
        df.insert(0, 'Financial Statement', key)

        # Apply NaN to the blank cells
        df.replace(r'', r'NaN')

        # Create the Category column again and cleanse the index
        df.reset_index(level=0, inplace=True)

        # Match the the correct indexes to enter the API Parameter in the right spot
        df = df.merge(df_help, how='left', left_on=['Category', 'Topic', 'Financial Statement'],
                      right_on=['Category', 'Topic', 'Financial Statement'])

        # Change order of the API Parameter column in dataframe
        cols = list(df.columns.values)
        df = df[[cols[0]] + [cols[-1]] + cols[1:-1]]

        processed_df_list.append(df)

    # Concatenate all dataframes into one
    concat_df = pd.concat(processed_df_list)

    # Remove last row if ot isn't 'TTM'
    if concat_df.columns[-1] != 'TTM':
        concat_df = concat_df.drop(columns=[list(concat_df.columns.values)[-1]])

    return concat_df


def create_dataframe_from_api(fs_dict):
    # Create dataframe of quickfs help file (this file contains relevant translation and identification parameters)
    help_file = load_quickfs_help_file()
    df_help = pd.DataFrame(help_file["Translation List"])

    # Create year based header
    period_end_date_list = fs_dict['data']['financials']['annual']['period_end_date']
    annual_headers = [end_date.split('-')[0] for end_date in period_end_date_list]

    # Create annual dataframe
    df_annual = pd.DataFrame(fs_dict['data']['financials']['annual']).transpose()
    df_annual.columns = annual_headers

    # Change index column to normal column
    df_annual.insert(loc=0, column='API Parameter', value=df_annual.index)
    df_annual.reset_index(level=0, inplace=True)
    del df_annual['index']

    # Include new columns in annual dataframe from the help dataframe
    df = pd.merge(df_help, df_annual, on='API Parameter')

    # Remove duplicate rows
    df = df.drop_duplicates(subset=['API Parameter'])

    return df
