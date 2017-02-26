"""Purge old data helper."""
from datetime import timedelta
import logging

import homeassistant.util.dt as dt_util

from . import models
from .util import session_scope

_LOGGER = logging.getLogger(__name__)


def purge_old_data(instance, purge_days):
    """Purge events and states older than purge_days ago."""
    purge_before = dt_util.utcnow() - timedelta(days=purge_days)

    states = models.States
    events = models.Events

    with session_scope(session=instance.get_session()) as session:
        deleted_rows = session.query(states) \
                              .filter((states.created < purge_before)) \
                              .delete(synchronize_session=False)
        _LOGGER.debug("Deleted %s states", deleted_rows)

        deleted_rows = session.query(events) \
                              .filter((events.created < purge_before)) \
                              .delete(synchronize_session=False)
        _LOGGER.debug("Deleted %s events", deleted_rows)

    # Execute sqlite vacuum command to free up space on disk
    if instance.engine.driver == 'sqlite':
        _LOGGER.info("Vacuuming SQLite to free space")
        instance.engine.execute("VACUUM")
