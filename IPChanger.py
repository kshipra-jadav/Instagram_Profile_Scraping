import requests
from bs4 import BeautifulSoup
from pprint import pp

PROXIES_WEBSITE = 'https://free-proxy-list.net/'

class IPChanger:
    def __init__(self):
        pass

    def scrape_proxies(self):
        content = requests.get(PROXIES_WEBSITE).content
        soup = BeautifulSoup(content, features='html.parser')

        ip_addresses = []

        tbody = soup.find('table').find('tbody')

        for tr in tbody.find_all('tr'):
            ip_addresses.append(tr.find('td').text)

        pp(ip_addresses)



# for testing purpose only
if __name__ == '__main__':
    ipc = IPChanger()
    ipc.scrape_proxies()