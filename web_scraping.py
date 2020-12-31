from bs4 import BeautifulSoup
import pymsgbox

from dataframe_handler import web_scrape_to_dataframe, merge_fs_dataframes
from general import check_request_status
from proxy_rotation import fetch


def links_constructor(ticker):
    base_url = r"https://api.quickfs.net/stocks/"
    api_key = r"grL0gNYoMoLUB1ZoAKLfhXkoMoLODiO1WoL9.grLtk3PoMoLmqFEsMasbNK9fkXudkNBtR2jpkr5dINZoAKLtRNZoMl" \
              r"G2PQuiWQknWJOcOpEfqXGoMwcoqNWaka9tIKO6OlG1MQk0OosoIS1fySsoMoLuySBwh2tbhpV0yXVdyXBakuHwhSVthK" \
              r"5lh20oAKLsRNWiq29rIKO6OaWIJQufWG1Vq1RrZuWSIKOcOwHryNIthXBwICO6PKsokpBwyS9dDFLtqoO6grLBDrO6PCs" \
              r"oZ0GoMlH9vN0.sbxSI5du4jS2FlR0-qktBT62siUOb1_YMMWYs3GDYou"

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

    analyst_growth_rate = soup.find('td', attrs={"data-reactid": "427"}).text
    analyst_growth_rate = float(analyst_growth_rate.replace('%', '')) / 100

    return analyst_growth_rate
