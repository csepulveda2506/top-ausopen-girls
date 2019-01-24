from typing import List

import faust


class TwitterUserRecord(faust.Record, serializer='json'):
    name: str
    username: str


class TwitsRecord(faust.Record, serializer='json'):
    text: str
    hash_tags: List[str]
    screen_name: str
    retweets_count: int


class PlayerTwitsRecord(faust.Record, serializer='json'):
    player: TwitterUserRecord
    twits: List[TwitsRecord]
