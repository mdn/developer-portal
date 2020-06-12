RESOURCE_COUNT_CHOICES = ((3, "3"), (6, "6"), (9, "9"))

RICH_TEXT_FEATURES = (
    "bold",
    "blockquote",
    "code",
    "h2",
    "h3",
    "h4",
    "hr",
    "image",
    "italic",
    "link",
    "button-block",  # custom - see common/wagtail_hooks.py
    "ol",
    "ul",
)

RICH_TEXT_FEATURES_SIMPLE = ("bold", "italic", "code")

ROLE_CHOICES = (
    ("staff", "Staff"),
    ("tech-speaker", "Tech Speaker"),
    ("community", "Community"),
)

VIDEO_TYPE = (
    ("conference", "Conference"),
    ("tutorial", "Tutorial"),
    ("webinar", "Webinar"),
    ("presentation", "Presentation"),
    ("talk", "Talk"),
    ("demo", "Demo"),
    ("vlog", "Vlog"),
    ("live stream", "Live stream"),
    ("technical briefing", "Technical briefing"),
)


PAGINATION_QUERYSTRING_KEY = "page"
TOPIC_QUERYSTRING_KEY = "topic"
ROLE_QUERYSTRING_KEY = "role"
COUNTRY_QUERYSTRING_KEY = "country"
DATE_PARAMS_QUERYSTRING_KEY = "date"
SEARCH_QUERYSTRING_KEY = "search"

# This is a special value for the above that indicates "all previous events"
PAST_EVENTS_QUERYSTRING_VALUE = "past"
FUTURE_EVENTS_QUERYSTRING_VALUE = "future"
DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS = 6


# Note: see app_tags.pagination_additional_filter_params to add support
# for any new querystring keys you add here, else they will be ignored
ENVIRONMENT_PRODUCTION = "production"
ENVIRONMENT_STAGING = "staging"
ENVIRONMENT_DEVELOPMENT = "development"
