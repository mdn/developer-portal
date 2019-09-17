from wagtail.images.formats import (
    Format,
    register_image_format,
    unregister_image_format,
)


unregister_image_format("fullwidth")
unregister_image_format("left")
unregister_image_format("right")

register_image_format(
    Format("left", "Left-aligned", "richtext-image format-left", "width-300")
)
register_image_format(
    Format("right", "Right-aligned", "richtext-image format-right", "width-300")
)
register_image_format(
    Format("center", "Center-aligned", "richtext-image format-center", "width-300")
)
