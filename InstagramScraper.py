import requests
import user_agent
from urllib.parse import urlparse


class InstagramScraper:
    USER_BASEURL = "https://www.instagram.com/api/v1/users/web_profile_info"
    X_IG_APP_ID = "936619743392459"

    def __init__(self) -> None:
        pass

    def __scrape_user(self, username: str) -> None:
        params = {'username': username}
        headers = {
            'User-Agent': user_agent.generate_user_agent(),
            'X-IG-App-ID': self.X_IG_APP_ID
        }

        req = requests.models.PreparedRequest()

        req.prepare_url(url=self.USER_BASEURL, params=params)

        res = requests.get(req.url, headers=headers)
        print(res.json())



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