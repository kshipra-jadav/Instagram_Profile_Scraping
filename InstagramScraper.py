import requests
import user_agent
from urllib.parse import urlparse

from pprint import pp
import os
import json

from IPChanger import IPChanger
from utils import timeit

class InstagramScraper:
    USER_BASEURL = "https://www.instagram.com/api/v1/users/web_profile_info"
    X_IG_APP_ID = "936619743392459"
    PROFILES_FOLDER = os.path.join(os.getcwd(), 'profiles')

    def __init__(self) -> None:
        self.ipc = IPChanger()

    @timeit
    def __scrape_user(self, username: str) -> None:
        print(f'Scraping Userdata for - {username}')
        params = {'username': username}
        headers = {
            'User-Agent': user_agent.generate_user_agent(),
            'X-IG-App-ID': self.X_IG_APP_ID
        }
        proxy = {
            'http': self.ipc.getproxy(),
        }

        req = requests.models.PreparedRequest()

        req.prepare_url(url=self.USER_BASEURL, params=params)

        res = requests.get(req.url, headers=headers, proxies=proxy)
        data = res.json()['data']['user']
        user_dict = self.__parse_user_json(data)

        # pp(user_dict)
        user_data = json.dumps(user_dict)

        with open(os.path.join(self.PROFILES_FOLDER, f'{username}.json'), 'w') as f:
            f.write(user_data)

        print(f'Userdata saved to - \\profiles\\{username}.json')

    @staticmethod
    def __parse_user_json(user: dict[str, str: str]) -> dict[str, str]:
        full_name = user['full_name']
        ig_id = user['id']
        cat_enum = user['category_enum']
        cat_name = user['category_name']
        related_profiles = [profile['node']['username'] for profile in user['edge_related_profiles']['edges']]
        num_followers = user['edge_followed_by']['count']
        num_posts = user['edge_owner_to_timeline_media']['count']

        user_dict = {
            'Full Name': full_name,
            'Instagram ID': ig_id,
            'Cateogy ENUM': cat_enum,
            'Category Name': cat_name,
            'Number of Posts': num_posts,
            'Number of Followers': num_followers,
            'Related Profiles': related_profiles,
        }

        return user_dict

    def scrape_user_from_url(self, user_url: str):
        url = urlparse(user_url)
        username = url.path.replace("/", "")
        self.__scrape_user(username)

    def scrape_user_from_username(self, username: str):
        self.__scrape_user(username)

@timeit
def main():
    usernames = ['leomessi', 'cristiano', 'arianagrande', 'theweekend']
    igscr = InstagramScraper()
    for username in usernames:
        igscr.scrape_user_from_username(username)


# testing purposes only
if __name__ == '__main__':
    main()