from crontab import CronTab
import os

path = path = os.path.abspath(".")

cron = CronTab(user=True)
cron.remove_all()   # reset cron jobs

job = cron.new(command=f"cd {path} && venv && python3 manage.py decrease_hunger_mood")
job.hour.on(0)  # exec at 12AM every day
job.set_comment("Decrease Hunger & Mood")

job = cron.new(command=f"cd {path} && echo hi >> test.txt")
job.minute.every(1)  # exec every minute
job.set_comment("Test Job")

cron.write()

# To start these jobs, just run this cron.py script

# To list what cron jobs are running: crontab -l (input into terminal)
# Guide: https://betterstack.com/community/guides/scaling-python/python-scheduled-tasks/#scheduling-tasks-with-cron-jobs
