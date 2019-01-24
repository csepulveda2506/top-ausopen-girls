import json
import logging
import sys
from typing import List

import faust
from kafka.errors import KafkaError
from kafka.producer import KafkaProducer

from faust_app.records import TwitsRecord, PlayerTwitsRecord, TwitterUserRecord
from twit.twitter_api import TwitterService

app = faust.App(
    'ausopen',
    broker='kafka://localhost:9092',
)

twitter_service: TwitterService = TwitterService()
KAFKA_SERVERS: List[str] = ['localhost:9092']
TWITTER_HANDLES_TOPIC: str = 'players-handles'
TWITTER_HANDLES_FILE: str = 'players_handles.json'
PLAYER_TWITS_TOPIC: str = 'players-twits'
twits_topic: faust.types.TopicT = app.topic(PLAYER_TWITS_TOPIC,
                                            key_type=str,
                                            value_type=PlayerTwitsRecord,
                                            partitions=8)
twits_table: faust.types.TableT = app.Table(PLAYER_TWITS_TOPIC)

producer = KafkaProducer(bootstrap_servers=KAFKA_SERVERS,
                         value_serializer=lambda m: json.dumps(m).encode(
                             'ascii'))


@app.agent(TWITTER_HANDLES_TOPIC)
async def merge_twits_to_players(players):
    async for player in players:
        print('Matching player handles to twits')
        twits = twitter_service.get_twits(player['username'])
        await app.send(channel=twits_topic, key=player['username'],
                       value=PlayerTwitsRecord(
                           player=TwitterUserRecord(
                               name=player['name'],
                               username=player[
                                   'username']),
                           twits=[
                               TwitsRecord(
                                   text=twit.text,
                                   hash_tags=twit.hash_tags,
                                   screen_name=twit.screen_name,
                                   retweets_count=twit.retweets_count) for
                               twit in twits]))


@app.agent(PLAYER_TWITS_TOPIC)
async def populate_table(player_twits):
    async for player_twit in player_twits:
        twits_table[player_twit.player.username] = player_twit.twits


@app.page('/players/{player}')
@app.table_route(table=twits_table, match_info='player')
async def get_player_twits(web, request, player):
    print(twits_table.keys())
    return web.json({
        player: twits_table[player]
    })


@app.page('/players')
@app.table_route(table=twits_table)
async def get_player_twits(web, request):
    return web.json(dict(twits_table.items()))


@app.timer(interval=60.0)
async def sync_players_handles():
    print('Syncing players data')
    data = __read_data__()
    for player in data:
        try:
            future = producer.send(TWITTER_HANDLES_TOPIC,
                                   key=bytes(player['name'], "ascii"),
                                   value=player)
            ignore = future.get(timeout=10)
        except KafkaError as e:
            print(logging.log(level=logging.ERROR, msg=e))
            sys.exit(1)
        except KeyboardInterrupt:
            producer.close()


def __read_data__():
    with open(TWITTER_HANDLES_FILE) as f:
        return json.load(f)
