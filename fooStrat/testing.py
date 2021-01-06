from datetime import datetime
import pandas as pd
from fooStrat.constants import fp_cloud_process
df = pd.read_pickle(fp_cloud_process + 'flib_e0.pkl')
fp = fp_cloud_process + 'etl_test_log.txt'
myFile = open(fp, 'a+')
myFile.write('\n' + str(df['date'].max()) + ' | data processed on ' + str(datetime.now()))
myFile.close()




