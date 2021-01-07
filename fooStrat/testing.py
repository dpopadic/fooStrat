from datetime import datetime
import pandas as pd
from fooStrat.constants import fp_cloud_process
df = pd.read_pickle(fp_cloud_process + 'flib_e0.pkl')
fp = fp_cloud_process + 'etl_test_log.txt'
myFile = open(fp, 'a+')
myFile.write('\n' + str(df['date'].max()) + ' | data processed on ' + str(datetime.now()))
myFile.close()


a = pd.read_pickle(fp_cloud + 'pro_data/flib_g1.pkl')
b = pd.read_pickle(fp_cloud + 'pro_data/flib_t1.pkl')
flib = pd.concat([a, b], axis=0).reset_index(drop=True)
flib.to_pickle(fp_cloud + 'pro_data/flib_gt1.pkl')

