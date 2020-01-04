# DATA EXPLORATION ----------------------------------------------------
import pandas as pd
import numpy as np
import os
from foostrat_utils import comp_pts, reconfig_res, ret_xl_cols

# undo latest commit Alt + 9 -> log Tab -> select last commit

# all available fields in db ------------------------------------------
# get all data file names..
src_dat_path = os.path.join(os.getcwd(), 'src_data', '')
fi_nm = ['src_data/' + f for f in os.listdir(src_dat_path) if f[:13] == 'all-euro-data']
# summarise all available column names..
df_cols = ret_xl_cols(file_names=fi_nm, id_col="Div")


# non-key field mappings ----------------------------------------------
# Problem: For the same fields, some columns are defined as HomeTeam and others as HT..
# create a column mapping table by analysing the columns across data
ht_clmn = ['HomeTeam', 'HT']
at_clmn = ['AwayTeam', 'HT']
odds_clmn_h = ['AvgH', 'B365H', 'BWH', 'IWH', 'PSH', 'WHH', 'VCH', 'BbAvH', 'PSCH']
odds_clmn_d = ['AvgD', 'B365D', 'BWD', 'IWD', 'PSD', 'WHD', 'VCD', 'BbAvD', 'PSCD']
odds_clmn_a = ['AvgA', 'B365A', 'BWA', 'IWA', 'PSA', 'WHA', 'VCA', 'BbAvA', 'PSCA']
odds_clmn_b25 = ['BbMx<2.5', 'BbAv<2.5']
odds_clmn_a25 = ['BbMx>2.5', 'BbAv>2.5']

df_cols_un = pd.DataFrame(df_cols.groupby("field")["field"].apply(np.unique))
df_cols_un.shape
df_cols_un.to_clipboard(sep=",")







