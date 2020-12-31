import pandas as pd
import os
import pymsgbox
import openpyxl
from pandas import ExcelWriter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import colors, Font


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
