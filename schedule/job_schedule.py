# CRON JOBS CREATION ---------------------------------------------------
from crontab import CronTab # python -m pip install python-crontab
# access the system..
# note: to effectively remove cron jobs:
# list: terminal -> crontab -l
# remove: terminal -> crontab -r
cron = CronTab(user=True)
# create new cron job..
py_inst = '/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7'
py_file = '/Users/dariopopadic/PycharmProjects/fooStrat/1_sourcing.py'
job = cron.new(command = py_inst + ' ' + py_file, comment = 'foostrat_data_download')
# schedule for 24h at midnight..
job.minute.on(0)
job.hour.on(0)
# job.every(1).days()
# job.minute.every(1)
# 0 16 1,10,22 * * tells cron to run a task at 4 PM (which is the
# 16th hour) on the 1st, 10th and 22nd day of every month.
# write job to cron tab..
cron.write()

# view jobs:
for job in cron:
    print(job)

# cron.remove_all()
# cron.write()
# resources: http://blog.appliedinformaticsinc.com/managing-cron-jobs-with-python-crontab/
