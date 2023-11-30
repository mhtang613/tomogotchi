from crontab import CronTab
import os

path = os.path.abspath(".").replace(os.path.expanduser('~'), '')[1:]

cron = CronTab(user=True)
cron.remove_all()   # reset cron jobs

job = cron.new(command=f"cd {path} && venv && python3 manage.py daily_update")
job.hour.on(0)  # exec at 12AM every day
job.set_comment("Decrease Hunger & Mood. Reset earned coin count.")

job = cron.new(command=f"cd {path} && echo 'working?' >> test.txt")
job.minute.every(1)  # exec every minute
job.set_comment("Test Job")

cron.write()

# To start these jobs, just run this cron.py script

# To list what cron jobs are running: crontab -l (input into terminal)
# Guide: https://betterstack.com/community/guides/scaling-python/python-scheduled-tasks/#scheduling-tasks-with-cron-jobs
