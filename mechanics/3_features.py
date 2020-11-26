# FACTOR COMPUTATIONS -------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.features as sf
import fooStrat.processing as su

# load source data..
source_core = pd.read_pickle('data/pro_data/source_core.pkl')

# odds retrieval ------------------------------------------------------------------------------------------------------
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')

# features ------------------------------------------------------------------------------------------------------------
# - goal based factors
# - result based factors
# - attack strength factors
# - standings based factors
# - turnaround ability factors
# - head-to-head factors
# - home factor
fgb = sf.feat_goalbased(data=source_core, k=5)
frb = sf.feat_resbased(data=source_core)
fstre = sf.feat_strength(data=source_core, k=5)
fsb = sf.feat_stanbased(data=source_core)
ftf = sf.feat_turnaround(data=source_core)
fh2h = sf.feat_h2h(data=source_core)
hf = sf.fhome(data=source_core)
fun = sf.feat_odds_uncertainty(data=source_core, odds=match_odds)


# factor library ------------------------------------------------------------------------------------------------------
fsb.field.unique()
su.delete_flib(field=["points_advantage", "rank_position"])

su.update_flib(data=[fsb], update=True, recreate_feature=True)
su.update_flib(data=[fgb, frb, fstre, fsb, ftf, fh2h, hf, fun], update=False)

# consolidate for feature evaluation
su.consol_flib()


# verify..
flib_x = pd.read_pickle('data/pro_data/flib_e0.pkl')
flib_x.field.unique()
flib_x.query("div=='E0' & season==2020 & team=='liverpool' & date=='2020-09-12'")


















