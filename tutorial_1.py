# This tutorial is from youtube: https://www.youtube.com/watch?v=3fcKKZMFbyA
import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import csv


def write_csv(data):
    with open('result.csv', 'a') as f:
        fields = ['title', 'reviews', 'released', 'tags']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow(data)


def get_html(url):
    response = requests.get(url)

    if not response.ok:
        print(f'Code: {response.status_code}, url: {url}')
    return response.text


def get_games(html):
    soup = BeautifulSoup(html, features='lxml')

    pattern = r'^https://store.steampowered.com/app/'
    games = soup.find('a', href=re.compile(pattern))

    return games


def get_hover_data(id):
    url = f'https://store.steampowered.com/apphoverpublic/{id}'
    html = get_html(url)
    soup = BeautifulSoup(html, features='lxml')

    try:
        title = soup.find('h4', class_='hover_title').text.strip()
    except:
        title = ''
        print(url)

    try:
        released = soup.find('div', class_='hover_release').span.text.split(':')[-1].strip()
    except:
        released = ''
        print(url)

    try:
        reviews_raw = soup.find('div', class_='hover_review_summary').text
    except:
        reviews = ''
        print(url)

    else:
        pattern = r'\d+'
        reviews = int(''.join(re.findall(pattern, reviews_raw)))

    try:
        tags_raw = soup.find_all('div', class_='app_tag')
    except:
        tags = ''
        print(url)
    else:
        tags_text = [tag.text for tag in tags_raw]
        tags = ", ".join(tags_text)

    data = {
        'title': title,
        'released': released,
        'reviews': reviews,
        'tags': tags
    }

    write_csv(data)


def main():
    all_games = []

    start = 0
    url = f"https://store.steampowered.com/search/results/?query&start={start}&count=100&tags=1702"

    while True:

        games = get_games(get_html(url))

        if games:
            all_games.extend(games)
            start += 100
            url = f"https://store.steampowered.com/search/results/?query&start={start}&count=100&tags=1702"
        else:
            break


    for game in all_games:
        print(game)
    #     id = game.get('data-ds-appid')
    #     get_hover_data(id)

    # Steam url
    # https: // store.steampowered.com / search /?tags = 1702

    # Infinite scroll
    # https: // store.steampowered.com / search / results /?query & start = 50 & count = 50 & dynamic_data = & sort_by = _ASC & tags = 1702 & snr = 1_7_7_240_7 & infinite = 1

    # Hover image
    # https://store.steampowered.com/apphoverpublic/751780?review_score_preference=0&l=english&pagev6=true

    pass


if __name__ == '__main__':
    main()
