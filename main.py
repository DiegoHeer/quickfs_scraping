import json
import os
import pathlib
import pymsgbox

from excel_handler import excel_to_dataframe, create_fs_excel_file
from dataframe_handler import create_dataframe_from_api
from general import check_validity_output_file, save_json_request_to_file
from web_scraping import links_constructor, scrape_tables
from api_scraping import get_api_request
from filter_fs_data import get_rule_number1_ratios

# This project focus on scraping financial data from the quickfs.com website and process it to Rule #1 output data
# Other sites that can be used for scraping are:
# https://www.rocketfinancial.com/


def gen_financial_data_frame(ticker):
    # Financial Table Types that will be scraped

    # Let user choose the solution for getting the data: Either scraping or using API
    user_answer = pymsgbox.confirm(f'What method do you want to use to get the financial data from {ticker}?',
                                   'Select Option', buttons=['API', 'Scraping'])

    # Output folders
    work_directory = pathlib.Path(__file__).parent.absolute()
    excel_output_folder = os.path.join(work_directory, 'financial_files', 'excel')
    json_output_folder = os.path.join(work_directory, 'financial_files', 'json')
    excel_output_path = os.path.join(excel_output_folder, ticker + '.xlsx')
    json_output_path = os.path.join(json_output_folder, ticker + '.json')

    if user_answer == 'Scraping':
        pymsgbox.alert("Be aware that this option my not work due to possible scraping restrictions from website.")

        if not check_validity_output_file(excel_output_path):
            links = links_constructor(ticker)
            df_fs = scrape_tables(links)
            create_fs_excel_file(excel_output_path, df_fs, ticker)
        else:
            df_fs = excel_to_dataframe(excel_output_path)

    else:
        if not check_validity_output_file(json_output_path):
            json_file = get_api_request(ticker)
            save_json_request_to_file(json_file, json_output_path)
        else:
            with open(json_output_path, 'r') as file:
                json_file = json.load(file)

        df_fs = create_dataframe_from_api(json_file)

    # *****************TEST TERRITORY**********************************************************

    get_rule_number1_ratios(df_fs, ticker)

    # *****************************************************************************************


if __name__ == '__main__':
    list_with_tickers_from_watchlist = ['STX', 'CRSR', 'LOGI', 'GOOGL', 'NVDA', 'CSCO', 'QCOM', 'ATVI',
                                        'EBAY', 'EA', 'RYAAY', 'SSNGY', 'GPRO', 'CSIOY', 'PINS', 'SPOT', 'ANSS', 'BA',
                                        'RYCEF', 'EADSF', 'ERJ', 'BDRAF', 'HXL', 'MELI', 'LTMAQ', 'DAL', 'ESYJY',
                                        'CPCAY', 'AFLYY', 'AZUL', 'DLAKY']

    gen_financial_data_frame('QCOM')
