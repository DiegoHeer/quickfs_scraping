from bs4 import BeautifulSoup
import pandas as pd
import pymsgbox
import numpy as np

from general import check_request_status, load_quickfs_help_file
from proxy_rotation import fetch


def links_constructor(ticker):
    base_url = r"https://api.quickfs.net/stocks/"
    api_key = r"grL0gNYoMoLUB1ZoAKLfhXkoMoLODiO1WoL9.grLtk3PoMoLmqFEsMasbNK9fkXudkNBtR2jpkr5dINZoAKLtRNZoMl" \
              r"G2PQuiWQknWJOcOpEfqXGoMwcoqNWaka9tIKO6OlG1MQk0OosoIS1fySsoMoLuySBwh2tbhpV0yXVdyXBakuHwhSVthK" \
              r"5lh20oAKLsRNWiq29rIKO6OaWIJQufWG1Vq1RrZuWSIKOcOwHryNIthXBwICO6PKsokpBwyS9dDFLtqoO6grLBDrO6PCs" \
              r"oZ0GoMlH9vN0.sbxSI5du4jS2FlR0-qktBT62siUOb1_YMMWYs3GDYou"

    # There are 5 types of tables that will be extracted: overview, income statement, balance sheet, cash flow and
    # key ratios
    table_names = ['income statement', 'balance sheet', 'cash flow', 'key ratios']
    table_types = ['is', 'bs', 'cf', 'ratios']

    # The timeframe used will be annual
    timeframe = '/Annual/'

    # Construct the links
    url_links = {}
    for iteration, table_type in enumerate(table_types):
        link = base_url + ticker.upper() + "/" + table_type + timeframe + api_key
        url_links[table_names[iteration]] = link

    return url_links


def get_scraping_request(link, site='quickfs'):
    # Fetch request using a proxy rotation method
    req = fetch(link)

    # check request status
    check_request_status(req)

    # Identify if ticker entered is valid
    if site == 'quickfs':
        if req.json()['errors'] == 'Unknown Symbol':
            pymsgbox.alert(f"The ticker entered is invalid. Please enter a new one. Link: {link}")
            exit()

    # Create a soup object from the request
    soup = BeautifulSoup(req.content, features='lxml')

    return soup


def scrape_fs_tables(soup):
    # Create dictionary to put data from table in
    table_dict = {'headers': [], 'labels': [], 'data': []}

    # get all data from table
    fs_table = soup.find('table', class_='fs-table')
    for index, row in enumerate(fs_table.find_all('tr')):
        # Get all columns
        cols = row.find_all('td')

        # First row is the header
        if index == 0:
            headers = [element.text.strip() for element in cols]
            # The first element from the headers list is removed because it is blank
            table_dict['headers'] = headers[1:]

        # First element in the row is the label
        label = cols[0].text.strip()
        table_dict['labels'].append(label)

        # Rest of the elements of the row are data
        data = [element.get('data-value') for element in cols[1:]]
        table_dict['data'].append(data)

    return table_dict


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


def scrape_tables(url_links):
    dataframe_dict = {}
    # Scrape the table data for each link and create a dataframe from it
    for key, link in url_links.items():
        fs_table = scrape_fs_tables(get_scraping_request(link))
        df = web_scrape_to_dataframe(fs_table)
        dataframe_dict[key] = df

    # Merge the dataframes to a single one
    merged_df = merge_fs_dataframes(dataframe_dict)

    return merged_df


def merge_fs_dataframes(df_dict):
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


def scrape_yahoo_analyst_growth_rate(ticker):
    base_url = f"https://finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"

    soup = get_scraping_request(base_url, site='yahoo-finance')

    analyst_growth_rate = soup.find('td', attrs={"data-reactid": "427"}).text
    analyst_growth_rate = float(analyst_growth_rate.replace('%', '')) / 100

    return analyst_growth_rate
