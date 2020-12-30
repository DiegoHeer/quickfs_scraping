import requests
import pandas as pd
import pymsgbox

from general import check_request_status, load_quickfs_help_file, gen_compatible_api_dict, \
    remove_non_existent_data_from_dict


def get_api_request(ticker, bool_batch_execution=False):
    # Request data from API
    # Be aware! There is a limit for requests per day
    api_key = "0cb07ade55259176dd3ecc9cc11a16f118877d8c"
    link_all_data = f"https://public-api.quickfs.net/v1/data/all-data/{ticker}?api_key={api_key}"

    if not bool_batch_execution:
        user_answer = pymsgbox.confirm(
            f"Click on 'OK' if you only want to request the essential data for {ticker}. "
            f"Clicking on 'Cancel' will request all financial data. "
            f"Be aware that the second option will consume almost half the daily api quota!")
    else:
        user_answer = 'OK'

    if user_answer == 'OK':
        # Create a storage dictionary
        data_dict = dict()

        # Request the time frame
        time_metric = 'period_end_date'
        link = f"https://public-api.quickfs.net/v1/data/{ticker}/{time_metric}?period=FY-19:FY&api_key={api_key}"
        req = requests.get(link)
        check_request_status(req)
        data_dict[time_metric] = req.json().pop('data')

        # Get the relevant metric data
        help_file = load_quickfs_help_file()
        relevant_parameters_list = help_file['Relevant Parameters']
        for parameter_dict in relevant_parameters_list:
            # Get the api parameter(metric)
            api_parameter = parameter_dict['API Parameter']

            # Create link and get data
            link = f"https://public-api.quickfs.net/v1/data/{ticker}/{api_parameter}?period=FY-19:FY&api_key={api_key}"
            req = requests.get(link)
            check_request_status(req)
            data_dict[api_parameter] = req.json().pop('data')

        # Convert the data dictionary into a compatible dictionary that can be used by the rest of the code
        data_file = gen_compatible_api_dict(data_dict)

    else:
        # link_selected_data
        req = requests.get(link_all_data)

        # Check request status before continuing
        check_request_status(req)

        # Change request response to json
        data_file = req.json()

    # Check if json file is valid
    data_file = remove_non_existent_data_from_dict(data_file)

    return data_file


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
