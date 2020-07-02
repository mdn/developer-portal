RESOURCE_COUNT_CHOICES = ((3, "3"), (6, "6"), (9, "9"))

DESCRIPTION_MAX_LENGTH = 400

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
LOCATION_QUERYSTRING_KEY = (
    "location"
)  #  NB this is used with the `country` field on page models
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


MOZILLA_SUPPORT_STRING = "Sponsored by Mozilla"
POSTS_PAGE_SEARCH_FIELDS = ["title", "description"]
EVENTS_PAGE_SEARCH_FIELDS = ["title", "description"]

POST = "Post"
EVENT = "Event"
PERSON = "Person"
CONTENT = None  # Deliberate
TOPIC = "Products & Technologies"

PAGE_TYPE_LOOKUP_FOR_LABEL = {
    "Article": POST,
    "Video": POST,
    "ExternalArticle": POST,
    "ExternalVideo": POST,
    "Event": EVENT,
    "ExternalEvent": EVENT,
    "Person": PERSON,
    "ExternalEvent": EVENT,
    "ContentPage": CONTENT,
    "Topic": TOPIC,
}
