import os
import random

import requests
from bs4 import BeautifulSoup

# TODO: Add exception handling, Databse connection

class IPChanger:
    PROXIES_WEBSITE = 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt'

    def __init__(self) -> None:
        self.proxy_list: list[str] = []

    def __scrape_proxies(self) -> None:
        print('Proxy list not found. Scraping proxies first ...')

        content = requests.get(self.PROXIES_WEBSITE).text

        self.proxy_list = content.split('\n')

    def getproxy(self) -> str:
        if not self.proxy_list:
            self.__scrape_proxies()

        return random.sample(self.proxy_list, k=1)[0]




# for testing purpose only
if __name__ == '__main__':
    ipc = IPChanger()
    for _ in range(5):
        print(ipc.getproxy())