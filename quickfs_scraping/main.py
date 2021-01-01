import json
import os
import pathlib
import pymsgbox

from quickfs_scraping.excel_handler import excel_to_dataframe, dataframe_to_excel, excel_sheet_exists
from quickfs_scraping.dataframe_handler import create_dataframe_from_api
from quickfs_scraping.general import check_validity_output_file, save_json_request_to_file
from quickfs_scraping.web_scraping import links_constructor, scrape_tables
from quickfs_scraping.api_scraping import get_api_request
from quickfs_scraping.filter_fs_data import get_rule_number1_ratios


# This project focus on scraping financial data from the quickfs.com website and process it to Rule #1 output data
# Other sites that can be used for scraping are:
# https://www.rocketfinancial.com/


def app(ticker, bool_batch=False):
    # Let user choose the solution for getting the data: Either scraping or using API
    if not bool_batch:
        scraping_method = pymsgbox.confirm(f'What method do you want to use to get the financial data from {ticker}?',
                                           'Select Option', buttons=['API', 'Web Scraping'])
    else:
        scraping_method = 'API'

    # Output folders
    work_directory = pathlib.Path(__file__).parent.absolute()
    excel_output_folder = os.path.join(work_directory, '../financial_files', 'excel')
    json_output_folder = os.path.join(work_directory, '../financial_files', 'json')
    excel_output_path = os.path.join(excel_output_folder, ticker + '.xlsx')
    json_output_path = os.path.join(json_output_folder, ticker + '.json')

    if scraping_method == 'Web Scraping':
        pymsgbox.alert("Be aware that this option my not work due to possible scraping restrictions from website.")

        if not check_validity_output_file(excel_output_path) \
                or not excel_sheet_exists(excel_output_path, source=scraping_method):
            links = links_constructor(ticker)
            df_fs = scrape_tables(links)
        else:
            df_fs = excel_to_dataframe(excel_output_path, source=scraping_method)

    else:
        if not check_validity_output_file(json_output_path) \
                or not excel_sheet_exists(excel_output_path, source=scraping_method):
            json_file = get_api_request(ticker, bool_batch=bool_batch)
            save_json_request_to_file(json_file, json_output_path)
        else:
            with open(json_output_path, 'r') as file:
                json_file = json.load(file)

        df_fs = create_dataframe_from_api(json_file)

    # Get all the calculated ratios and relevant stock data
    results_df = get_rule_number1_ratios(df_fs, ticker)

    # Output all the financial data into an excel file
    dataframe_to_excel(excel_output_path, df_fs, ticker, source=scraping_method, bool_batch=True)

    # Output all the Rule #1 results into the excel file
    dataframe_to_excel(excel_output_path, results_df, ticker, source='filter_fs_data', bool_batch=bool_batch)


if __name__ == '__main__':
    app('EA')
