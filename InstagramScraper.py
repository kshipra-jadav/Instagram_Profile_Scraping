import requests
import user_agent
from urllib.parse import urlparse, quote
import httpx
import datetime

from pprint import pp
import os
import json
import asyncio
import time

from IPChanger import IPChanger


class InstagramScraper:
    USER_BASEURL = "https://www.instagram.com/api/v1/users/web_profile_info"
    POST_BASEURL = "https://www.instagram.com/graphql/query"
    X_IG_APP_ID = "936619743392459"
    INSTAGRAM_ACCOUNT_DOCUMENT_ID = "9310670392322965"
    PROFILES_FOLDER = os.path.join(os.getcwd(), 'profiles')
    POSTS_FOLDER = os.path.join(os.getcwd(), 'posts')

    def __init__(self) -> None:
        self.ipc = IPChanger()

        if not os.path.isdir(self.PROFILES_FOLDER):
            os.mkdir(self.PROFILES_FOLDER)

        if not os.path.isdir(self.POSTS_FOLDER):
             os.mkdir(self.POSTS_FOLDER)

    def __scrape_user(self, username: str, scrape_posts=False) -> dict[str, str]:
        client = self.__get_proxied_client(async_client=False)

        print(f"Scraping User - {username}")
        
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

        print(f"{[user_dict['instagram_id'], user_dict['name']]}")

        if scrape_posts:
            self.scrape_user_posts(username)

        client.close()

        return {'User Name': user_dict['name']}
    

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
            'instagram_id': ig_id,
            'name': full_name,
            'category': cat_name,
            'enum': cat_enum,
            'num_posts': num_posts,
            'num_followers': num_followers,
            'biography': bio,
            'related_profiles': related_profiles
        }
        
        return user_dict

    def scrape_user_from_username(self, usernames: list[str], scrape_posts=False):
        for user in usernames:
            self.__scrape_user(user, scrape_posts)


    def scrape_user_posts(self, username: str) -> None:

        page_size = 12

        variables = {
            "after": None,
            "before": None,
            "data": {
                "count": page_size,
                "include_reel_media_seen_timestamp": True,
                "include_relationship_info": True,
                "latest_besties_reel_media": True,
                "latest_reel_media": True
            },
            "first": page_size,
            "last": None,
            "username": f"{username}",
            "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
            "__relay_internal__pv__PolarisShareSheetV3relayprovider": True
        }

        prev_cursor = None
        _page_number = 1

        max_retries = 10
        curr_retries = 0

        posts = []
        
        while True:
            if curr_retries > max_retries:
                print('Max Retries Exceeded')
                print('Stopping now ... ')
                break

            client: httpx.Client = self.__get_proxied_client(async_client=False)

            print(f"Scraping Page Number - {_page_number}")

            body = f"variables={quote(json.dumps(variables, separators=(',', ':')))}&doc_id={self.INSTAGRAM_ACCOUNT_DOCUMENT_ID}"

            response = client.post(
                url=self.POST_BASEURL,
                data=body,
                headers={"content-type": "application/x-www-form-urlencoded"}
            )
            

            if 'proxy-status' in response.headers:
                print('Proxy Status Header Detected')
                curr_retries += 1
                print('Going to sleep for 2 seconds')
                time.sleep(2)
                print('Back from sleep')
                continue
            
            
            data = response.json()
            pp(data)
            parsed_posts = self.__parse_posts(data['data'])

            if parsed_posts is None:
                print('All posts from Past One Year have been scraped.')
                print('Turning Off Scraping Now')
                break

            posts.extend(parsed_posts)

            page_info = data['data']["xdt_api__v1__feed__user_timeline_graphql_connection"]['page_info']

            if not page_info['has_next_page']:
                print('Max Amount of Posts Have Been Scraped')
                print(f'Number of Posts Scraped - {len(posts)}')
                break

            if variables["after"] == page_info["end_cursor"]:
                print('Max Amount of Posts Have Been Scraped')
                print(f'Number of Posts Scraped - {len(posts)}')
                break

            variables["after"] = page_info["end_cursor"]

            _page_num += 1

            
            posts.clear()
        
        client.close()


    def __get_proxied_client(self, async_client=True) -> httpx.AsyncClient | httpx.Client:
        proxy = self.ipc.getproxy()
        if async_client:
            proxy_mounts = {
                'http://': httpx.AsyncHTTPTransport(proxy=f'http://{proxy}'),
            }

            client = httpx.AsyncClient(follow_redirects=True, mounts=proxy_mounts, timeout=40)

            return client
        else:
            proxy_mounts = {
                'http://': httpx.HTTPTransport(proxy=f"http://{proxy}")
            }
            
            client = httpx.Client(follow_redirects=True, mounts=proxy_mounts, timeout=40)

            return client

    def __parse_posts(self, data):
        posts = []

        for post in data['xdt_api__v1__feed__user_timeline_graphql_connection']['edges']:
            post = post['node']
            img_url = post['display_uri']
            shortcode = post['code']
            num_comments = post['comment_count']
            post_timestamp = post['taken_at']
            num_likes = post['like_count']

            caption = None
            tagged_user = []
            sponsor_usr = []

            if len(post['caption']['text']) == 0:
                caption = ""
           
            else:
                caption = post['caption']['text']
            
            if len(post['usertags']['in']) > 0:
                users = post['usertags']['in']

                for user in users:
                    tagged_user.append(user['user']['username'])
            
            post_dict = {
                'short_code': shortcode,
                'image_url': img_url,
                'tagged_users': tagged_user,
                'caption': caption,
                'num_comments': num_comments,
                'num_likes': num_likes,
                'timestamp': post_timestamp
            }

            post_time = datetime.datetime.fromtimestamp(post_timestamp)
            curr_time = datetime.datetime.now()

            one_year_ago = curr_time - datetime.timedelta(days=365)

            if post_time < one_year_ago:
                return None


            posts.append(post_dict)


        return posts



def count_rel():
    for file in os.listdir('profiles'):
        with open(f'profiles/{file}', 'r') as f:
            data = json.load(f)
            print(f"{data['Full Name']} - {len(data['Related Profiles'])}")


