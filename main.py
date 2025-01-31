import asyncio

from InstagramScraper import InstagramScraper
from db.models import init_db
from db import queries

async def main():
    usernames = ['leomessi', 'theweekend', 'arianagrande', 'cristiano', 'virdas']
    igscr = InstagramScraper()
    await igscr.scrape_user_from_username(usernames=usernames)
    # await igscr.scrape_user_posts(user_id='173560420') # cristiano



# testing purposes only
if __name__ == '__main__':
    init_db()
    # asyncio.run(main())

    queries.print_all_influencers()
