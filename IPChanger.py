import os
import random

import requests
from bs4 import BeautifulSoup

PROXIES_WEBSITE = 'https://free-proxy-list.net/'
PROXY_LIST_FILENAME = 'proxy-list.txt'

class IPChanger:
    def __init__(self) -> None:
        self.proxy_list: None | list[str] = self.__load_proxies() # crude implementation. replace with database call later

    @staticmethod
    def __load_proxies() -> None | list[str]:
        if os.path.isfile(os.path.join(os.getcwd(), PROXY_LIST_FILENAME)):
            print('Proxy list found. Loading proxies from disk ...')
            with open(os.path.join(os.getcwd(), PROXY_LIST_FILENAME), 'r') as f:
                iplist = [line.strip('\n') for line in f]

            return iplist

        return None


    def __scrape_proxies(self) -> None:
        print('Proxy list not found. Scraping proxies first ...')
        content = requests.get(PROXIES_WEBSITE).content
        soup = BeautifulSoup(content, features='html.parser')

        tbody = soup.find('table').find('tbody')

        for tr in tbody.find_all('tr'):
            self.proxy_list.append(tr.find('td').text)

        with open(os.path.join(os.getcwd(), PROXY_LIST_FILENAME), 'w') as file: # crude implementation. replace with database call later.
            for ip in self.proxy_list:
                file.write(ip)
                file.write('\n')

    def getproxy(self) -> str:
        if not self.proxy_list:
            self.__scrape_proxies()

        return random.sample(self.proxy_list, k=1)[0]




# for testing purpose only
if __name__ == '__main__':
    ipc = IPChanger()
    print(ipc.getproxy())