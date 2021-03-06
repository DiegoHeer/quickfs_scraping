from bs4 import BeautifulSoup
import pymsgbox

from quickfs_scraping.dataframe_handler import web_scrape_to_dataframe, merge_fs_dataframes
from quickfs_scraping.general import check_request_status, get_quickfs_key
from quickfs_scraping.proxy_rotation import fetch


def links_constructor(ticker):
    base_url = r"https://api.quickfs.net/stocks/"
    api_key = get_quickfs_key("Web Scraping")

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


def scrape_yahoo_analyst_growth_rate(ticker):
    base_url = f"https://finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"

    soup = get_scraping_request(base_url, site='yahoo-finance')

    try:
        growth_rate_5_years_row = soup.body.find('td', text='Next 5 Years (per annum)').parent
        growth_rate_1_year_row = soup.body.find('td', text='Next Year').parent
        growth_rate_5_years = growth_rate_5_years_row.find_all('td')[1].text
        growth_rate_1_year = growth_rate_1_year_row.find_all('td')[1].text
    except AttributeError:
        return 0

    if growth_rate_5_years != 'N/A':
        return float(growth_rate_5_years.replace('%', '')) / 100
    elif growth_rate_1_year != 'N/A':
        return float(growth_rate_1_year.replace('%', '')) / 100
    else:
        return 0
