"""
Celery worker management for Healthcare Celery Library

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

import logging
import sys
from typing import Optional, List
from .app import get_celery_app
from .config import CeleryConfig
from .exceptions import WorkerError

logger = logging.getLogger(__name__)


def start_worker(
    queues: Optional[List[str]] = None,
    concurrency: Optional[int] = None,
    hostname: Optional[str] = None,
    loglevel: Optional[str] = None
) -> None:
    """
    Start a Celery worker.
    
    Args:
        queues: List of queues to consume from
        concurrency: Number of worker processes
        hostname: Worker hostname
        loglevel: Logging level
        
    Raises:
        WorkerError: If worker fails to start
    """
    try:
        app = get_celery_app()
        
        if queues is None:
            queues = ["healthcare", "default", "high_priority", "low_priority"]
        if concurrency is None:
            concurrency = CeleryConfig.worker_concurrency
        if hostname is None:
            hostname = "healthcare-worker@%h"
        if loglevel is None:
            loglevel = CeleryConfig.worker_log_level.lower()
        
        logger.info(f"Starting Celery worker with queues: {queues}")
        logger.info(f"Concurrency: {concurrency}, Hostname: {hostname}")
        
        app.start([
            "worker",
            "--loglevel", loglevel,
            "--concurrency", str(concurrency),
            "--hostname", hostname,
            "--queues", ",".join(queues),
            "--prefetch-multiplier", str(CeleryConfig.worker_prefetch_multiplier),
            "--max-tasks-per-child", str(CeleryConfig.worker_max_tasks_per_child),
        ])
        
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        raise WorkerError(f"Failed to start worker: {e}", worker_name=hostname)


def main() -> None:
    """Main entry point for starting a Celery worker."""
    try:
        start_worker()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 