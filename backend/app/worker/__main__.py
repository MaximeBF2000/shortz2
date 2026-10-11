"""Worker process: python -m app.worker"""

import logging
import threading
import time

from app.config import get_settings
from app.db import create_tables
from app.worker import queue
from app.worker.tasks import TASKS

log = logging.getLogger("shortz.worker")
POLL_INTERVAL = 1.5


def work_forever(name: str) -> None:
    while True:
        job = queue.claim_next()
        if job is None:
            time.sleep(POLL_INTERVAL)
            continue
        log.info("[%s] %s %s", name, job.kind, job.payload)
        try:
            TASKS[job.kind](**job.payload)
            queue.finish(job.id)
            log.info("[%s] done %s", name, job.kind)
        except Exception as error:  # the task already recorded a user-facing error
            queue.finish(job.id, error=str(error))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    create_tables()
    requeued = queue.requeue_interrupted()
    if requeued:
        log.info("Requeued %d interrupted job(s)", requeued)

    count = get_settings().worker_concurrency
    log.info("Worker started with %d thread(s)", count)
    threads = [threading.Thread(target=work_forever, args=(f"w{i}",), daemon=True) for i in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
