#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Load dev settings by default. To override this, set either:
    # - DJANGO_ENV to e.g. production, or;
    # - DJANGO_SETTINGS_MODULE to e.g. developerportal.settings.production (takes precedence).
    env = os.environ.setdefault("DJANGO_ENV", "dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"developerportal.settings.{env}")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
