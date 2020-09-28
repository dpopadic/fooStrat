# ----------------------------------------------------
# --- DATA PROCESSING
# ----------------------------------------------------
# This script reads the necessary data files and processes them into the right shape. As of now,
# two different data source formats are handled: major leagues, minor leagues
import pandas as pd
from fooStrat.processing import update_data_latest, update_data_historic
from fooStrat.mapping import odds_fields
from fooStrat.servicers import fodds

# history update ------------------------------------------------------
update_data_historic(path='data/src_data/',
                     file_desc='all-euro-data',
                     file_key=[23, 32],
                     file_key_name='season',
                     file_desc_2='new_leagues_data.xlsx',
                     file_key_name_2='Season')


# latest update ------------------------------------------------------
# read existing
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
# update data
update_data_latest(ex=source_core,
                   new_1='latest_results_major.xlsx',
                   new_2='latest_results_minor.xlsx',
                   season='2020-2021',
                   path='data/src_data/')


# odds update --------------------------------------------------------
match_odds = fodds(data=source_core,
                   field_home=list(odds_fields.get('odds_home_win')),
                   field_away=list(odds_fields.get('odds_away_win')),
                   field_draw=list(odds_fields.get('odds_draw_win')))
match_odds.to_pickle('./data/pro_data/match_odds.pkl')

# meta data ----------------------------------------------------------
leagues_map = pd.DataFrame(source_core.loc[:, 'div'].unique(), columns={'div'})
leagues_map.to_pickle('data/src_data/leagues_map.pkl')










