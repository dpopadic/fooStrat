

import pandas as pd
from fooStrat.constants import fp_cloud_log
from fooStrat.evaluation import comp_pnl_eval

results = con_res(data=source_core, obj='lose')

data = pd.read_excel(fp_cloud_log + 'predictions_lose.xlsx',
                     sheet_name='lose',
                     index_col=0)

data = data[['div', 'season', 'date_play', 'team', 'market']]
data.rename(columns={'date_play': 'date'}, inplace=True)


par = pd.merge(data,
               results[['div', 'season', 'date', 'team', 'val']],
               on = ['div', 'season', 'date', 'team'],
               how='left')

par = par.dropna()
par.rename(columns={'date_play': 'date', 'val': 'res'}, inplace=True)
par['weight'] = 1
par['val'] = 1 / par['market']
par['payoff'] = par.loc[:, ['val', 'res', 'weight']].apply(comp_pnl_eval, stake=10, axis=1)
par['payoff_cum'] = par.loc[:, 'payoff'].cumsum(skipna=True)


