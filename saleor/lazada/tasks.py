from __future__ import absolute_import, unicode_literals

from celery import task
from datetime import datetime

from .utils import util_sync_orders_status

@task()
def task_sync_lazada_orders():
    # Do another thing...
    util_sync_orders_status(None)