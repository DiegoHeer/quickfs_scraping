import json

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import *
import pymsgbox
import shutil
from pandas import ExcelWriter
from filter_fs_data import get_rule_number1_ratios


def links_constructor(ticker, table_names):
    base_url = r"https://api.quickfs.net/stocks/"
    api_key = r"grL0gNYoMoLUB1ZoAKLfhXkoMoLODiO1WoL9" \
              r".grLtk3PoMoLmqFEsMasbNK9fkXudkNBtR2jpkr5dINZoAKLtRNZoMlG2PQx5WixrPJRcOpEfqXGoMwcoqNWaka9tIKO6OlG1MQ" \
              r"k0OosoIS1fySsoMoLuySBwh2tbhpV0yXVdyXBakuHwhSVthK5lh20oAKLsRNWiq29rIKO6OaWIJQufWG1Vq1RrZuWSIKOcOwHry" \
              r"NIthXBwICO6PKsokpBwyS9dDFLtqoO6grLBDrO6PCsoZ0GoMlH9vN0.o51zrquUvS_VCyK9uIgYM4RLZP4gu2VairnipVf8mEG"

    # There are 5 types of tables that will be extracted: overview, income statement, balance sheet, cash flow and
    # key ratios
    table_types = ['is', 'bs', 'cf', 'ratios']

    # The timeframe used will be annual
    timeframe = '/Annual/'

    # Construct the links
    url_links = {}
    for iteration, table_type in enumerate(table_types):
        link = base_url + ticker.upper() + "/" + table_type + timeframe + api_key
        url_links[table_names[iteration]] = link

    return url_links


def check_request_status(req):
    # Check if response of request is good
    if req.status_code != 200:
        if req.status_code == 207:
            user_answer = pymsgbox.confirm(f"The request was only partially successful. Status code: {req.status_code}."
                                           f"To continue press 'OK'", title="Alert")
            if user_answer == 'Cancel':
                exit()

        elif req.status_code == 401:
            pymsgbox.alert(
                f"The request requires an authentication. Please check the API key Status code: {req.status_code}.",
                title="Error")
            exit()

        elif req.status_code == 403:
            pymsgbox.alert(f"The request was denied. Access is restricted. Status code: {req.status_code}",
                           title="Error")
            exit()

        elif req.status_code == 413:
            pymsgbox.alert(f"Request is too large. Please consider reducing it. Status code: {req.status_code}",
                           title="Error")
            exit()

        elif req.status_code == 429:
            pymsgbox.alert(
                f"Maximum limit of requests is exceeded. Please continue tomorrow. Status code: {req.status_code}",
                title="Error")
            exit()


def get_api_request(ticker):
    # Request data from API
    # Be aware! There is a limit for requests per day
    api_key = "0cb07ade55259176dd3ecc9cc11a16f118877d8c"
    link = f"https://public-api.quickfs.net/v1/data/all-data/{ticker}?api_key={api_key}"
    req = requests.get(link)

    # Check request status before continuing
    check_request_status(req)

    json_file = req.json()

    # Check if json file is valid
    # TODO: include a check method to verify if json file is valid

    return json_file


def get_scraping_request(link):
    # Request data from link
    req = requests.get(link)

    # check request status
    check_request_status(req)

    # Identify if ticker entered is valid
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


def load_quickfs_help_file():
    quickfs_help_file = 'quickfs_helpfile.json'
    with open(quickfs_help_file, 'r') as file:
        help_file = json.load(file)

    return help_file


def create_fs_tables_from_api(fs_dict, table_names):
    # Create dataframe of quickfs help file (this file contains relevant translation and identification parameters)
    help_file = load_quickfs_help_file()
    df_help = pd.DataFrame(help_file)

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
    df_annual = pd.merge(df_help, df_annual, on='API Parameter')

    # Obtain the TTM column using the quarterly dataframe
    df_quarterly = pd.DataFrame(fs_dict['data']['financials']['quarterly']).transpose()
    quarterly_header = df_quarterly.iloc[0].values.flatten().tolist()
    df_quarterly = df_quarterly[1:]
    df_quarterly.columns = quarterly_header

    # Change index column to normal column
    df_quarterly.insert(loc=0, column='API Parameter', value=df_quarterly.index)
    df_quarterly.reset_index(level=0, inplace=True)
    del df_quarterly['index']

    # Remove unnecessary data from quarterly dataframe, leaving only the API Parameter and TTM date
    df_quarterly = df_quarterly[['API Parameter', df_quarterly.columns[-1]]]

    # Change last column name to 'TTM'
    df_quarterly = df_quarterly.rename(columns={df_quarterly.columns[-1]: 'TTM'})

    # Merge TTM dataframe with annual dataframe
    df_merged = pd.merge(df_annual, df_quarterly, on='API Parameter')

    # Create the dataframes for each financial table
    df_dict = dict()
    for fs_name in table_names:
        df_dict[fs_name] = df_merged.loc[df_merged['Financial Statement'] == fs_name.title()]

    return df_dict


