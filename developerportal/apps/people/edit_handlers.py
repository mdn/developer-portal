from wagtail.admin.edit_handlers import FieldPanel


class CustomLabelFieldPanel(FieldPanel):
    def __init__(self, *args, label="Full name", **kwargs):
        super().__init__(*args, **kwargs)
        self._custom_label = label

    def render_as_field(self):
        if hasattr(self, "_custom_label"):
            self.bound_field.label = self._custom_label
        return super().render_as_field()
