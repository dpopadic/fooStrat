from crontab import CronTab
cron = CronTab(user=True)
py_inst = '/Users/dariopopadic/PycharmProjects/fooStrat/venv/bin/python3.7'
py_file = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/8_runner.py'
job = cron.new(command = py_inst + ' ' + py_file, comment = 'foostrat_etl')
job.minute.every(10)
cron.write()

# view jobs:
for job in cron:
    print(job)


# cron.remove_all()

