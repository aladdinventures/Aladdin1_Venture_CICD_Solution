
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

class NewsBotScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def add_job(self, func, trigger, **kwargs):
        """Adds a job to the scheduler."""
        self.scheduler.add_job(func, trigger, **kwargs)

    def start(self):
        """Starts the scheduler."""
        print("Scheduler started.")
        self.scheduler.start()

    def shutdown(self):
        """Shuts down the scheduler."""
        print("Scheduler shutting down.")
        self.scheduler.shutdown()

if __name__ == '__main__':
    # Example usage:
    def my_job(name):
        print(f"Job \'{name}\' executed at {datetime.now()}")

    scheduler_instance = NewsBotScheduler()

    # Schedule a job to run every 5 seconds
    scheduler_instance.add_job(my_job, 'interval', seconds=5, args=["interval_job"])

    # Schedule a job to run once after 10 seconds
    # This would typically be used for a single run, but for demonstration, we'll make it a one-off
    # In a real scenario, you'd likely use a different trigger or manage job removal.
    # For simplicity, APScheduler doesn't have a direct 'run once after X seconds' trigger for BackgroundScheduler
    # A common pattern is to add a date trigger for a specific future time.
    from apscheduler.triggers.date import DateTrigger
    from datetime import timedelta
    run_time = datetime.now() + timedelta(seconds=10)
    scheduler_instance.add_job(my_job, DateTrigger(run_time), args=["one_off_job"])

    scheduler_instance.start()

    try:
        # Keep the main thread alive for the scheduler to run
        import time
        time.sleep(15) # Let it run for 15 seconds
    except (KeyboardInterrupt, SystemExit):
        scheduler_instance.shutdown()

    scheduler_instance.shutdown()

