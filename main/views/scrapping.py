from apscheduler.schedulers.background import BackgroundScheduler

class Scheduler:
    def schedulerJob(self):
        print("log,scrapping")

    def startScheduler(self):
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.start()
        scheduler.add_job(self.schedulerJob, 'interval', seconds=2)
