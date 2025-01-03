import requests
import user_agent
from urllib.parse import urlparse
import httpx
import aiofiles

from pprint import pp
import os
import json
import asyncio
import time

from IPChanger import IPChanger

class InstagramScraper:
    USER_BASEURL = "https://www.instagram.com/api/v1/users/web_profile_info"
    X_IG_APP_ID = "936619743392459"
    PROFILES_FOLDER = os.path.join(os.getcwd(), 'profiles')

    def __init__(self) -> None:
        self.ipc = IPChanger()
        if not os.path.isdir(self.PROFILES_FOLDER):
            os.mkdir(self.PROFILES_FOLDER)

    async def __scrape_user(self, client: httpx.AsyncClient, username: str) -> dict[str, str]:
        print(f'Scraping Userdata for - {username}')
        params = {'username': username}
        headers = {
            'User-Agent': user_agent.generate_user_agent(),
            'X-IG-App-ID': self.X_IG_APP_ID
        }

        req = requests.models.PreparedRequest()
        req.prepare_url(url=self.USER_BASEURL, params=params)

        res = await client.get(req.url, headers=headers)
        data = res.json()['data']['user']
        user_dict = self.__parse_user_json(data)

        # pp(user_dict)
        user_data = json.dumps(user_dict)

        with open(os.path.join(self.PROFILES_FOLDER, f'{username}.json'), 'w') as f:
            f.write(user_data)

        print(f'Userdata saved to - \\profiles\\{username}.json')

        return {username: user_dict['Number of Followers']}

    def __scrape_user_sync(self, client: httpx.Client, username: str) -> dict[str, str]:
        print(f'Scraping Userdata for - {username}')
        params = {'username': username}
        headers = {
            'User-Agent': user_agent.generate_user_agent(),
            'X-IG-App-ID': self.X_IG_APP_ID
        }

        req = requests.models.PreparedRequest()
        req.prepare_url(url=self.USER_BASEURL, params=params)

        res = client.get(req.url, headers=headers)
        data = res.json()['data']['user']
        user_dict = self.__parse_user_json(data)

        # pp(user_dict)
        user_data = json.dumps(user_dict)

        with open(os.path.join(self.PROFILES_FOLDER, f'{username}.json'), 'w') as f:
            f.write(user_data)

        print(f'Userdata saved to - \\profiles\\{username}.json')

        return {username: user_dict['Number of Followers']}

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

    async def scrape_user_from_url(self, user_urls: list[str]):
        for user_url in user_urls:
            url = urlparse(user_url)
            username = url.path.replace("/", "")
            # self.__scrape_user(username)

    async def scrape_user_from_username(self, usernames: list[str]):
        start = time.perf_counter()
        proxy = self.ipc.getproxy()
        proxy_mounts = {
            'http://': httpx.AsyncHTTPTransport(proxy=f'http://{proxy}'),
        }

        client = httpx.AsyncClient(follow_redirects=True,
                                   mounts=proxy_mounts,
                                   timeout=10)

        tasks = []
        for username in usernames:
            tasks.append(asyncio.create_task(self.__scrape_user(client, username)))

        results = await asyncio.gather(*tasks)
        print(results)


        await client.aclose()
        print(f"Scrapning {len(usernames)} took {time.perf_counter() - start:.3f}seconds!")

    def scrape_user_from_username_sync(self, usernames: list[str]):
        start = time.perf_counter()
        client = httpx.Client(follow_redirects=True, timeout=10)
        results = [self.__scrape_user_sync(client, username) for username in usernames]
        print(results)
        client.close()
        print(f"Scraping {len(usernames)} synchronously took {time.perf_counter() - start:.3f}seconds!")

async def main():
    usernames = ['leomessi', 'theweekend', 'arianagrande', 'cristiano']
    igscr = InstagramScraper()
    await igscr.scrape_user_from_username(usernames)



# testing purposes only
if __name__ == '__main__':
    asyncio.run(main())