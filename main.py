import asyncio

from InstagramScraper import InstagramScraper
from db.models import init_db
from db import queries

def main():
    usernames = ['leomessi', 'virdas']
    igscr = InstagramScraper()
    igscr.scrape_user_from_username(usernames=usernames, scrape_posts=True)
    # igscr.scrape_user_posts(user_id='173560420') # cristiano



# testing purposes only
if __name__ == '__main__':
    init_db()
    main()
