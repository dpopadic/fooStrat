# test schedule ----------------------
from crontab import CronTab # python -m pip install python-crontab
# access the system..
cron = CronTab(user=True)
# create new cron job..
job = cron.new(command='python /Users/dariopopadic/PycharmProjects/fooStrat/test_task.py', comment = 'foostrat')
# schedule for every minute..
job.minute.every(1)
# write job to cron tab..
cron.write()

# analytics:
# view all cron jobs..
for job in cron:
    print(job)
# job.enable(False)
# job.is_enabled()
# remove all jobs..
# cron.remove_all()
# in terminal: list / remove all crontab jobs: crontab -l / crontab -r
# update the job..
for job in cron:
    if job.comment == 'foostrat':
        job.minute.every(10)
        cron.write()










