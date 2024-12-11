import os
import random

import requests
from bs4 import BeautifulSoup

# TODO: Add exception handling, Databse connection

class IPChanger:
    PROXIES_WEBSITE = 'https://free-proxy-list.net/'
    PROXY_LIST_FILENAME = 'proxy-list.txt'

    def __init__(self) -> None:
        self.proxy_file_path: str = os.path.join(os.getcwd(), self.PROXY_LIST_FILENAME)
        self.proxy_list: None | list[str] = self.__load_proxies() # crude implementation. replace with database call later

    def __load_proxies(self) -> None | list[str]:
        if os.path.isfile(self.proxy_file_path):
            print('Proxy list found. Loading proxies from disk ...')
            with open(self.proxy_file_path) as f:
                iplist = [line.strip('\n') for line in f]

            return iplist

        return None


    def __scrape_proxies(self) -> None:
        print('Proxy list not found. Scraping proxies first ...')
        content = requests.get(self.PROXIES_WEBSITE).content
        soup = BeautifulSoup(content, features='html.parser')

        tbody = soup.find('table').find('tbody')

        for tr in tbody.find_all('tr'):
            self.proxy_list.append(tr.find('td').text)

        with open(self.proxy_file_path, 'w') as file: # crude implementation. replace with database call later.
            for ip in self.proxy_list:
                file.write(ip)
                file.write('\n')
        print(f'Proxies saved to {self.proxy_file_path}')

    def getproxy(self) -> str:
        if not self.proxy_list:
            self.__scrape_proxies()

        return random.sample(self.proxy_list, k=1)[0]




# for testing purpose only
if __name__ == '__main__':
    ipc = IPChanger()
    print(ipc.getproxy())