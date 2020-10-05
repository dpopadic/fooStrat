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

# team clusters -------------------------------------------------------------------------------------------------------

tqual.query("div=='E0' & season=='2019'")
tqual.query("team=='arsenal'")
acf.query("team=='liverpool'")
fsb['field'].unique()
a = fsb.query("div=='E0' & season=='2018' & field=='team_quality_consistency'")

# issue with expand_field: only considers dates available in data provided
# needs a a parameter with data div, season, date -> date_univ = con_date_univ(data=source_core)


# standings based factors ---------------------------------------------------------------------------------------------
# note: these factors should also be normalised internally
fsb = sf.feat_stanbased(data=source_core)


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


















