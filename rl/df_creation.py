from numpy import full
import pandas as pd
from octanegg import Octane
def create_dataframes():
    def get_games():
        with Octane() as client:
            games = []
            page = 1
            while True:
                current_page_events = client.get_games(
                    group='rlcs', after="2022-04-01", before="2022-10-01", page=page
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

    def sort_full(games):
        full_games = []
        ks=['blue','orange']
        game_keys=[]
        for game in games:
            for k in ks:
                filterByKey = lambda keys: {x: game[x] for x in game.keys() if x != k}
                a=filterByKey(game)
                a['team']=a.pop(ks[ks.index(k)-1])
                game_keys += a.keys()
                full_games.append(a)
        testgame=pd.json_normalize(full_games, record_path=['team','players'],meta=list(set(game_keys)),errors='ignore')
        full_games[0:2]

    def normalize_dataframes(player_games, team_games, match_games, event_games):
        df_players=pd.json_normalize(player_games)
        df_teams=pd.json_normalize(team_games)
        df_matches=pd.json_normalize(match_games)
        df_matches=df_matches[df_matches.columns[df_matches.columns.str.startswith(('_id','slug','event','stage','date','format','game_id'))]]
        df_events=pd.json_normalize(event_games)
        return(df_players, df_teams, df_matches, df_events)

    games=get_games()
    (player_games, team_games, match_games, event_games) = sort_games(games)
    (df_players, df_teams, df_matches, df_events)=normalize_dataframes(player_games, team_games, match_games, event_games)
    return(df_players, df_teams, df_matches, df_events)

