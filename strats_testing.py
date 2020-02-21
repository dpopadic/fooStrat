# STRATEGY TESTING ------------------------------------------------------------------------
import pandas as pd
from foostrat_utils import con_res, comp_pnl

# load all required data
data_prc = pd.read_pickle('pro_data/data_prc.pkl')
data_fct = pd.read_pickle('pro_data/data_fct.pkl')
data_odds = pd.read_pickle('pro_data/data_odds.pkl')

# get results in custom shape
results = con_res(data_prc, field=['FTR'])
# factor: max factor for every day played..
positions = data_fct.loc[data_fct.groupby(['div', 'season', 'date', 'field'])['val'].idxmax()].reset_index(drop=True)
positions = positions.loc[:,['div', 'season', 'date', 'team']]
# retrieve the right odds..
odds = data_odds.query('field == "odds_win"')

# calculate pnl
pnl_strats = comp_pnl(positions=positions, odds=odds, results=results, event='win', stake=10)






