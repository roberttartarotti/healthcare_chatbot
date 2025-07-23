"""
Celery beat scheduler for Healthcare Celery Library

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import logging
import sys
import os
from typing import Optional
from celery.bin.beat import beat as celery_beat
from .app import get_celery_app
from .config import CeleryConfig
from .exceptions import BeatError

logger = logging.getLogger(__name__)


def start_beat(
    schedule: Optional[str] = None,
    loglevel: Optional[str] = None,
    pidfile: Optional[str] = None
) -> None:
    """
    Start the Celery beat scheduler.
    
    Args:
        schedule: Schedule file path
        loglevel: Logging level
        pidfile: PID file path
        
    Raises:
        BeatError: If beat scheduler fails to start
    """
    try:
        app = get_celery_app()
        
        if schedule is None:
            schedule = "/tmp/celerybeat-schedule"
        if loglevel is None:
            loglevel = CeleryConfig.worker_log_level.lower()
        if pidfile is None:
            pidfile = "/tmp/celerybeat.pid"
        
        os.makedirs(os.path.dirname(schedule), exist_ok=True)
        os.makedirs(os.path.dirname(pidfile), exist_ok=True)
        
        logger.info("Starting Celery beat scheduler")
        logger.info(f"Schedule file: {schedule}, PID file: {pidfile}")
        
        beat = celery_beat(app)
        
        worker_options = [
            "--loglevel", loglevel,
            "--schedule", schedule,
            "--pidfile", pidfile,
        ]
        
        beat.run_from_argv([sys.argv[0]] + worker_options)
        
    except Exception as e:
        logger.error(f"Failed to start beat scheduler: {e}")
        raise BeatError(f"Failed to start beat scheduler: {e}", schedule_name=schedule)


def main() -> None:
    """Main entry point for starting the Celery beat scheduler."""
    try:
        start_beat()
    except KeyboardInterrupt:
        logger.info("Beat scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Beat scheduler failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 