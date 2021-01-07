# ETL RUNNER ----------------------------------------------------------------------------------------------------------
import os
from datetime import datetime
from fooStrat.constants import fp_cloud_log
os.system('python mechanics/1_sourcing.py')
os.system('python mechanics/3_processing.py')
os.system('python mechanics/4_features.py')
os.system('python mechanics/7_signals.py')

# last update stamp -----------------------------------------------
fl = fp_cloud_log + 'model_updated.txt'
fo = open(fl, 'a+')
fo.write('\nModel updated on ' + str(datetime.now()))
fo.close()