def create_dataframe(table_dict):
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
    df = df.fillna(value='NaN')

    return df


def scrape_tables(url_links):
    dataframe_dict = {}
    # Scrape the table data for each link and create a dataframe from it
    for key, link in url_links.items():
        fs_table = scrape_fs_tables(get_scraping_request(link))
        df = create_dataframe(fs_table)
        dataframe_dict[key] = df

    return dataframe_dict


def check_validity_json_file(json_file_path):
    # Check if file exists
    if os.path.exists(json_file_path):
        # Check in which date it has been created
        creation_date = datetime.fromtimestamp(os.path.getctime(json_file_path)).date()
        current_date = datetime.now().date()
        one_month = relativedelta(months=1)

        # Replace and rename old json file if its creation date is at least one month older that today
        if creation_date + one_month < current_date:
            new_dir_name = os.path.join(os.path.dirname(json_file_path), 'old')
            base_name = os.path.splitext(os.path.basename(json_file_path))[0] + '_' + str(creation_date) + \
                        os.path.splitext(os.path.basename(json_file_path))[1]

            new_json_file_path = os.path.join(new_dir_name, base_name)

            # Replacing and renaming
            shutil.move(json_file_path, new_json_file_path)

            # A new json file will need to be generated, so the check validity is false
            return False

        else:
            # The current json file in the directory is still good for usage
            return True

    else:
        return False


def save_json_request_to_file(json_file, json_file_path):
    with open(json_file_path, 'w') as file:
        json.dump(json_file, file)


def gen_financial_excel_file(ticker):
    # Financial Table Types that will be scraped
    table_names = ['income statement', 'balance sheet', 'cash flow', 'key ratios']

    # Let user choose the solution for getting the data: Either scraping or using API
    user_answer = pymsgbox.confirm(f'What method do you want to use to get the financial data from {ticker}?',
                                   'Select Option', buttons=['API', 'Scraping'])
    if user_answer == 'Scraping':
        pymsgbox.alert("Be aware that this option my not work due to possible scraping restrictions from website.")

        links = links_constructor(ticker, table_names)
        df_dict = scrape_tables(links)
        data_source = 'scraping'

    else:
        pymsgbox.alert(
            "Be aware that there is a limited amount of requests that can be made per day using this option.")

        # Check if there is already an json file available from this month. If not, request a new one
        json_file_path = rf'financial_files\json\{ticker}.json'

        if not check_validity_json_file(json_file_path):
            json_file = get_api_request(ticker)
            save_json_request_to_file(json_file, json_file_path)

        else:
            with open(json_file_path, 'r') as file:
                json_file = json.load(file)

        df_dict = create_fs_tables_from_api(json_file, table_names)
        data_source = 'api'

    # *****************TEST TERRITORY**********************************************************

    get_rule_number1_ratios(df_dict, data_source)

    # *****************************************************************************************

    # Write all the dataframes to separate sheets in a specific excel file
    output_folder = os.path.join('financial_files', 'excel')
    output_path = os.path.join(output_folder, ticker + '.xlsx')

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
    # pymsgbox.confirm(f'The financial excel file for {ticker} has been successfully generated.', 'Success!',
    #                  buttons=['OK'])


if __name__ == '__main__':
    list_with_tickers_from_watchlist = ['STX', 'CRSR', 'LOGI', 'GOOGL', 'NVDA', 'CSCO', 'QCOM', 'ATVI',
                                        'EBAY', 'EA', 'RYAAY', 'SSNGY', 'GPRO', 'CSIOY', 'PINS', 'SPOT', 'ANSS', 'BA',
                                        'RYCEF', 'EADSF', 'ERJ', 'BDRAF', 'HXL', 'MELI', 'LTMAQ', 'DAL', 'ESYJY',
                                        'CPCAY', 'AFLYY', 'AZUL', 'DLAKY']

    gen_financial_excel_file('DAL')
