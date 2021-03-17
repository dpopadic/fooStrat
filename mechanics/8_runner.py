# ETL RUNNER ----------------------------------------------------------------------------------------------------------
import os
from datetime import datetime
from fooStrat.constants import fp_cloud_log
# python virtual env
py_inst = '/Users/dariopopadic/PycharmProjects/fooStrat/venv/bin/python3.7'
# scripts to execute
pyf_1 = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/1_sourcing.py'
pyf_2 = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/3_processing.py'
pyf_3 = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/4a_features.py'
pyf_4 = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/4b_features.py'
pyf_5 = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/7a_signals.py'
pyf_6 = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/7b_signals.py'
pyf_7 = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/9_monitoring.py'
os.system(py_inst + ' ' + pyf_1)
os.system(py_inst + ' ' + pyf_2)
os.system(py_inst + ' ' + pyf_3)
os.system(py_inst + ' ' + pyf_4)
os.system(py_inst + ' ' + pyf_5)
os.system(py_inst + ' ' + pyf_6)
os.system(py_inst + ' ' + pyf_7)

# last update stamp -----------------------------------------------
fl = fp_cloud_log + 'model_updated.txt'
fo = open(fl, 'a+')
fo.write('\nModel updated on ' + str(datetime.now()))
fo.close()
