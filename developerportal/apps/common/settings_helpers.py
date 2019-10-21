"""Functionality to help with configuring settings.
DO NOT IMPORT django.conf.settings INTO THIS MODULE because it is imported
into settings.base
"""
import os

from developerportal.regex import REDIS_DB_URL_PATTERN


def _get_redis_url_for_cache(redis_cache_db_number):
    _redis_cache_url = os.environ.get("REDIS_URL", "redis://redis:6379")
    if REDIS_DB_URL_PATTERN.match(_redis_cache_url):
        raise RuntimeError(
            "REDIS_URL specifies a specific database, not just the server"
        )
    if _redis_cache_url[-1] == "/":
        _redis_cache_url = _redis_cache_url[:-1]
    return _redis_cache_url + f"/{redis_cache_db_number}"
