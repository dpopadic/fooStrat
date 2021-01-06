# ETL RUNNER ----------------------------------------------------------------------------------------------------------
import os
os.system('python mechanics/1_sourcing.py')
os.system('python mechanics/3_processing.py')
os.system('python mechanics/4_features.py')
os.system('python mechanics/7_signals.py')

