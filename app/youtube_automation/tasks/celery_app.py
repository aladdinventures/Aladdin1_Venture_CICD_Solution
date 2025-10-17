"""
Celery Application Configuration
YouTube Automation System v3.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from celery import Celery
from celery.schedules import crontab

from core.config import settings

# Create Celery application
celery_app = Celery(
    "youtube_automation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.video_tasks", "tasks.analytics_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    task_track_started=True,
    task_send_sent_event=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    # Sync analytics every hour
    "sync-analytics-hourly": {
        "task": "tasks.analytics_tasks.sync_all_analytics",
        "schedule": crontab(minute=0),  # Every hour
    },
    # Auto-generate videos daily
    "auto-generate-videos-daily": {
        "task": "tasks.video_tasks.auto_generate_videos",
        "schedule": crontab(hour=9, minute=0),  # 9 AM daily
    },
    # Auto-upload videos daily
    "auto-upload-videos-daily": {
        "task": "tasks.video_tasks.auto_upload_videos",
        "schedule": crontab(hour=10, minute=0),  # 10 AM daily
    },
}

if __name__ == "__main__":
    celery_app.start()

