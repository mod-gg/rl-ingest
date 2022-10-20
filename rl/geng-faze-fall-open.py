from copy import deepcopy
import pandas as pd
from octanegg import Octane
import matplotlib.pyplot as plt
import seaborn as sns
import re


def create_dataframes():
    def get_games():
        with Octane() as client:
            games = []
            page = 1
            while True:
                current_page_events = client.get_games(
                    group="rlcs", after="2022-10-06", before="2022-10-10", page=page
                )
                if not current_page_events:  # no more games
                    break
                games += current_page_events
                page += 1
        return games

    def split_games(games):
        team_games = []

        for game in games:
            a = deepcopy(game)
            b = deepcopy(game)

            a["team"] = a.pop("orange")
            a["opponent"] = a.pop("blue")

            b["team"] = b.pop("blue")
            b["opponent"] = b.pop("orange")
            team_games.append(a)
            team_games.append(b)

        player_games = []
        for game in team_games:
            for i in range(len(game["team"]["players"])):
                igame = deepcopy(game)
                igame["team"]["players"] = game["team"]["players"][i]
                player_games.append(igame)

        return player_games

    def normalize_dataframes(player_games):
        df = pd.json_normalize(player_games)
        return df

    games = get_games()
    player_games = split_games(games)
    df = normalize_dataframes(player_games)
    return df

def filter_frames(df):
    tdf = df.drop(columns=[x for x in df.columns if "players" in x])
    tdf = tdf.loc[tdf.astype(str).drop_duplicates().index]
    tdf["team.win_count"] = tdf["team.winner"].fillna(False) * 1
    tdf["team.team.stats.core.assistsPerGoal"] = tdf["team.team.stats.core.assists"]/tdf["team.team.stats.core.goals"]
    tdf["team.team.stats.core.assistsPerGoal"]=tdf["team.team.stats.core.assistsPerGoal"].fillna(0)
    tdf["opponent.team.stats.core.assistsPerGoal"] = tdf["opponent.team.stats.core.assists"]/tdf["team.team.stats.core.goals"]
    tdf["opponent.team.stats.core.assistsPerGoal"]=tdf["opponent.team.stats.core.assistsPerGoal"].fillna(0)
    tmdf_matches = tdf.groupby(
        as_index=False, by=["team.team.team.name", "opponent.team.team.name","match.date"]
    ).mean()
    tmdf = tdf.groupby(
        as_index=False, by=["team.team.team.name", "opponent.team.team.name"]
    ).mean()
    geng_tmdf_matches = tmdf_matches.query("`team.team.team.name`.str.contains('Gen.G')")
    geng_tmdf_matches = geng_tmdf_matches.sort_values("match.date")
    geng_tmdf = tmdf.query("`team.team.team.name`.str.contains('Gen.G')")
    return(geng_tmdf, geng_tmdf_matches)

def save_plots(geng_tmdf, geng_tmdf_matches):
    team_stat_columns = [x for x in geng_tmdf_matches.columns if "team.team.stats" in x]
    for x in team_stat_columns:
        plt.figure(figsize=[13.0,9.0])
        nme = ('Gen.G ' + " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', x.split('.')[-1])).split())).title()
        plt.title(nme)
        y=x.replace('team.team.', 'opponent.team.')
        geng_tmdf_matches[nme]=geng_tmdf_matches[x]/geng_tmdf_matches[y]
        sns.stripplot(data=geng_tmdf_matches, x="match.date", y=nme, hue="opponent.team.team.name", palette=['red','dodgerblue','black','darkgreen','purple','gold'])
        plt.axhline(1.0)
        plt.xticks(geng_tmdf_matches['match.date'], ['Swiss 1',' Swiss 2','Swiss 3', 'Swiss 4','Quarterfinals', 'Semifinals', 'Finals'])
        plt.xlabel('Match')
        plt.ylabel('Gen.G Stat Ratio')
        plt.legend(title='Opponent')
        plt.savefig('team_plots/geng-ratios/'+ nme + '.png',format='png')
        plt.close()


        plt.figure(figsize=[13.0,9.0])
        nme = ('Gen.G ' + " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', x.split('.')[-1])).split())).title()
        plt.title(nme)
        y='duration'
        geng_tmdf_matches[nme]=(geng_tmdf_matches[x]/geng_tmdf_matches[y]) * 300.0
        sns.stripplot(data=geng_tmdf_matches, x="match.date", y=nme, hue="opponent.team.team.name", palette=['red','dodgerblue','black','darkgreen','purple','gold'])
        plt.xticks(geng_tmdf_matches['match.date'], ['Swiss 1',' Swiss 2','Swiss 3', 'Swiss 4','Quarterfinals', 'Semifinals', 'Finals'])
        plt.xlabel('Match')
        plt.ylabel('Gen.G Stats Per 5 Minutes')
        plt.legend(title='Opponent')
        plt.savefig('team_plots/geng-means/'+ nme + '.png',format='png')
        plt.close()

df = create_dataframes()
geng_tmdf, geng_tmdf_matches = filter_frames(df)
save_plots(geng_tmdf, geng_tmdf_matches)