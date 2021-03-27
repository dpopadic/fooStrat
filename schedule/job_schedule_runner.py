from crontab import CronTab
cron = CronTab(user=True)
py_inst = '/Users/dariopopadic/PycharmProjects/fooStrat/venv/bin/python3.7'
py_file = '/Users/dariopopadic/PycharmProjects/fooStrat/mechanics/8_runner.py'
job = cron.new(command = py_inst + ' ' + py_file, comment = 'foostrat_etl')
# schedule for 24h at 2pm
job.hour.on(15)
job.minute.on(0)
cron.write()

# view jobs:
for job in cron:
    print(job)


# cron.remove_all()

