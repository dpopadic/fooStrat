# FACTOR CALCULATION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, fhome, odds_fields, fodds, expand_field, jitter, comp_score

# load source data..
source_core = pd.read_pickle('pro_data/source_core.pkl')


# odds retrieval ------------------------------------------------------------------------------------------------------
# get relevant odds
match_odds = fodds(source_core,
                   field_home=list(odds_fields.get('odds_home_win')),
                   field_away=list(odds_fields.get('odds_away_win')),
                   field_both=list(odds_fields.get('odds_draw_win')))
match_odds.to_pickle('./pro_data/match_odds.pkl')


# goal superiority rating ---------------------------------------------------------------------------------------------
# compute factor
data_gsf_0 = fgoalsup(data=source_core, field=['FTHG', 'FTAG'], field_name=['g_scored', 'g_received'], k=5)

# fgoalsup: need to neutralise score for teams that played in lower/upper league before: set to 0


a=source_core.query('div=="E0" & date=="2019-08-09" & (field=="FTHG" | field=="FTAG")')
data_gsf_0.query('div=="E0" & date=="2019-08-09"')

data = source_core
data = data_fct.loc[:, ['div', 'date', 'season', 'team']]
data.query('div=="E0" & date=="2019-08-09"')

def newcomers(data):
    """Identify newcomers (promoted/demoted teams). This is used to neutralise scores for these teams at
    the start of each season.

    Parameters:
    -----------
        data (dataframe):   a dataframe with columns div, date, season, team

    """
    # assemble all teams by season, div
    U = data.groupby(['season', 'div'])['team'].unique().reset_index()
    Ue = U.apply(lambda x: pd.Series(x['team']), axis=1).stack().reset_index(level=1, drop=True)
    Ue.name = 'team'
    Ue = U.drop('team', axis=1).join(Ue)
    # need to synchronise seasons!

Ue.query('(div=="E0" & season=="2019-2020")')
a = Ue.query('(div=="E0" | div=="E1")')
a.query('div=="E0" & season=="2019-2020"')
a.query('div=="E1" & season=="2018-2019"')

a=data_gsf_0.query('div=="E0" & season=="2019-2020"')
source_core.query('div=="E0" & date=="2020-02-19" & (field=="FTHG" | field=="FTAG")')



# expand across time (and impute across divisions)
data_gsf = expand_field(data=data_gsf_0, impute=True)
# calculate cross-sectional signal across divisions (enable by div)..
data_gsf_ed = comp_score(data=data_gsf, metric='z-score')




# home factor ---------------------------------------------------------------------------------------------------------
# no need for expansion for boolean factors!
data_hf = fhome(data=source_core)





# factor library ------------------------------------------------------------------------------------------------------
factor_library = pd.concat([data_gsf_ed, data_hf],
                           axis=0,
                           sort=False,
                           ignore_index=True)
factor_library.to_pickle('./pro_data/factor_library.pkl')







