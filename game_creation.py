import pandas as pd
from octanegg import Octane
from pydantic import BaseModel
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

with Octane() as client:
    games = []
    page = 1
    while True:
        current_page_events = client.get_games(
            group='rlcs', after="2020-06-01", before="2022-10-01", page=page
        )
        if not current_page_events:  # no more games
            break
        games += current_page_events
        page += 1

player_games = []
for game in games:
    player_games.append(game['blue'])
    player_games.append(game['orange'])

import json
with open('playerdata.json', 'w') as f:
    json.dump(player_games, f)

df_player_games=pd.json_normalize(player_games, record_path=['players'])

