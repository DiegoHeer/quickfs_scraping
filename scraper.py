import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import pymsgbox
from pandas import ExcelWriter


def links_constructor(ticker):
    base_url = r"https://api.quickfs.net/stocks/"
    api_key = r"grL0gNYoMoLUB1ZoAKLfhXkoMoLODiO1WoL9" \
              r".grLtk3PoMoLmqFEsMasbNK9fkXudkNBtR2jpkr5dINZoAKLtRNZoMlG2PQx5WixrPJRcOpEfqXGoMwcoqNWaka9tIKO6OlG1MQ" \
              r"k0OosoIS1fySsoMoLuySBwh2tbhpV0yXVdyXBakuHwhSVthK5lh20oAKLsRNWiq29rIKO6OaWIJQufWG1Vq1RrZuWSIKOcOwHry" \
              r"NIthXBwICO6PKsokpBwyS9dDFLtqoO6grLBDrO6PCsoZ0GoMlH9vN0.o51zrquUvS_VCyK9uIgYM4RLZP4gu2VairnipVf8mEG"

    # There are 5 types of tables that will be extracted: overview, income statement, balance sheet, cash flow and
    # key ratios
    table_types = ['ovr', 'is', 'bs', 'cf', 'ratios']
    table_names = ['overview', 'income statement', 'balance sheet', 'cash flow', 'key ratios']

    # The timeframe used will be annual
    timeframe = '/Annual/'

    # Construct the links
    url_links = {}
    for iteration, table_type in enumerate(table_types):
        link = base_url + ticker.upper() + "/" + table_type + timeframe + api_key
        url_links[table_names[iteration]] = link

    return url_links


def get_request(link):
    # Request data from link
    req = requests.get(link)

    if req.json()['errors'] == 'Unknown Symbol':
        pymsgbox.alert("The ticker entered is invalid. Please enter a new one.")
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


def create_dataframe(table_dict):
    # Create the dataframe with header
    df = pd.DataFrame(table_dict['data'], columns=table_dict['headers'])

    # Add label column to dataframe
    df['Category'] = table_dict['labels']
    df = df[['Category'] + [col for col in df.columns if col != 'Category']]

    # Remove blank rows and the Operating Expenses row from the dataframe
    df = df.loc[df['Category'] != '']

    # Fill in blank cells with NaN
    df = df.fillna(value='NaN')

    return df


def scrape_tables(url_links):
    dataframe_dict = {}
    # Scrape the table data for each link and create a dataframe from it
    for key, link in url_links.items():
        fs_table = scrape_fs_tables(get_request(link))
        df = create_dataframe(fs_table)
        dataframe_dict[key] = df

    return dataframe_dict


def gen_financial_excel_file(ticker):
    links = links_constructor(ticker)
    df_dict = scrape_tables(links)

    # Write all the dataframes to separate sheets in a specific excel file
    output_folder = 'financial_files/'
    output_path = output_folder + ticker + '.xlsx'

    # Check if file already exists, if yes, delete
    if os.path.exists(output_path):
        # Check if the file is not open in another process
        try:
            os.remove(output_path)
        except PermissionError:
            pymsgbox.alert("The excel file couldn't be generated because it is open in another process.", 'Error')
            exit()

    # Write the dataframes into an excel file
    writer = ExcelWriter(output_path)
    for key in df_dict:
        df_dict[key].to_excel(excel_writer=writer, sheet_name=key, index=False)

    # Save the excel file
    writer.save()
    pymsgbox.confirm(f'The financial excel file for {ticker} has been successfully generated.', 'Success!',
                     buttons=['OK'])


if __name__ == '__main__':
    gen_financial_excel_file('ARRY')
