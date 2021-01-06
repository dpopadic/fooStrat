# FACTOR COMPUTATIONS -------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.features as sf
import fooStrat.processing as su
from fooStrat.constants import fp_cloud
# load source data..
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
source_core = su.latest_data_only(data=source_core)


# odds retrieval ------------------------------------------------------------------------------------------------------
match_odds = pd.read_pickle(fp_cloud + 'pro_data/match_odds.pkl')
match_odds = su.latest_data_only(data=match_odds)


# features ------------------------------------------------------------------------------------------------------------
# - goal based factors
# - result based factors
# - attack strength factors
# - standings based factors
# - turnaround ability factors
# - head-to-head factors
# - home factor
fgb = sf.feat_goalbased(data=source_core)
frb = sf.feat_resbased(data=source_core)
fstre = sf.feat_strength(data=source_core)
fsb = sf.feat_stanbased(data=source_core)
ftf = sf.feat_turnaround(data=source_core)
fh2h = sf.feat_h2h(data=source_core)
hf = sf.fhome(data=source_core)
fun = sf.feat_odds_uncertainty(data=source_core, odds=match_odds)


# factor library ------------------------------------------------------------------------------------------------------
fsb.field.unique()
# su.delete_flib(field=["points_advantage", "rank_position"])
# su.update_flib(data=[fsb], update=True, recreate_feature=True)
su.update_flib(data=[fgb, frb, fstre, fsb, ftf, fh2h, hf, fun], update=True, recreate_feature=False)
# consolidate all feature libraries (flib)
# su.consol_flib()


# verify..
# flib_x = pd.read_pickle(su.fp_cloud + 'pro_data/flib_e0.pkl')
# flib_x.field.unique()
# flib_x.query("div=='E0' & season==2020 & team=='liverpool' & date=='2020-09-12'")


















