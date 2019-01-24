import random
from typing import List

import tweepy

from conf.settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, \
    ACCESS_TOKEN_SECRET
from faust_app.records import TwitsRecord


class TwitterService:
    _TWIT_COUNT: int = 10
    _auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    def __init__(self):
        self._auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self._auth)

    def get_twits(self, username: str = 'elise_mertens') -> List[TwitsRecord]:
        response = self.api.search(q=f"{username}",
                                   rpp=random.sample(range(1, 90), 1))
        return [TwitsRecord(res.text,
                            [hashtag['text'] for hashtag in
                             res.entities['hashtags']],
                            res.user.screen_name,
                            res.retweet_count) for res in response]


if __name__ == "__main__":
    service = TwitterService()
    print(list(twit.text for twit in service.get_twits()))
