from crontab import CronTab
cron = CronTab(user=True)
py_inst = '/Users/dariopopadic/PycharmProjects/fooStrat/venv/bin/python3.7'
py_file = '/Users/dariopopadic/PycharmProjects/fooStrat/fooStrat/testing.py'
job = cron.new(command = py_inst + ' ' + py_file, comment = 'foostrat_etl')
job.minute.every(1)
cron.write()

# view jobs:
for job in cron:
    print(job)




