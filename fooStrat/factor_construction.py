# FACTOR COMPUTATION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from fooStrat.foostrat_utils import fhome, odds_fields, fodds, expand_field, \
    comp_score, update_flib, norm_factor, feat_goalbased, feat_resbased, \
    comp_league_standing, feat_stanbased, delete_flib, con_gameday, feat_strength, consol_flib

# load source data..
source_core = pd.read_pickle('data/pro_data/source_core.pkl')

# odds retrieval ------------------------------------------------------------------------------------------------------
# store relevant odds
match_odds = fodds(data=source_core,
                   field_home=list(odds_fields.get('odds_home_win')),
                   field_away=list(odds_fields.get('odds_away_win')),
                   field_draw=list(odds_fields.get('odds_draw_win')))
match_odds.to_pickle('./data/pro_data/match_odds.pkl')

# game day dataset
game_day = con_gameday(data=source_core)
game_day.to_pickle('./data/pro_data/game_day.pkl')


# goal based factors --------------------------------------------------------------------------------------------------
fgb = feat_goalbased(data=source_core, k=5)
fgb = norm_factor(data=fgb)

# result based factors ------------------------------------------------------------------------------------------------
frb = feat_resbased(data=source_core)
frb = norm_factor(data=frb)

# attack strength factors ---------------------------------------------------------------------------------------------
# note: normalisation performed internally
fstre = feat_strength(data = source_core, k=5)

# exploration
fstre.query("div=='E0' & season==2019 & date=='2020-07-26' & team=='chelsea'")
fstre.query("div=='E0' & season==2020 & date=='2020-09-14' & team=='chelsea'")
fstre.query("div=='E0' & season==2020 & date=='2020-09-12' & team=='liverpool'")





# standings based factors ---------------------------------------------------------------------------------------------
fsb = feat_stanbased(data=source_core)
fsb = norm_factor(data=fsb, neutralise=False)

# home factor ---------------------------------------------------------------------------------------------------------
# no need for expansion for boolean factors!
hf = fhome(data=source_core)

# factor library ------------------------------------------------------------------------------------------------------
fsb.field.unique()
delete_flib(field=["points_advantage", "rank_position"])

update_flib(data=[fsb], update=True)
update_flib(data=[fgb, frb, fstre, fsb, hf], update=False)

# consolidate for feature evaluation
consol_flib()


# verify..
flib_x = pd.read_pickle('data/pro_data/flib_e0.pkl')
flib_x.field.unique()
flib_x.query("div=='E0' & season==2020 & team=='liverpool' & date=='2020-09-12'")


















