from copy import deepcopy
import pandas as pd
from octanegg import Octane
def create_dataframes():
    def get_games():
        with Octane() as client:
            games = []
            page = 1
            while True:
                current_page_events = client.get_games(
                    group='rlcs', after="2022-04-01", before="2022-06-01", page=page
                )
                if not current_page_events:  # no more games
                    break
                games += current_page_events
                page += 1
        return(games)
    def sort_games(games):
        player_games = []
        team_games = []
        match_games=[]
        event_games = []
        ks=['blue','orange']
        for game in games:
            id_dict = {'game_id': game['_id']}
            event_games.append(game['match']['event'] | id_dict)
            match_games.append(game['match'] | id_dict)
            for key in ks:
                team_games.append(game[key]['team'] | id_dict)
                for player in game[key]['players']:
                    player_games.append(player | id_dict )
        return(player_games, team_games, match_games, event_games)

    def split_games(games):
        team_games=[]
        ks=['blue','orange']
        for game in games:
            for k in ks:
                filterByKey = lambda keys: {x: game[x] for x in game.keys() if x != k}
                a=filterByKey(game)
                a['team']=a.pop(ks[ks.index(k)-1])
                team_games.append(a)
    
        player_games=[]
        for game in team_games:
            for i in range(len(game['team']['players'])):
                igame=deepcopy(game)
                igame['team']['players']=game['team']['players'][i]
                player_games.append(igame)
        
        return(player_games)
    def normalize_dataframes(player_games):
        df=pd.json_normalize(player_games)
        return(df)

    games=get_games()
    player_games = sort_games(games)
    df=normalize_dataframes(player_games)
    return(df)
