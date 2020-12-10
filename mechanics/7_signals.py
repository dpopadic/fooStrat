import pandas as pd
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
source_core.query("div == 'E0' & date == '2020-11-30'")

data_fct.query("div == 'E0'").sort_values('date')['date'].unique()
a=data_fct.query("div == 'E0' & team == 'liverpool' & season == '2020'")
data_fct.query("div == 'E0' & date == '2020-11-30'")






