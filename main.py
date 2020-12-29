import json
import os
import pymsgbox

from general import check_validity_output_file, excel_to_dataframe, create_fs_excel_file, save_json_request_to_file
from web_scraping import links_constructor, scrape_tables
from api_scraping import get_api_request, create_fs_tables_from_api
from filter_fs_data import get_rule_number1_ratios


def gen_financial_data_frame(ticker):
    # Financial Table Types that will be scraped
    table_names = ['income statement', 'balance sheet', 'cash flow', 'key ratios']

    # Let user choose the solution for getting the data: Either scraping or using API
    user_answer = pymsgbox.confirm(f'What method do you want to use to get the financial data from {ticker}?',
                                   'Select Option', buttons=['API', 'Scraping'])

    # Output folders
    excel_output_folder = os.path.join('financial_files', 'excel')
    json_output_folder = os.path.join('financial_files', 'json')
    excel_output_path = os.path.join(excel_output_folder, ticker + '.xlsx')
    json_output_path = os.path.join(json_output_folder, ticker + '.json')

    if user_answer == 'Scraping':
        pymsgbox.alert("Be aware that this option my not work due to possible scraping restrictions from website.")

        if not check_validity_output_file(excel_output_path):
            links = links_constructor(ticker, table_names)
            df_dict = scrape_tables(links)
            create_fs_excel_file(excel_output_path, df_dict, ticker)
        else:
            df_dict = excel_to_dataframe(excel_output_path, table_names)

        data_source = 'scraping'

    else:
        # pymsgbox.alert(
        #     "Be aware that there is a limited amount of requests that can be made per day using this option.")

        if not check_validity_output_file(json_output_path):
            json_file = get_api_request(ticker)
            save_json_request_to_file(json_file, json_output_path)

        else:
            with open(json_output_path, 'r') as file:
                json_file = json.load(file)

        df_dict = create_fs_tables_from_api(json_file, table_names)
        data_source = 'api'

    # *****************TEST TERRITORY**********************************************************

    get_rule_number1_ratios(df_dict, data_source)

    # *****************************************************************************************


if __name__ == '__main__':
    list_with_tickers_from_watchlist = ['STX', 'CRSR', 'LOGI', 'GOOGL', 'NVDA', 'CSCO', 'QCOM', 'ATVI',
                                        'EBAY', 'EA', 'RYAAY', 'SSNGY', 'GPRO', 'CSIOY', 'PINS', 'SPOT', 'ANSS', 'BA',
                                        'RYCEF', 'EADSF', 'ERJ', 'BDRAF', 'HXL', 'MELI', 'LTMAQ', 'DAL', 'ESYJY',
                                        'CPCAY', 'AFLYY', 'AZUL', 'DLAKY']

    gen_financial_data_frame('DASTY')
