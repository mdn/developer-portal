# Heavily based on
# https://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html
# #ensuring-a-task-is-only-executed-one-at-a-time

from contextlib import contextmanager

from django.core.cache import cache

from celery.five import monotonic
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


@contextmanager
def redis_lock(lock_id, oid):
    timeout_at = monotonic() + LOCK_EXPIRE - 3
    # cache.add returns False if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        if monotonic() < timeout_at and status:
            # Don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else.
            # Also don't release the lock if we didn't acquire it.
            cache.delete(lock_id)
