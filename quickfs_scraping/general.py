import json
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import *
import pymsgbox
import shutil
import pathlib


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


def load_quickfs_help_file():
    project_root_directory = os.path.split(os.environ['VIRTUAL_ENV'])[0]
    quickfs_help_file = os.path.join(project_root_directory, 'quickfs_data', 'quickfs_helpfile.json')
    with open(quickfs_help_file, 'r') as file:
        help_file = json.load(file)

    return help_file


def get_quickfs_key(source="API"):
    project_root_directory = os.path.split(os.environ['VIRTUAL_ENV'])[0]
    quickfs_key_file = os.path.join(project_root_directory, 'quickfs_data', 'quickfs_keys.json')
    with open(quickfs_key_file, 'r') as file:
        key_file = json.load(file)

    if source == 'Web Scraping':
        return key_file['web_scraping_key']
    else:
        return key_file['api_key']


def is_file_available(file_path):
    try:
        file_path_name = os.path.splitext(file_path)[0]
        file_path_ext = os.path.splitext(file_path)[1]
        temp_name = file_path_name + "_temp" + file_path_ext

        os.rename(file_path, temp_name)
        os.rename(temp_name, file_path)
    except OSError:
        pymsgbox.alert(f"File: '{file_path}' is being used by another process. Please close it before continuing",
                       "File not available")
        exit()


def check_validity_output_file(output_file_path):
    # Check if file exists
    if os.path.exists(output_file_path):
        # Check if file is being used by another process
        is_file_available(output_file_path)

        # Check in which date it has been created
        creation_date = datetime.fromtimestamp(os.path.getctime(output_file_path)).date()
        current_date = datetime.now().date()
        one_month = relativedelta(months=1)

        # Replace and rename old output file if its creation date is at least one month older that today
        if creation_date + one_month < current_date:
            new_dir_name = os.path.join(os.path.dirname(output_file_path), 'old')
            base_name = os.path.splitext(os.path.basename(output_file_path))[0]
            base_name_ext = os.path.splitext(os.path.basename(output_file_path))[1]
            new_base_name = base_name + '_' + str(creation_date) + base_name_ext

            new_json_file_path = os.path.join(new_dir_name, new_base_name)

            # Replacing and renaming
            try:
                shutil.move(output_file_path, new_json_file_path)
            except PermissionError:
                pymsgbox.alert(f"The old excel file couldn't be replaced. Output file path: {output_file_path}.",
                               'Error')
                exit()

            # A new output file will need to be generated, so the check validity is false
            return False

        else:
            # The current output file in the directory is still good for usage
            return True

    else:
        return False


def save_json_request_to_file(json_file, json_file_path):
    with open(json_file_path, 'w') as file:
        json.dump(json_file, file, indent=4, sort_keys=True)


def gen_compatible_api_dict(data_dict):
    # This function parses the current data dictionary into the same format style as a API full data dictionary
    data_file = {'data': {'financials': {'annual': {}}}}
    for key, value in data_dict.items():
        data_file['data']['financials']['annual'][key] = value

    return data_file


def remove_non_existent_data_from_dict(data_dict):
    # This function removes zero entries in data_dict if they exist. This is possible because maybe the company
    # doesn't has stock data for a certain period

    # Create dataframe for easier parsing
    df = pd.DataFrame(data_dict['data']['financials']['annual'])

    # Delete rows where the period_end_date value is zero
    df = df[df['period_end_date'] != 0]

    # Change dataframe back to dictionary
    data_dict = df.to_dict('list')
    data_dict = gen_compatible_api_dict(data_dict)

    return data_dict


def get_sheet_name(bool_scraping=True, scraping_method=None):
    if scraping_method == 'Web Scraping' and bool_scraping:
        return 'financial_statement_scraped'
    elif scraping_method == 'API' and bool_scraping:
        return 'financial_statement_api'
    else:
        return 'rule1_results'
