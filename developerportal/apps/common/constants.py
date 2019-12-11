COLOR_CHOICES = (
    ("pink-40", "Pink 40%"),
    ("red-40", "Red 40%"),
    ("orange-40", "Orange 40%"),
    ("yellow-40", "Yellow 40%"),
    ("green-40", "Green 40%"),
    ("blue-40", "Blue 40%"),
    ("violet-40", "Violet 40%"),
    ("purple-40", "Purple 40%"),
    ("pink-20", "Pink 20%"),
    ("red-20", "Red 20%"),
    ("orange-20", "Orange 20%"),
    ("yellow-20", "Yellow 20%"),
    ("green-20", "Green 20%"),
    ("blue-20", "Blue 20%"),
    ("violet-20", "Violet 20%"),
    ("purple-20", "Purple 20%"),
)

COLOR_VALUES = (
    ("pink-40", "#ff4aa2"),
    ("red-40", "#ff6a75"),
    ("orange-40", "#ff8a50"),
    ("yellow-40", "#ffbd4f"),
    ("green-40", "#54ffbd"),
    ("blue-40", "#0090ed"),
    ("violet-40", "#ab71ff"),
    ("purple-40", "#d74cf0"),
    ("pink-20", "#ff8ac5"),
    ("red-20", "#ff9aa2"),
    ("orange-20", "#ffb587"),
    ("yellow-20", "#ffea80"),
    ("green-20", "#b3ffe3"),
    ("blue-20", "#00ddff"),
    ("violet-20", "#cb9eff"),
    ("purple-20", "#f68fff"),
)

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
