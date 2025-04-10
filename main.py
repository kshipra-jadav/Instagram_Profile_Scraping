import asyncio

from InstagramScraper import InstagramScraper

def main():
    usernames = ['virdas']
    igscr = InstagramScraper()
    igscr.scrape_user_from_username(usernames=usernames, scrape_posts=True)



# testing purposes only
if __name__ == '__main__':
    main()
