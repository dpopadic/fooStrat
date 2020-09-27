# test task ----------------------
import os
from datetime import datetime
# relevant working directory..
# if in project: proj_path = os.path.join(os.getcwd(), '')
proj_path = '/Users/dariopopadic/PycharmProjects/fooStrat/'
fl = proj_path + 'append.txt'
myFile = open(fl, 'a+')
myFile.write('\nAccessed on ' + str(datetime.now()))
myFile.close()


