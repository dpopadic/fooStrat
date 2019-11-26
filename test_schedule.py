# test schedule ----------------------
from crontab import CronTab

cron = CronTab(user='dario')
cron = CronTab(user=True)
job = cron.new(command='test_task.py')
job.minute.every(1)
cron.write()

for job in cron:
    print(job)
# job.enable(False)
# job.is_enabled()
# cron.remove_all()