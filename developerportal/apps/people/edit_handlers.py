from wagtail.admin.edit_handlers import FieldPanel


class FullNameFieldPanel(FieldPanel):
    def render_as_field(self):
        self.bound_field.label = 'Full name'
        return super().render_as_field()
