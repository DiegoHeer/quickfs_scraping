import json
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import *
import pymsgbox
import shutil
import openpyxl
from pandas import ExcelWriter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import colors, Font


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
    quickfs_help_file = 'quickfs_helpfile.json'
    with open(quickfs_help_file, 'r') as file:
        help_file = json.load(file)

    return help_file


def check_validity_output_file(output_file_path):
    # Check if file exists
    if os.path.exists(output_file_path):
        # Check in which date it has been created
        creation_date = datetime.fromtimestamp(os.path.getctime(output_file_path)).date()
        current_date = datetime.now().date()
        one_month = relativedelta(months=1)

        # Replace and rename old output file if its creation date is at least one month older that today
        if creation_date + one_month < current_date:
            new_dir_name = os.path.join(os.path.dirname(output_file_path), 'old')
            base_name = os.path.splitext(os.path.basename(output_file_path))[0] + '_' + str(creation_date) + \
                        os.path.splitext(os.path.basename(output_file_path))[1]

            new_json_file_path = os.path.join(new_dir_name, base_name)

            # Replacing and renaming
            shutil.move(output_file_path, new_json_file_path)

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


def excel_to_dataframe(excel_output_path):
    excel_file = pd.ExcelFile(excel_output_path, engine='openpyxl')

    return pd.read_excel(excel_file, sheet_name='financial_data')


def create_fs_excel_file(excel_output_path, df, ticker):
    # Check if file already exists, if yes, delete
    if os.path.exists(excel_output_path):
        # Check if the file is not open in another process
        try:
            os.remove(excel_output_path)
        except PermissionError:
            pymsgbox.alert("The excel file couldn't be generated because it is open in another process.", 'Error')
            exit()

    # Write the dataframes into an excel file
    writer = ExcelWriter(excel_output_path)
    sheet_name = 'financial_data'
    df.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)
    writer.save()

    # Convert data in excel file to table format
    wb = openpyxl.load_workbook(filename=excel_output_path)

    # Create table
    tab = Table(displayName="financial_data", ref=f'A1:{chr(len(df.columns) + 64)}{len(df) + 1}')

    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    tab.tableStyleInfo = style

    # Change header font color
    # ws = wb[sheet_name]
    # header_col = ws.row_dimensions[1]
    # header_col.font = Font(color=colors.WHITE)

    # Add table to sheet and save workbook
    wb[sheet_name].add_table(tab)
    wb.save(excel_output_path)

    # Success message
    pymsgbox.confirm(f'The financial excel file for {ticker} has been successfully generated.', 'Success!',
                     buttons=['OK'])


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
