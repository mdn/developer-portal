from django.core.exceptions import ValidationError


def check_for_svg_file(obj):
    # A very light, naive check that the file at least has an .svg suffix.
    # This is NOT 100% safe/guaranteed, but given the users are trusted, this just a
    # small layer of protection against accidental oversights, because saving a bitmap
    # into this field by accident will cause `app_tags.render_svg()` to fail.

    if obj.file.name.split(".")[-1] != "svg":
        raise ValidationError(u"Only SVG images are allowed here.")
