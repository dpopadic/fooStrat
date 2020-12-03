# ----------------------------------------------------
# --- DATA RESTORATION
# ----------------------------------------------------
from fooStrat.processing import update_data_historic, fp_cloud

# history update ------------------------------------------------------
update_data_historic(file_desc='all-euro-data',
                     file_key=[23, 32],
                     file_key_name='season',
                     file_desc_2='new_leagues_data.xlsx',
                     file_key_name_2='Season')
