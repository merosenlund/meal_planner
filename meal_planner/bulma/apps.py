from django.apps import AppConfig
from django.forms.forms import BaseForm
from django.forms.utils import RenderableFormMixin


class BulmaConfig(AppConfig):
    name = "meal_planner.bulma"


# Monkey patching form rendering for Bulma
def as_bulma(self):
    return self.render(self.template_name_bulma)


setattr(RenderableFormMixin, "as_bulma", as_bulma)
BaseForm.template_name_bulma = "django/forms/bulma.html"
