# ----------------------------------------------------
# --- DATA PROCESSING
# ----------------------------------------------------
# This script reads the necessary data files and processes them into the right shape. As of now,
# two different data source formats are handled: major leagues, minor leagues
import pandas as pd
from fooStrat.processing import update_data_latest, fp_cloud
from fooStrat.mapping import odds_fields
from fooStrat.servicers import get_odds


# latest update ------------------------------------------------------
# read existing
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')


# update data
update_data_latest(ex=source_core,
                   new_1='latest_results_major.xlsx',
                   new_2='latest_results_minor.xlsx',
                   season='2020-2021')


# odds update --------------------------------------------------------
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
match_odds = get_odds(data=source_core,
                      field_home=list(odds_fields.get('odds_home_win')),
                      field_away=list(odds_fields.get('odds_away_win')),
                      field_draw=list(odds_fields.get('odds_draw_win')))
match_odds.to_pickle(fp_cloud + 'pro_data/match_odds.pkl')


# upcoming games -----------------------------------------------------
path = fp_cloud
f = 'latest_fixtures_major.xlsx'
fp = path + 'src_data/' + f
df0 = pd.read_excel(fp, sheet_name='fixtures')

from fooStrat.processing import process_data_major

extra_key = pd.DataFrame({'fi_nm': fi_nm,
                          file_key_name: '2020-2021'})
major = process_data_major(fi_nm=fi_nm,
                               extra_key=extra_key,
                               key_cols={'Div': 'div',
                                         'Date': 'date',
                                         'HomeTeam': 'home_team',
                                         'AwayTeam': 'away_team'},
                               key_cols_map={'HT': 'HomeTeam',
                                             'AT': 'AwayTeam'})





# meta data ----------------------------------------------------------
leagues_map = pd.DataFrame(source_core.loc[:, 'div'].unique(), columns={'div'})
leagues_map.to_pickle(fp_cloud + 'src_data/leagues_map.pkl')










