import requests
import user_agent
from urllib.parse import urlparse

from pprint import pp

from IPChanger import IPChanger

class InstagramScraper:
    USER_BASEURL = "https://www.instagram.com/api/v1/users/web_profile_info"
    X_IG_APP_ID = "936619743392459"

    def __init__(self) -> None:
        self.ipc = IPChanger()

    def __scrape_user(self, username: str) -> None:
        params = {'username': username}
        headers = {
            'User-Agent': user_agent.generate_user_agent(),
            'X-IG-App-ID': self.X_IG_APP_ID
        }
        proxy = {
            'http': self.ipc.getproxy(),
        }

        print(proxy)

        req = requests.models.PreparedRequest()

        req.prepare_url(url=self.USER_BASEURL, params=params)

        print(req.url)

        res = requests.get(req.url, headers=headers, proxies=proxy)
        data = res.json()['data']
        user_name = data['user']['username']
        full_name = data['user']['full_name']
        ig_id = data['user']['id']
        cat_enum = data['user']['category_enum']
        cat_name = data['user']['category_name']
        related_profiles = data['user']['edge_related_profiles']['edges']
        num_followers = data['user']['edge_followed_by']['count']
        num_posts = data['user']['edge_owner_to_timeline_media']['count']

        user_dict = {
            'user_name': user_name,
            'full_name': full_name,
            'ig_id': ig_id,
            'cat_enum': cat_enum,
            'cat_name': cat_name,
            'num_posts': num_posts,
            'num_followers': num_followers,
            'related_profiles': related_profiles,
        }

        pp(user_dict)


    def scrape_user_from_url(self, user_url: str):
        url = urlparse(user_url)
        username = url.path.replace("/", "")
        self.__scrape_user(username)

    def scrape_user_from_username(self, username: str):
        self.__scrape_user(username)


# testing purposes only
if __name__ == '__main__':
    igscr = InstagramScraper()
    igscr.scrape_user_from_url("https://www.instagram.com/leomessi/?hl=en")