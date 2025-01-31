from db.engine import make_session
from db.influencer import Influencer

def get_all_influencers():
    """Fetch all influencers from the database and return them as a list."""
    session = make_session()
    try:
        influencers = session.query(Influencer).all()
        return influencers
    finally:
        session.close()

def print_all_influencers():
    """Fetch and print all influencers."""
    influencers = get_all_influencers()
    for influencer in influencers:
        print(influencer)


