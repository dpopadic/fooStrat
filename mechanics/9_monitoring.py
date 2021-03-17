import pandas as pd
from fooStrat.constants import fp_cloud, fp_cloud_log
from fooStrat.evaluation import trade_monitor

source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
trade_monitor(data=source_core, path=fp_cloud_log)



