import os
import random

import requests
from bs4 import BeautifulSoup

# TODO: Add exception handling, Databse connection

class IPChanger:
    PROXIES_WEBSITE = 'https://free-proxy-list.net/'
    PROXY_LIST_FILENAME = 'proxy-list.txt'

    def __init__(self) -> None:
        self.proxy_list: list[str] = []

    def __scrape_proxies(self) -> None:
        print('Proxy list not found. Scraping proxies first ...')
        content = requests.get(self.PROXIES_WEBSITE).content
        soup = BeautifulSoup(content, features='html.parser')

        tbody = soup.find('table').find('tbody')

        for tr in tbody.find_all('tr'):
            td = tr.find_all('td')
            ip, port = td[0].text, td[1].text
            proxy = f'{ip}:{port}'
            self.proxy_list.append(proxy)

    def getproxy(self) -> str:
        if not self.proxy_list:
            self.__scrape_proxies()

        return random.sample(self.proxy_list, k=1)[0]




# for testing purpose only
if __name__ == '__main__':
    ipc = IPChanger()
    for _ in range(5):
        print(ipc.getproxy())