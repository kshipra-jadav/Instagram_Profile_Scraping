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
    POST_BASEURL = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    X_IG_APP_ID = "936619743392459"
    PROFILES_FOLDER = os.path.join(os.getcwd(), 'profiles')
    POSTS_FOLDER = os.path.join(os.getcwd(), 'posts')

    def __init__(self) -> None:
        self.ipc = IPChanger()

        if not os.path.isdir(self.PROFILES_FOLDER):
            os.mkdir(self.PROFILES_FOLDER)

        if not os.path.isdir(self.POSTS_FOLDER):
             os.mkdir(self.POSTS_FOLDER)

    async def __scrape_user(self, username: str) -> dict[str, str]:
        client = self.__get_proxied_client()

        print(f"Scraping User - {username}")
        
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

        await client.aclose()

        return {username: user_dict['Instagram ID']}
    @staticmethod
    def __parse_user_json(user: dict[str, str: str]) -> dict[str, str]:
        full_name = user['full_name']
        ig_id = user['id']
        cat_enum = user['category_enum']
        cat_name = user['category_name']
        related_profiles = [profile['node']['username'] for profile in user['edge_related_profiles']['edges']]
        num_followers = user['edge_followed_by']['count']
        num_posts = user['edge_owner_to_timeline_media']['count']
        bio = user['biography_with_entities']['raw_text']

        user_dict = {
            'Full Name': full_name,
            'Instagram ID': ig_id,
            'Cateogy ENUM': cat_enum,
            'Category Name': cat_name,
            'Number of Posts': num_posts,
            'Number of Followers': num_followers,
            'Related Profiles': related_profiles,
            'Biography': bio
        }

        return user_dict

    async def scrape_user_from_url(self, user_urls: list[str]):
        for user_url in user_urls:
            url = urlparse(user_url)
            username = url.path.replace("/", "")
            # self.__scrape_user(username)

    async def scrape_user_from_username(self, usernames: list[str]):
        tasks = []
        start = time.perf_counter()
        for username in usernames:
            tasks.append(asyncio.create_task(self.__scrape_user(username)))

        results = await asyncio.gather(*tasks)
        print(results)


        print(f"Scrapning {len(usernames)} took {time.perf_counter() - start:.3f}seconds!")

    async def scrape_user_posts(self, user_id: str) -> None:
        variables = {
        "id": user_id,
        "first": 12,
        "after": None,
        }

        page_num = 1

        max_retries = 10
        curr_retries = 0

        posts = []
        
        while True:
            if curr_retries > max_retries:
                print('Max Retries Exceeded')
                print('Stopping now ... ')
                break

            client: httpx.AsyncClient = self.__get_proxied_client()

            print(f"Scraping Page Number - {page_num}")

            response = await client.get(self.POST_BASEURL + json.dumps(variables))

            if 'proxy-status' in response.headers:
                print('Proxy Status Header Detected')
                curr_retries += 1
                print('Going to sleep for 2 seconds')
                await asyncio.sleep(2)
                print('Back from sleep')
                continue
            
            
            data = response.json()

            posts.extend(self.__parse_posts(data['data']))

            page_info = data['data']["user"]["edge_owner_to_timeline_media"]['page_info']

            if not page_info['has_next_page']:
                print('Max Amount of Posts Have Been Scraped')
                print(f'Number of Posts Scraped - {len(posts)}')
                break

            if variables["after"] == page_info["end_cursor"]:
                print('Max Amount of Posts Have Been Scraped')
                print(f'Number of Posts Scraped - {len(posts)}')
                break

            variables["after"] = page_info["end_cursor"]

            page_num += 1

            await client.aclose()

            with open(os.path.join(self.POSTS_FOLDER, f'{user_id}.json'), 'w') as f:
                json.dump(posts, f, indent=4)

    def __get_proxied_client(self) -> httpx.AsyncClient:
        proxy = self.ipc.getproxy()
        proxy_mounts = {
            'http://': httpx.AsyncHTTPTransport(proxy=f'http://{proxy}'),
        }

        client = httpx.AsyncClient(follow_redirects=True, mounts=proxy_mounts, timeout=40)

        return client

    def __parse_posts(self, data):
        posts = []

        for post in data['user']['edge_owner_to_timeline_media']['edges']:
            post = post['node']
            img_url = post['display_url']
            shortcode = post['shortcode']
            num_comments = post['edge_media_to_comment']['count']
            post_timestamp = post['taken_at_timestamp']
            num_likes = post['edge_media_preview_like']['count']
            user_id = post['owner']['id']

            caption = None
            tagged_user = []
            sponsor_usr = []

            if len(post['edge_media_to_caption']['edges']) == 0:
                caption = ""
           
            else:
                caption = post['edge_media_to_caption']['edges'][0]['node']['text']
            
            if len(post['edge_media_to_tagged_user']) > 0:
                users = post['edge_media_to_tagged_user']['edges']

                for user in users:
                    tagged_user.append(user['node']['user']['username'])
            
            if len(post['edge_media_to_sponsor_user']['edges']) > 0:
                users = post['edge_media_to_sponsor_user']['edges']

                for user in users:
                    sponsor_usr.append(user['node']['sponsor']['username'])

            post_dict = {
                'Image URL': img_url,
                'Tagged Users': tagged_user,
                'Caption': caption,
                'Short Code': shortcode,
                'Number of Comments': num_comments,
                'Sponsor Users': sponsor_usr,
                'Post Timestamp': post_timestamp,
                'Number of Likes': num_likes,
                'User ID': user_id
            }

            posts.append(post_dict)
        
        return posts



def count_rel():
    for file in os.listdir('profiles'):
        with open(f'profiles/{file}', 'r') as f:
            data = json.load(f)

            print(f"{data['Full Name']} - {len(data['Related Profiles'])}")


async def main():
    usernames = ['leomessi', 'theweekend', 'arianagrande', 'cristiano', 'virdas']
    igscr = InstagramScraper()
    # await igscr.scrape_user_from_username(usernames=['mrtechsingh'])
    await igscr.scrape_user_posts(user_id='173560420') # cristiano



# testing purposes only
if __name__ == '__main__':
    asyncio.run(main())