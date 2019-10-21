import re

# Spot a REDIS_URL with a DB number associated with it
REDIS_DB_URL_PATTERN = re.compile(r"redis\:\/\/.*\d{4,5}(\/\d{1,2})")
