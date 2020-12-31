import requests
from requests.exceptions import ConnectTimeout, ProxyError, SSLError
from bs4 import BeautifulSoup
import pymsgbox


def get_proxy_list():
    free_proxy_site = r'https://free-proxy-list.net'
    content = requests.get(free_proxy_site).text
    soup = BeautifulSoup(content, 'lxml')
    table = soup.find('table')
    rows = table.find_all('tr')
    cols = [[col.text for col in row.find_all('td')] for row in rows]

    proxies = list()

    for col in cols:
        if len(col) > 0:
            if col[4] == 'elite proxy' and col[6] == 'yes':
                proxies.append('https://' + col[0] + ':' + col[1])

    return proxies


def fetch(url):
    proxy_list = get_proxy_list()

    print(url)

    # First try to fetch request without using proxy rotation
    try:
        req = requests.get(url)
        return req
    except:
        for proxy in proxy_list:
            try:
                print(f'Trying proxy: {proxy}')
                req = requests.get(url, proxies={'https': proxy}, timeout=5)
                return req
            except ConnectTimeout:
                print('Connection time out error. Trying next one')
            except ProxyError:
                print('Proxy Error. Trying next one')
            except SSLError:
                print('SSL Error. Maximum retries exceeded with url. Trying next one')

    # If nothing is returned, send error message to user
    pymsgbox.alert(f"Couldn't obtain a valid proxy. Please change api key for web scraping.")
    exit()


if __name__ == '__main__':
    get_proxy_list()
