# STRATEGY TESTING ------------------------------------------------------------------------
import pandas as pd
from foostrat_utils import con_res, comp_pnl

# load all required data
source_core = pd.read_pickle('pro_data/source_core.pkl')
factor_library = pd.read_pickle('pro_data/factor_library.pkl')
match_odds = pd.read_pickle('pro_data/match_odds.pkl')

# get results in custom shape
results = con_res(source_core, field=['FTR'])
# factor: max factor for every day played..
positions = factor_library.loc[factor_library.groupby(['div', 'season', 'date', 'field'])['val'].idxmax()].reset_index(drop=True)
positions = positions.loc[:,['div', 'season', 'date', 'team']]
# retrieve the right odds..
odds = match_odds.query('field == "odds_win"')

# calculate pnl
pnl_strats = comp_pnl(positions=positions, odds=odds, results=results, event='win', stake=10)






