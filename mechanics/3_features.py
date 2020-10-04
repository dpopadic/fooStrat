# FACTOR COMPUTATION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.features as sf
import fooStrat.servicers as ss
import fooStrat.processing as su

# load source data..
source_core = pd.read_pickle('data/pro_data/source_core.pkl')

# odds retrieval ------------------------------------------------------------------------------------------------------
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')

# game day dataset
game_day = ss.con_gameday(data=source_core)
game_day.to_pickle('./data/pro_data/game_day.pkl')


# goal based factors --------------------------------------------------------------------------------------------------
fgb = sf.feat_goalbased(data=source_core, k=5)
fgb = ss.norm_factor(data=fgb)

# result based factors ------------------------------------------------------------------------------------------------
frb = sf.feat_resbased(data=source_core)
frb = ss.norm_factor(data=frb)

# attack strength factors ---------------------------------------------------------------------------------------------
# note: normalisation performed internally
fstre = sf.feat_strength(data = source_core, k=5)

# exploration
fstre.query("div=='E0' & season==2019 & date=='2020-07-26' & team=='chelsea'")
fstre.query("div=='E0' & season==2020 & date=='2020-09-14' & team=='chelsea'")
fstre.query("div=='E0' & season==2020 & date=='2020-09-12' & team=='liverpool'")


# team clusters -------------------------------------------------------------------------------------------------------

data = source_core

df_0 = data[(data.field == 'FTR') | (data.field == 'FTHG') | (data.field == 'FTAG')]
# compute rolling league standings
df_1 = ss.comp_league_standing(data=df_0, home_goals='FTHG', away_goals='FTAG', result='FTR')

# approach: divide teams into 3 buckets based on previous season rank

def team_quality_cluster(data):
    "Calculates the team quality cluster features.
    "

    # last game of season
    df_2 = df_1.groupby(['div', 'season']).apply(lambda x: x[x['date'] == x['date'].max()]).reset_index(drop=True)

    # -- team quality cluster
    tqual = df_2.copy()
    tqual['val'] = tqual.groupby(['div', 'season'])['rank'].transform(
        lambda x: pd.qcut(x, q=3, labels=range(1, 3 + 1), duplicates='drop'))
    tqual = tqual[['div', 'season', 'date', 'team', 'val']]
    tqual['field'] = 'team_quality_cluster'

    # -- autocorrelation last 5y
    acf = df_2.copy()
    tmp = acf.groupby('team', as_index=False)['points'].rolling(window=5, min_periods=1).apply(
        lambda x: pd.Series(x).autocorr(lag=1))
    acf['val'] = tmp.reset_index(level=0, drop=True)
    acf = acf[['div', 'season', 'date', 'team', 'val']]
    acf['field'] = 'team_quality_consistency'
    acf = acf[acf['val'].notna()].reset_index(level=0, drop=True)

    # combine
    res = pd.concat([tqual, acf], axis=0, sort=False, ignore_index=True)
    return res


tqual.query("div=='E0' & season=='2019'")
tqual.query("team=='arsenal'")
acf.query("team=='liverpool'")

# issue with expand_field: only considers dates available in data provided
# needs a a parameter with data div, season, date -> date_univ = con_date_univ(data=source_core)




# standings based factors ---------------------------------------------------------------------------------------------
fsb = sf.feat_stanbased(data=source_core)
fsb = ss.norm_factor(data=fsb, neutralise=False)

# home factor ---------------------------------------------------------------------------------------------------------
# no need for expansion for boolean factors!
hf = sf.fhome(data=source_core)

# factor library ------------------------------------------------------------------------------------------------------
fsb.field.unique()
su.delete_flib(field=["points_advantage", "rank_position"])

su.update_flib(data=[fsb], update=True)
su.update_flib(data=[fgb, frb, fstre, fsb, hf], update=False)

# consolidate for feature evaluation
su.consol_flib()


# verify..
flib_x = pd.read_pickle('data/pro_data/flib_e0.pkl')
flib_x.field.unique()
flib_x.query("div=='E0' & season==2020 & team=='liverpool' & date=='2020-09-12'")


















