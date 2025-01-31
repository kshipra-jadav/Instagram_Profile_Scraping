import requests
import user_agent
from urllib.parse import urlparse
import httpx
import datetime

from pprint import pp
import os
import json
import asyncio
import time

from IPChanger import IPChanger

from db.engine import make_session
from db.influencer import Influencer
from db.posts import Posts

class InstagramScraper:
    USER_BASEURL = "https://www.instagram.com/api/v1/users/web_profile_info"
    POST_BASEURL = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    X_IG_APP_ID = "936619743392459"
    PROFILES_FOLDER = os.path.join(os.getcwd(), 'profiles')
    POSTS_FOLDER = os.path.join(os.getcwd(), 'posts')

    def __init__(self) -> None:
        self.ipc = IPChanger()
        self.session = make_session()

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

        inf = Influencer(**user_dict)

        try:
            self.session.add(inf)
            self.session.commit()
            print(f"{user_dict['name']} Successfully Inserted in DB")
        except Exception as e:
            print(f"Error occured - {e}")
            self.session.rollback()
        if scrape_posts:
            self.scrape_user_posts(user_dict['instagram_id'])

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


    def scrape_user_posts(self, user_id: str) -> None:
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

            client: httpx.Client = self.__get_proxied_client(async_client=False)

            print(f"Scraping Page Number - {page_num}")

            response = client.get(self.POST_BASEURL + json.dumps(variables))

            if 'proxy-status' in response.headers:
                print('Proxy Status Header Detected')
                curr_retries += 1
                print('Going to sleep for 2 seconds')
                time.sleep(2)
                print('Back from sleep')
                continue
            
            
            data = response.json()
            parsed_posts = self.__parse_posts(data['data'], user_id)

            if parsed_posts is None:
                print('All posts from Past One Year have been scraped.')
                print('Turning Off Scraping Now')
                break

            posts.extend(parsed_posts)

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


            try:
                self.session.bulk_insert_mappings(Posts, posts)
                print(f"{len(posts)} Posts Successfully Inserted!")
                self.session.commit()
            except Exception as e:
                print(f"There has been exception. Posts will not be committed.")
                self.session.rollback()
            
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

    def __parse_posts(self, data, user_id):
        posts = []

        for post in data['user']['edge_owner_to_timeline_media']['edges']:
            post = post['node']
            img_url = post['display_url']
            shortcode = post['shortcode']
            num_comments = post['edge_media_to_comment']['count']
            post_timestamp = post['taken_at_timestamp']
            num_likes = post['edge_media_preview_like']['count']

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
                'user_id': user_id,
                'short_code': shortcode,
                'image_url': img_url,
                'tagged_users': tagged_user,
                'sponsored_users': sponsor_usr,
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


